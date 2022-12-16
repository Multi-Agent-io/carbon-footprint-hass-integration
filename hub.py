from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from .carbon_asset_calculator import calculate_compensation_amt_tokens_async

_LOGGER = logging.getLogger(__name__)


class Hub:
    def __init__(self, hass: HomeAssistant, email_address: str, password: str) -> None:
        """Init hub."""
        self._hass = hass
        self._name = "Solarweb"
        self._id = self._name.lower()
        self.online = True

    @property
    def hub_id(self) -> str:
        """ID for hub."""
        return self._id

    async def get_tokens(self, energy):
        geo = self._hass.states.get("zone.home")
        geo_str = f'{geo.attributes["latitude"]}, {geo.attributes["longitude"]}'
        return await calculate_compensation_amt_tokens_async(geo=geo_str, kwh=energy)
