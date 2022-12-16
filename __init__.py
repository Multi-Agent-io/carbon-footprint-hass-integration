"""Solarweb integration."""
from __future__ import annotations

import asyncio
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from carbon_offset import burn_carbon_asset_async, calculate_compensation_amt_tokens_async

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    _LOGGER.warning("Start setup in init")
    _LOGGER.warning(f"E-mail address: {entry.data['email_address']}")
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub.Hub(
    #     hass, entry.data["email_address"], entry.data["password"]
    # )

    try:
        geo = hass.states.get("zone.home")
        geo_str = f'{geo.attributes["latitude"]}, {geo.attributes["longitude"]}'
        to_burn = float(hass.data[DOMAIN][entry.entry_id].boards[0]._to_compensate)
        hass.data[DOMAIN][entry.entry_id].boards[0]._tokens_to_burn = round(
            await calculate_compensation_amt_tokens_async(to_burn, geo_str) / 10**9, 2
        )
        _LOGGER.warning(f"Tokens calculated: {hass.data[DOMAIN][entry.entry_id].boards[0]._tokens_to_burn}")
    except Exception as e:
        _LOGGER.error(f"Exception in getting tokens: {e}")
        await asyncio.sleep(15)
        geo = hass.states.get("zone.home")
        geo_str = f'{geo.attributes["latitude"]}, {geo.attributes["longitude"]}'
        to_burn = float(hass.data[DOMAIN][entry.entry_id].boards[0]._to_compensate)
        hass.data[DOMAIN][entry.entry_id].boards[0]._tokens_to_burn = round(
            await calculate_compensation_amt_tokens_async(to_burn, geo_str) / 10**9, 2
        )
        _LOGGER.warning(f"Tokens calculated: {hass.data[DOMAIN][entry.entry_id].boards[0]._tokens_to_burn}")

    async def burn(energy, seed, geo_str):
        _LOGGER.warning(f"Start burning {energy} kWh")
        try:
            tokens_to_burn: float = await calculate_compensation_amt_tokens_async(geo=geo_str, kwh=energy)
            is_success, tr_hash, link = await burn_carbon_asset_async(seed=seed, tokens_to_burn=tokens_to_burn)
            _LOGGER.warning(f"Trying to burn {energy}, hash: {tr_hash}")
            _LOGGER.warning(f"Is success {is_success}")
        except TimeoutError:
            time.sleep(15)
            tokens_to_burn: float = await calculate_compensation_amt_tokens_async(geo=geo_str, kwh=energy)
            is_success, tr_hash, link = await burn_carbon_asset_async(seed=seed, tokens_to_burn=tokens_to_burn)
            _LOGGER.warning(f"Trying to burn {energy}, hash: {tr_hash}")
            _LOGGER.warning(f"Is success {is_success}")
        except Exception as e:
            _LOGGER.error(f"Exception in burning: {e}")
            is_success = False
            tr_hash = ""
            link = ""
        return (is_success, tr_hash, link)

    async def burn_footprint(call):
        """Handle the service call."""
        geo = hass.states.get("zone.home")
        geo_str = f'{geo.attributes["latitude"]}, {geo.attributes["longitude"]}'
        to_burn = float(hass.data[DOMAIN][entry.entry_id].boards[0]._to_compensate)
        seed = entry.data["seed_secret"]
        is_burned, tr_hash, link = await burn(to_burn, seed, geo_str)
        if not is_burned:
            title = "CO2 Footprint Compensation"
            text = f"{to_burn} kWh wasn't compensated, not enough tokens"
            await hass.services.async_call(
                domain="notify", service="persistent_notification", service_data={"title": title, "message": text}
            )
            return
        # TODO
        hass.data[DOMAIN][entry.entry_id].boards[0]._compensated += round(to_burn, 2)
        hass.data[DOMAIN][entry.entry_id].boards[0]._last_hash = tr_hash
        hass.data[DOMAIN][entry.entry_id].boards[0]._link = link
        hass.data[DOMAIN][entry.entry_id].boards[0]._to_compensate -= round(to_burn, 2)
        hass.data[DOMAIN][entry.entry_id].boards[0]._tokens_to_burn = round(
            await calculate_compensation_amt_tokens_async(
                float(hass.data[DOMAIN][entry.entry_id].boards[0]._to_compensate), geo_str
            )
            / 10**9,
            2,
        )

        def write_to_file(state, file):
            with open(f"{file}.txt", "w") as f:
                f.write(str(state))

        write_to_file(hass.data[DOMAIN][entry.entry_id].boards[0]._compensated, "_compensated")
        write_to_file(hass.data[DOMAIN][entry.entry_id].boards[0]._last_hash, "_last_hash")
        write_to_file(hass.data[DOMAIN][entry.entry_id].boards[0]._link, "_link")
        await hass.data[DOMAIN][entry.entry_id].boards[0].publish_updates()
        title = "CO2 Footprint Compensation"
        text = f"{to_burn} kWh was compensated"
        await hass.services.async_call(
            domain="notify", service="persistent_notification", service_data={"title": title, "message": text}
        )

    hass.services.async_register(DOMAIN, "burn_footprint", burn_footprint)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
