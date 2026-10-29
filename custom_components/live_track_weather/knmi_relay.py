"""The KNMI radar relay in Home Assistant (Weather SSOT item 278, contract D13 "Relays").

Exists only when the user has entered their own KNMI WMS key (options). It reads KNMI's capabilities every
5 minutes for the newest frame, and serves that frame's tiles at KNMI_TILE_PATH. A frame's picture is asked for
the first time a tile of it is wanted, once, however many tiles and browsers ask at the same moment; nobody
looking costs only the capabilities. The tiles of the newest two frames are kept, so the card can swap frames
without a blank.

The tile view requires authentication: the card asks Home Assistant to sign each tile's path
(`auth/sign_path`), so the relay, which spends the user's key, is not open to anyone who can reach Home
Assistant (D13). Nothing here raises into Home Assistant: a failure drops the relay's `time`, and the card
falls back to its other sources.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from datetime import timedelta
from typing import Any

import aiohttp
from aiohttp import web

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.http import KEY_HASS, HomeAssistantView
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import knmi
from .const import (DOMAIN, KNMI_ATTRIBUTION, KNMI_BUDGET_PER_H, KNMI_DATASET, KNMI_JITTER_S, KNMI_LAYER,
                    KNMI_POLL_S, KNMI_RELAY_ID, KNMI_RESERVE, KNMI_RETRY_S, KNMI_STYLE, KNMI_TILE_PATH, KNMI_WMS,
                    REQUEST_TIMEOUT, USER_AGENT)

_LOGGER = logging.getLogger(__name__)
_KEEP_FRAMES = 2


def _int(v: str | None) -> int | None:
    try:
        return int(v) if v is not None else None
    except ValueError:
        return None


async def _ask(session: aiohttp.ClientSession, key: str, params: dict[str, str]
               ) -> tuple[int, bytes | None, str, dict[str, str]]:
    """One request to KNMI's WMS. (status, body, content type, headers); status 0 when it never answered."""
    try:
        async with session.get(KNMI_WMS, params={"DATASET": KNMI_DATASET, **params},
                               headers={"Authorization": key, "User-Agent": USER_AGENT},
                               timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as r:
            return r.status, await r.read(), r.headers.get("Content-Type", ""), dict(r.headers)
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.debug("KNMI WMS failed: %s", type(err).__name__)
        return 0, None, "", {}


async def async_check_key(hass: HomeAssistant, key: str) -> str | None:
    """For the options form: None when KNMI accepts the key for its radar WMS, else the error's key."""
    status, body, _, _ = await _ask(async_get_clientsession(hass), key, knmi.capabilities_params())
    if status in (401, 403):
        return "knmi_key_rejected"
    if status != 200 or knmi.newest_frame(body, KNMI_LAYER) is None:
        return "knmi_cannot_connect"
    return None


class KnmiRelay(DataUpdateCoordinator[dict[str, Any]]):
    """The newest frame from KNMI's capabilities, and the tiles of the frames asked for."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, key: str) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_knmi",
                         update_interval=timedelta(seconds=KNMI_POLL_S + random.randint(0, KNMI_JITTER_S)))
        self._key = key
        self._session = async_get_clientsession(hass)
        self.budget = knmi.Budget(KNMI_BUDGET_PER_H, KNMI_RESERVE)
        self._tiles: dict[str, dict[tuple[int, int, int], bytes]] = {}
        self._building: dict[str, asyncio.Future] = {}
        self._failed: dict[str, float] = {}
        self._warned: set[str] = set()

    def _warn_once(self, key: str, msg: str, *args: Any) -> None:
        if key not in self._warned:
            self._warned.add(key)
            _LOGGER.warning(msg, *args)

    async def _request(self, params: dict[str, str]) -> tuple[int, bytes | None, str]:
        if not self.budget.allowed():
            return 0, None, ""
        self.budget.spend()
        status, body, ctype, headers = await _ask(self._session, self._key, params)
        self.budget.server(status, _int(headers.get("X-Ratelimit-Remaining")), _int(headers.get("X-Ratelimit-Reset")))
        if status in (401, 403):
            self._warn_once("key", "KNMI refused the key (HTTP %s): KNMI radar is off until the key is changed", status)
        elif status == 429:
            self._warn_once("429", "KNMI says this key is over its hourly limit; KNMI radar pauses until it resets")
        return status, body, ctype

    async def _async_update_data(self) -> dict[str, Any]:
        old = self.data or {}
        status, body, _ = await self._request(knmi.capabilities_params())
        when = knmi.newest_frame(body, KNMI_LAYER) if status == 200 else None
        if when is None:
            # Keep the last frame: it ages out on the card (30 min) if KNMI stays away.
            return old
        return {"time": when, "frame": knmi.frame_key(when)}

    def usable(self) -> bool:
        d = self.data or {}
        frame = d.get("frame")
        if not frame or not self.budget.allowed():
            return False
        return time.monotonic() - self._failed.get(frame, -1e18) >= KNMI_RETRY_S

    def relay(self) -> dict[str, Any] | None:
        d = self.data or {}
        return knmi.relay_attribute(d.get("frame"), d.get("time"), self.usable(), KNMI_TILE_PATH,
                                    KNMI_ATTRIBUTION, KNMI_RELAY_ID)

    async def tile(self, frame: str, z: int, x: int, y: int) -> bytes | None:
        """A tile's PNG, or None (the view answers 404)."""
        if frame in self._tiles:
            return self._tiles[frame].get((z, x, y))
        d = self.data or {}
        if frame != d.get("frame") or (x, y) not in knmi.tiles_at(z):
            return None
        # One task per frame: every tile asked for meanwhile waits on it, and a browser that goes away
        # (its request cancelled) does not cancel the picture for the others.
        task = self._building.get(frame)
        if task is None:
            task = self.hass.async_create_background_task(self._build_safe(frame, d["time"]),
                                                          f"{DOMAIN} knmi frame {frame}")
            self._building[frame] = task
            task.add_done_callback(lambda _t, f=frame: self._building.pop(f, None))
        tiles = await asyncio.shield(task)
        return tiles.get((z, x, y)) if tiles else None

    async def _build_safe(self, frame: str, when: str) -> dict[tuple[int, int, int], bytes] | None:
        try:
            return await self._build(frame, when)
        except Exception as err:  # noqa: BLE001 - never into the view
            _LOGGER.debug("KNMI frame %s: %s", frame, err)
            self._failed[frame] = time.monotonic()
            return None

    async def _build(self, frame: str, when: str) -> dict[tuple[int, int, int], bytes] | None:
        if time.monotonic() - self._failed.get(frame, -1e18) < KNMI_RETRY_S:
            return None
        status, body, ctype = await self._request(knmi.picture_params(KNMI_LAYER, KNMI_STYLE, when))
        tiles = None
        if status == 200 and body and ctype.startswith("image/png"):
            try:
                tiles = await self.hass.async_add_executor_job(knmi.cut, body)
            except (ValueError, OSError) as err:
                _LOGGER.debug("KNMI frame %s: picture unusable: %s", frame, err)
        if tiles is None:
            self._failed[frame] = time.monotonic()
            self.async_update_listeners()  # the sensor drops `time`: the card falls back
            return None
        self._tiles[frame] = tiles
        for old in sorted(self._tiles)[:-_KEEP_FRAMES]:
            self._tiles.pop(old, None)
        for old in [f for f in self._failed if f < frame]:
            self._failed.pop(old, None)
        return tiles


class KnmiTileView(HomeAssistantView):
    """`KNMI_TILE_PATH/<frame>/<z>/<x>/<y>.png`. Authenticated: the card signs each path (D13)."""

    url = KNMI_TILE_PATH + "/{frame}/{z}/{x}/{y}.png"
    name = f"api:{DOMAIN}:knmi_tile"
    requires_auth = True

    async def get(self, request: web.Request, frame: str, z: str, x: str, y: str) -> web.Response:
        hass = request.app[KEY_HASS]
        relay: KnmiRelay | None = hass.data.get(DOMAIN, {}).get("knmi_relay")
        if relay is None or not knmi.FRAME_RE.match(frame) or not (z.isdigit() and x.isdigit() and y.isdigit()):
            return web.Response(status=404)
        body = await relay.tile(frame, int(z), int(x), int(y))
        if body is None:
            return web.Response(status=404)
        return web.Response(body=body, content_type="image/png",
                            headers={"Cache-Control": "private, max-age=3600"})
