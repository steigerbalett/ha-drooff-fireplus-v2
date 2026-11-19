"""Repairs (notices) for drooff_fireplus_v2."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.repairs import ConfirmRepairFlow

if TYPE_CHECKING:
    from homeassistant.components.repairs import RepairsFlow
    from homeassistant.core import HomeAssistant


async def async_create_fix_flow(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    issue_id: str,  # noqa: ARG001 Unused function argument: `issue_id`
    data: dict[str, Any] | None,  # noqa: ARG001 Unused function argument: `data`
) -> RepairsFlow:
    """Let the notice about new software of the fire+ be confirmed, which removes it."""
    return ConfirmRepairFlow()
