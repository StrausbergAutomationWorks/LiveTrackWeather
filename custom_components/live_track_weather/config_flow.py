"""Config flow: nothing to ask. One entry covers the whole US.

There is no location: the map shows every US alert and the card decides what
is on screen. The options are the poll interval and, optionally, the user's own
KNMI key for radar over the Netherlands (Weather SSOT item 278): checked with
KNMI once when entered; left empty, the map uses RainViewer there.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .const import (
    CONF_KNMI_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


class LiveTrackWeatherFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="Live Track Weather", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return LiveTrackWeatherOptions()


class LiveTrackWeatherOptions(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        current = dict(self.config_entry.options)
        if user_input is not None:
            key = (user_input.get(CONF_KNMI_KEY) or "").strip()
            if key and key != (current.get(CONF_KNMI_KEY) or ""):
                from .knmi_relay import async_check_key  # only when a new key is entered
                err = await async_check_key(self.hass, key)
                if err:
                    errors[CONF_KNMI_KEY] = err
            if not errors:
                data = {CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]}
                if key:
                    data[CONF_KNMI_KEY] = key
                return self.async_create_entry(data=data)
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            vol.Optional(CONF_KNMI_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        })
        suggested = {CONF_KNMI_KEY: current.get(CONF_KNMI_KEY, "")}
        if user_input is not None:
            suggested = {CONF_KNMI_KEY: user_input.get(CONF_KNMI_KEY, "")}
        return self.async_show_form(step_id="init", errors=errors,
                                    data_schema=self.add_suggested_values_to_schema(schema, suggested))
