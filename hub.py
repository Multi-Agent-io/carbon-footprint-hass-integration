from __future__ import annotations

import asyncio
import functools
import imaplib
import logging
import random
import re
from datetime import timedelta

import pandas as pd
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .carbon_asset_calculator import calculate_compensation_amt_tokens

_LOGGER = logging.getLogger(__name__)


def to_thread(func: tp.Callable) -> tp.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


class Hub:
    def __init__(self, hass: HomeAssistant, email_address: str, password: str) -> None:
        """Init hub."""
        self._hass = hass
        self._name = "Solarweb"
        self._id = self._name.lower()
        self.boards = [
            Board(hass, f"{self._id}_energy", f"{self._name}_energy", email_address, password),
        ]
        self.online = True

    @property
    def hub_id(self) -> str:
        """ID for hub."""
        return self._id

    async def test_connection(self) -> bool:
        await asyncio.sleep(1)
        return True


class Board:
    def __init__(
        self,
        hass,
        board_id: str,
        name: str,
        email_address: str,
        password: str,
        imap_server: str = "imap.gmail.com",
        sender_address: str = "noreply@solarweb.com",
    ) -> None:
        """Init."""
        _LOGGER.warning("Start setup board")
        self._id = board_id
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        self.email_address: str = email_address
        self.password: str = password
        self.imap_server: str = imap_server
        self.sender_address: str = sender_address
        self._production = 0
        self._consumption = 0
        self._own_consumption = 0
        self._to_grid_today = 0
        self._from_grid_today = 0

        self._last_hash = "0"
        self._link = "0"

        def read_from_file(state):
            try:
                with open(f"{state}.txt") as f:
                    value = f.read()
            except Exception:
                value = 0
            return value

        self._old_id = read_from_file("_old_id")
        self._production_total = round(float(read_from_file("_production_total")), 2)
        self._consumption_total = round(float(read_from_file("_consumption_total")), 2)
        self._own_consumption_total = round(float(read_from_file("_own_consumption_total")), 2)
        self._to_grid_total = round(float(read_from_file("_to_grid_total")), 2)
        self._from_grid_total = round(float(read_from_file("_from_grid_total")), 2)
        self._compensated = round(float(read_from_file("_compensated")), 2)
        self._to_compensate = round(
            float(self._consumption_total) - float(self._production_total) - float(self._compensated), 2
        )
        self._hass = hass
        self._tokens_to_burn = 0
        # check new emails once a minute
        self._unsub = async_track_time_interval(hass, self.check_new_mails, timedelta(minutes=30))

    @to_thread
    def get_tokens(self, energy, hass):
        geo = hass.states.get("zone.home")
        geo_str = f'{geo.attributes["latitude"]}, {geo.attributes["longitude"]}'
        tokens_to_burn = calculate_compensation_amt_tokens(geo=geo_str, kwh=energy)
        self._tokens_to_burn = tokens_to_burn
        return tokens_to_burn

    @to_thread
    def parse_url(self, url):
        data = pd.read_csv(url)
        info = self.parse_report(data)
        return info

    def parse_report(self, data):
        info = data.iloc[1][1:]
        info = pd.to_numeric(info, errors="coerce")
        info = info.apply(lambda x: x / 1000)
        info = info.apply(lambda x: round(x, 2))

        return info

    async def check_new_mails(self, event):
        try:
            imap = imaplib.IMAP4_SSL(self.imap_server)
            imap.login(self.email_address, self.password)
            imap.select("INBOX")
            messages = imap.uid("search", "ALL", None, f'(FROM "{self.sender_address}")')
            try:
                last_id = messages[1][0].decode().split()[-1]
                with open("_old_id.txt", "w") as f:
                    # uncomment +1 to test updating
                    f.write(str(int(last_id)))  # +1))
                if self._old_id == last_id:
                    return
                else:
                    self._old_id = last_id
            except Exception as e:
                _LOGGER.error(f"Exception: no such letters: {e}")
                return
            type, data = imap.uid("fetch", str(last_id), "RFC822")
            # TODO correct regex
            link_pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
            text = data[0][1].decode("UTF-8")
            text = text.split("href='")
            url = text[1].split("'>Download")
            url = url[0]
            url.replace("\r\n", "")
            _LOGGER.error(f"Link: {url}")
            try:
                [
                    self._production,
                    self._consumption,
                    self._own_consumption,
                    self._to_grid_today,
                    self._from_grid_today,
                ] = await self.parse_url(url)
                _LOGGER.warning(f"New data!")
            except Exception as e:
                _LOGGER.error(f"Error in parsing: {e}")

            def write_to_file(state, file):
                with open(f"{file}.txt", "w") as f:
                    f.write(str(state))

            self._production_total = float(self._production_total) + float(self._production)
            self._consumption_total = float(self._consumption_total) + float(self._consumption)
            self._own_consumption_total = float(self._own_consumption_total) + float(self._own_consumption)
            self._to_grid_total = float(self._to_grid_total) + float(self._to_grid_today)
            self._from_grid_total = float(self._from_grid_total) + float(self._from_grid_today)
            self._to_compensate = round(
                float(self._consumption_total) - float(self._production_total) - float(self._compensated), 2
            )
            geo = self._hass.states.get("zone.home")
            geo_str = f'{geo.attributes["latitude"]}, {geo.attributes["longitude"]}'
            self._tokens_to_burn = round(await get_tokens_to_burn_thread(self._to_compensate, geo_str) / 10**9, 2)
            _LOGGER.warning(f"Tokens calculated: {self._tokens_to_burn}")

            write_to_file(self._production_total, "_production_total")
            write_to_file(self._consumption_total, "_consumption_total")
            write_to_file(self._own_consumption_total, "_own_consumption_total")
            write_to_file(self._to_grid_total, "_to_grid_total")
            write_to_file(self._from_grid_total, "_from_grid_total")

            await self.publish_updates()
            _LOGGER.warning(f"New energy states")

        except Exception as e:
            _LOGGER.error(f"Exception in check_new_mails: {e}")

    @property
    def board_id(self) -> str:
        """Return ID for board."""
        return self._id

    async def delayed_update(self) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        await asyncio.sleep(random.randint(1, 10))
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when board changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        return True

    @property
    def battery_level(self) -> int:
        """Battery level as a percentage."""
        return self._energy
