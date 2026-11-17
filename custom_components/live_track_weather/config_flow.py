"""Config flow: nothing to ask. One entry covers the whole US.

The map shows every US alert and the card decides what is on screen. The options are the poll interval;
optionally, the user's own KNMI key for radar over the Netherlands (Weather SSOT item 278), checked with
KNMI once when entered (left empty, the map uses RainViewer there); the places watched for alerts
(Weather SSOT item 334): home by default, people, device trackers and zones as the user adds them, and
the CAP severity from which an alert turns a place's entity on; airport stations only for the measured
weather (item 350); and, for fire and smoke at the places (item 351), the user's own FIRMS and AirNow keys
(each checked once when entered; left empty, that part is off), the fire distance and the smoke AQI.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (BooleanSelector, EntitySelector, EntitySelectorConfig,
                                            NumberSelector, NumberSelectorConfig, NumberSelectorMode,
                                            SelectSelector, SelectSelectorConfig, SelectSelectorMode,
                                            TextSelector, TextSelectorConfig, TextSelectorType)

from .const import (
    CONF_AIRNOW_KEY,
    CONF_ALERT_THRESHOLD,
    CONF_FIRE_KM,
    CONF_FIRMS_KEY,
    CONF_KNMI_KEY,
    CONF_OBSERVE_AIRPORTS_ONLY,
    CONF_SCAN_INTERVAL,
    CONF_SMOKE_AQI,
    CONF_WATCH_ENTITIES,
    CONF_WATCH_HOME,
    DEFAULT_OBSERVE_AIRPORTS_ONLY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_WATCH_HOME,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    WATCH_DOMAINS,
)
from .hazards import FIRE_KM_DEFAULT, SMOKE_AQI_DEFAULT
from .places import DEFAULT_THRESHOLD, THRESHOLDS

_KEYS = (CONF_KNMI_KEY, CONF_FIRMS_KEY, CONF_AIRNOW_KEY)


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
            keys = {k: (user_input.get(k) or "").strip() for k in _KEYS}
            # Each key is checked only when it is new; one request to its own service.
            if keys[CONF_KNMI_KEY] and keys[CONF_KNMI_KEY] != (current.get(CONF_KNMI_KEY) or ""):
                from .knmi_relay import async_check_key
                if err := await async_check_key(self.hass, keys[CONF_KNMI_KEY]):
                    errors[CONF_KNMI_KEY] = err
            if keys[CONF_FIRMS_KEY] and keys[CONF_FIRMS_KEY] != (current.get(CONF_FIRMS_KEY) or ""):
                from .hazard_keys import async_check_firms
                if err := await async_check_firms(self.hass, keys[CONF_FIRMS_KEY]):
                    errors[CONF_FIRMS_KEY] = err
            if keys[CONF_AIRNOW_KEY] and keys[CONF_AIRNOW_KEY] != (current.get(CONF_AIRNOW_KEY) or ""):
                from .hazard_keys import async_check_airnow
                if err := await async_check_airnow(self.hass, keys[CONF_AIRNOW_KEY]):
                    errors[CONF_AIRNOW_KEY] = err
            if not errors:
                data = {
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    CONF_WATCH_HOME: bool(user_input.get(CONF_WATCH_HOME, DEFAULT_WATCH_HOME)),
                    CONF_WATCH_ENTITIES: list(user_input.get(CONF_WATCH_ENTITIES) or []),
                    CONF_ALERT_THRESHOLD: user_input.get(CONF_ALERT_THRESHOLD, DEFAULT_THRESHOLD),
                    CONF_OBSERVE_AIRPORTS_ONLY: bool(user_input.get(CONF_OBSERVE_AIRPORTS_ONLY,
                                                                    DEFAULT_OBSERVE_AIRPORTS_ONLY)),
                    CONF_FIRE_KM: int(user_input.get(CONF_FIRE_KM, FIRE_KM_DEFAULT)),
                    CONF_SMOKE_AQI: int(user_input.get(CONF_SMOKE_AQI, SMOKE_AQI_DEFAULT)),
                }
                for k, v in keys.items():
                    if v:
                        data[k] = v
                return self.async_create_entry(data=data)
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            vol.Required(CONF_WATCH_HOME, default=current.get(CONF_WATCH_HOME, DEFAULT_WATCH_HOME)): BooleanSelector(),
            vol.Optional(CONF_WATCH_ENTITIES, default=current.get(CONF_WATCH_ENTITIES, [])): EntitySelector(
                EntitySelectorConfig(domain=list(WATCH_DOMAINS), multiple=True)),
            vol.Required(CONF_ALERT_THRESHOLD, default=current.get(CONF_ALERT_THRESHOLD, DEFAULT_THRESHOLD)):
                SelectSelector(SelectSelectorConfig(options=list(THRESHOLDS), mode=SelectSelectorMode.DROPDOWN,
                                                    translation_key=CONF_ALERT_THRESHOLD)),
            vol.Required(CONF_OBSERVE_AIRPORTS_ONLY, default=current.get(CONF_OBSERVE_AIRPORTS_ONLY,
                                                                         DEFAULT_OBSERVE_AIRPORTS_ONLY)):
                BooleanSelector(),
            vol.Optional(CONF_FIRMS_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(CONF_FIRE_KM, default=current.get(CONF_FIRE_KM, FIRE_KM_DEFAULT)): NumberSelector(
                NumberSelectorConfig(min=5, max=150, step=1, unit_of_measurement="km", mode=NumberSelectorMode.BOX)),
            vol.Optional(CONF_AIRNOW_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(CONF_SMOKE_AQI, default=current.get(CONF_SMOKE_AQI, SMOKE_AQI_DEFAULT)): NumberSelector(
                NumberSelectorConfig(min=25, max=300, step=1, mode=NumberSelectorMode.BOX)),
            vol.Optional(CONF_KNMI_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        })
        source = user_input if user_input is not None else current
        suggested = {k: source.get(k, "") for k in _KEYS}
        return self.async_show_form(step_id="init", errors=errors,
                                    data_schema=self.add_suggested_values_to_schema(schema, suggested))
