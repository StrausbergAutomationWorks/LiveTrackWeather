"""Polling coordinator: one /alerts/active request per poll, for the whole US.

No location is configured or used: the map shows every US alert, and the card
decides what is on screen. This integration never reads another integration's
config entries.
"""

from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .alerts import live_list
from .const import (
    ALERTS_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_TRANSIENT_FAILURES,
    REQUEST_TIMEOUT,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class WeatherCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches the active alerts and turns them into the live list."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry,
                 colours: dict[str, dict[str, Any]]) -> None:
        opts = {**entry.data, **entry.options}
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=int(opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
        )
        self._session = async_get_clientsession(hass)
        self._colours = colours
        self._failures = 0
        self._last_good: dict[str, Any] | None = None
        self._unknown_logged: set[str] = set()

    async def _fetch(self) -> bytes | None:
        try:
            async with self._session.get(
                ALERTS_URL,
                headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    _LOGGER.debug("NWS alerts answered HTTP %s", resp.status)
                    return None
                return await resp.read()
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("NWS alerts fetch failed: %s", type(err).__name__)
            return None

    def _parse(self, raw: bytes) -> dict[str, Any] | None:
        try:
            doc = json.loads(raw)
        except ValueError:
            return None
        if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
            return None
        return live_list(doc, self._colours)

    async def _async_update_data(self) -> dict[str, Any]:
        raw = await self._fetch()
        # About 1.4 MB of JSON: parse it off the event loop.
        result = await self.hass.async_add_executor_job(self._parse, raw) if raw else None
        if result is None:
            self._failures += 1
            if self._failures <= MAX_TRANSIENT_FAILURES and self._last_good is not None:
                return self._last_good
            raise UpdateFailed(f"NWS alerts unavailable ({self._failures} consecutive failures)")
        self._failures = 0
        new_unknown = set(result["unknown_events"]) - self._unknown_logged
        if new_unknown:
            _LOGGER.info("Events not in the NWS colour table, drawn grey: %s",
                         ", ".join(sorted(new_unknown)))
            self._unknown_logged |= new_unknown
        self._last_good = result
        return result
