"""Polling coordinator for the SPC Day 1 categorical outlook (contract D16).

SPC answers `max-age=120` with an ETag; Day 1 is reissued five times a day. Polled every
SPC_POLL_S with If-None-Match. A failed request never clears the map before the outlook's own
`EXPIRE`: the last good parse is re-read against the clock each poll, so an outlook whose day
is over leaves the map even while SPC cannot be reached. This coordinator never raises.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import outlook as ol
from .const import DOMAIN, REQUEST_TIMEOUT, SPC_DAY1_URL, SPC_POLL_S, USER_AGENT

_LOGGER = logging.getLogger(__name__)


def _parse_json(raw: bytes) -> Any:
    try:
        return json.loads(raw)
    except ValueError:
        return None


class OutlookCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_outlook",
                         update_interval=timedelta(seconds=SPC_POLL_S))
        self._session = async_get_clientsession(hass)
        self._etag: str | None = None
        self._doc: Any = None

    async def _async_update_data(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        headers = {"User-Agent": USER_AGENT}
        if self._etag:
            headers["If-None-Match"] = self._etag
        try:
            async with self._session.get(SPC_DAY1_URL, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as r:
                if r.status == 200:
                    body = await r.read()
                    doc = await self.hass.async_add_executor_job(_parse_json, body)
                    if isinstance(doc, dict) and isinstance(doc.get("features"), list):
                        self._doc = doc
                        self._etag = r.headers.get("ETag")
                elif r.status != 304:
                    _LOGGER.debug("SPC Day 1 outlook answered %s", r.status)
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("SPC Day 1 outlook failed: %s", type(err).__name__)
        # No per-poll timestamp: the state changes only when the outlook does, so the card
        # redraws (and restacks the publishers above it) only then.
        return ol.parse(self._doc, now) if self._doc is not None else ol.empty()
