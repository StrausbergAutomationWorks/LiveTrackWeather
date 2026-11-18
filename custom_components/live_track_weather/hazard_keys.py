"""Checking a FIRMS MAP_KEY and an AirNow API key when the user enters one in the options (Weather SSOT item 351).

MEASURED 2026-11-17 (bin\\ltw351_badkeys.txt): FIRMS's key status answers a good key 200 with JSON holding
"transaction_limit", a wrong one 403 ("MAP_KEY is invalid or your have exceeded your transaction/time limit");
AirNow's ziplatlong answers a wrong key 401 {"WebServiceError":[{"Message":"Invalid API key"}]}, a good one 200 (a
list, or an error object saying there are no observations nearby). One request each, only when a new key is entered.
"""

from __future__ import annotations

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import geonames
from .const import AIRNOW_URL, FIRMS_STATUS_URL, REQUEST_TIMEOUT, USER_AGENT


async def async_check_firms(hass: HomeAssistant, key: str) -> str | None:
    """None when FIRMS takes the key, else an error key for strings.json."""
    try:
        async with async_get_clientsession(hass).get(
                FIRMS_STATUS_URL, params={"MAP_KEY": key}, headers={"User-Agent": USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            if resp.status == 403:
                return "firms_key_rejected"
            if resp.status != 200:
                return "firms_cannot_connect"
            body = await resp.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError):
        return "firms_cannot_connect"
    return None if isinstance(body, dict) and "transaction_limit" in body else "firms_key_rejected"


async def async_check_airnow(hass: HomeAssistant, key: str) -> str | None:
    """None when AirNow takes the key (asked at Home Assistant's home, 4 decimals), else an error key."""
    try:
        async with async_get_clientsession(hass).get(
                AIRNOW_URL, params={"format": "application/json", "latitude": f"{hass.config.latitude:.4f}",
                                    "longitude": f"{hass.config.longitude:.4f}", "API_KEY": key},
                headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            if resp.status in (401, 403):
                return "airnow_key_rejected"
            if resp.status != 200:
                return "airnow_cannot_connect"
    except (aiohttp.ClientError, TimeoutError):
        return "airnow_cannot_connect"
    return None


async def async_check_geonames(hass: HomeAssistant, username: str) -> str | None:
    """None when GeoNames takes the username (item 352 step 4b): one gtopo30JSON call at Home Assistant's home, 4
    decimals, 0.1 credit; else an error key (geonames.check_error). MEASURED 2026-11-18: an unconfirmed account
    answers 401 "user account has not been confirmed"; the other answers are read from GeoNames' pages."""
    try:
        async with async_get_clientsession(hass).get(
                geonames.CHECK_URL, params=geonames.params(username, hass.config.latitude, hass.config.longitude),
                headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            status = resp.status
            body = await resp.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError):
        return "geonames_cannot_connect"
    return geonames.check_error(status, body)
