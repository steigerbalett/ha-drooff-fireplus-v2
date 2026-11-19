"""Button platform for drooff_fireplus_v2."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .api import FireplusApiClientError, FireplusApiClientNotStandbyError
from .const import DOMAIN
from .entity import FireplusEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import FireplusConfigEntry

# The fire+ accepts only one write at a time
PARALLEL_UPDATES = 1

SHUTDOWN = ButtonEntityDescription(
    key="shutdown",
    translation_key="shutdown",
    entity_category=EntityCategory.CONFIG,
    # rarely useful: the fire+ only starts again when it is switched off and on
    entity_registry_enabled_default=False,
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: FireplusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities([FireplusShutdownButton(entry.runtime_data.coordinator, SHUTDOWN)])


class FireplusShutdownButton(FireplusEntity, ButtonEntity):
    """Shuts down the fire+ like the button "fire+ ausschalten" of its web app."""

    async def async_press(self) -> None:
        """Shut down the fire+, only in standby."""
        try:
            await self.coordinator.config_entry.runtime_data.client.async_shut_down()
        except FireplusApiClientNotStandbyError as exception:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="shutdown_not_standby",
            ) from exception
        except FireplusApiClientError as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="shutdown_failed",
                translation_placeholders={"error": str(exception)},
            ) from exception
        self.coordinator.async_shut_down()
