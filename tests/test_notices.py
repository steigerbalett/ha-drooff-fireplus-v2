"""Tests for shutting down the fire+ and the notices about its software."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import aiohttp
import pytest
from homeassistant.components.repairs import ConfirmRepairFlow
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir

from custom_components.drooff_fireplus_v2.const import DOMAIN
from custom_components.drooff_fireplus_v2.repairs import async_create_fix_flow

from .conftest import CONFIGURATION_V2_4, mock_fireplus, setup_integration
from .test_controls import CONFIGURATION_V2_4_6, panel, posts
from .test_entities import entity_id

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

SHUTDOWN_URL = "http://fire/php/Ausschalten.php"
STANDBY = panel(i8="aus")


def issue(hass: HomeAssistant, config_entry: MockConfigEntry, key: str) -> ir.IssueEntry | None:
    """Return a notice of the config entry."""
    return ir.async_get(hass).async_get_issue(DOMAIN, f"{key}_{config_entry.entry_id}")


async def press(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Press the button that shuts down the fire+."""
    await hass.services.async_call(
        "button", "press", {"entity_id": entity_id(hass, config_entry, "button.shutdown")}, blocking=True
    )


async def test_shutdown_disabled_by_default(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """Shutting down is rarely useful, so the button has to be enabled first."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    entry = er.async_get(hass).async_get(entity_id(hass, config_entry, "button.shutdown"))
    assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert entry.entity_category is er.EntityCategory.CONFIG


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_shutdown_in_standby(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """In standby the request of the web app is sent and a notice says what to do next."""
    aioclient_mock.post(SHUTDOWN_URL, text="")
    mock_fireplus(aioclient_mock, panel=STANDBY)
    await setup_integration(hass, config_entry)
    await press(hass, config_entry)
    shutdown = [call for call in posts(aioclient_mock) if str(call[1]) == SHUTDOWN_URL]
    assert len(shutdown) == 1
    assert shutdown[0][2] == {"Ausschalten": "1"}
    notice = issue(hass, config_entry, "shut_down")
    assert notice is not None
    assert notice.translation_placeholders == {"name": "Drooff fire+"}

    # answers while the fire+ is going down keep the notice
    await config_entry.runtime_data.coordinator.async_refresh()
    assert issue(hass, config_entry, "shut_down") is not None
    # an answer minutes later means it was started again
    freezer.tick(timedelta(minutes=3))
    await config_entry.runtime_data.coordinator.async_refresh()
    assert issue(hass, config_entry, "shut_down") is None


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_shutdown_only_in_standby(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """Like the web app, the fire+ is not shut down while the stove is burning."""
    aioclient_mock.post(SHUTDOWN_URL, text="")
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    with pytest.raises(ServiceValidationError) as error:
        await press(hass, config_entry)
    assert error.value.translation_key == "shutdown_not_standby"
    assert not any(str(call[1]) == SHUTDOWN_URL for call in posts(aioclient_mock))
    assert issue(hass, config_entry, "shut_down") is None


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_shutdown_not_supported(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """A fire+ without the page reports an error."""
    aioclient_mock.post(SHUTDOWN_URL, status=404)
    mock_fireplus(aioclient_mock, panel=STANDBY)
    await setup_integration(hass, config_entry)
    with pytest.raises(HomeAssistantError) as error:
        await press(hass, config_entry)
    assert error.value.translation_key == "shutdown_failed"
    assert issue(hass, config_entry, "shut_down") is None


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_shutdown_without_answer(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """The fire+ may go down before it answers, that is no error."""
    aioclient_mock.post(SHUTDOWN_URL, exc=aiohttp.ServerDisconnectedError())
    mock_fireplus(aioclient_mock, panel=STANDBY)
    await setup_integration(hass, config_entry)
    await press(hass, config_entry)
    assert issue(hass, config_entry, "shut_down") is not None


@pytest.mark.parametrize(
    ("answer", "key"),
    [
        ("6, Update angehalten", "update_postponed"),
        ("5, Update fehlgeschlagen", "update_failed"),
    ],
)
async def test_update_notices(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry, answer: str, key: str
) -> None:
    """A postponed or failed update is shown as a notice until the result changes."""
    # the first matching mock answers
    aioclient_mock.get("http://fire/php/UpdateErgebniss.php", text=f'\ufeff"{answer}\\n"')
    message = answer.partition(", ")[2]
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    notice = issue(hass, config_entry, key)
    assert notice is not None
    assert notice.translation_key == key
    assert notice.translation_placeholders["message"] == message

    aioclient_mock.clear_requests()
    mock_fireplus(aioclient_mock)
    await config_entry.runtime_data.coordinator.async_update_update_status(force=True)
    assert issue(hass, config_entry, key) is None


async def test_no_update_notice(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """Without a postponed or failed update there is no notice."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    assert not ir.async_get(hass).issues


async def test_update_status_read_every_10_minutes(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Without an enabled update sensor, the update status is read every 10 minutes."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    coordinator = config_entry.runtime_data.coordinator

    def reads() -> int:
        return sum("UpdateErgebniss" in str(call[1]) for call in aioclient_mock.mock_calls)

    assert reads() == 1
    freezer.tick(timedelta(minutes=5))
    await coordinator.async_update_update_status()
    assert reads() == 1
    freezer.tick(timedelta(minutes=5))
    await coordinator.async_update_update_status()
    assert reads() == 2


async def test_first_start_stores_versions(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
    hass_storage: dict,
) -> None:
    """On the first start there is nothing to compare with."""
    mock_fireplus(aioclient_mock, configuration=CONFIGURATION_V2_4_6)
    await setup_integration(hass, config_entry)
    await hass.async_block_till_done()
    assert issue(hass, config_entry, "firmware_updated") is None
    stored = hass_storage[f"{DOMAIN}.{config_entry.entry_id}.versions"]["data"]
    assert stored == {"firmware": "2.4.6", "web_app": "2.1.8"}


async def test_new_software(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
    hass_storage: dict,
) -> None:
    """New software, also installed while Home Assistant was not running, is shown once."""
    hass_storage[f"{DOMAIN}.{config_entry.entry_id}.versions"] = {
        "version": 1,
        "key": f"{DOMAIN}.{config_entry.entry_id}.versions",
        "data": {"firmware": "2.4.1", "web_app": None},
    }
    mock_fireplus(aioclient_mock, configuration=CONFIGURATION_V2_4_6)
    await setup_integration(hass, config_entry)
    notice = issue(hass, config_entry, "firmware_updated")
    assert notice is not None
    assert notice.is_fixable
    assert notice.translation_placeholders == {
        "name": "Drooff fire+",
        "old_version": "2.4.1",
        "new_version": "2.4.6 / 2.1.8",
    }
    registry = dr.async_get(hass)
    assert [device.sw_version for device in dr.async_entries_for_config_entry(registry, config_entry.entry_id)] == [
        "2.4.6"
    ]
    flow = await async_create_fix_flow(hass, f"firmware_updated_{config_entry.entry_id}", None)
    assert isinstance(flow, ConfirmRepairFlow)


async def test_new_software_while_running(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
) -> None:
    """An update the fire+ installs while Home Assistant runs is noticed with the next configuration."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    assert issue(hass, config_entry, "firmware_updated") is None

    aioclient_mock.clear_requests()
    mock_fireplus(aioclient_mock, configuration=["2.4.6", *CONFIGURATION_V2_4[1:]])
    client = config_entry.runtime_data.client
    # the configuration is cached for a minute
    client._configuration = None  # noqa: SLF001
    await config_entry.runtime_data.coordinator.async_refresh()
    notice = issue(hass, config_entry, "firmware_updated")
    assert notice is not None
    assert notice.translation_placeholders["old_version"] == "2.4.1"
    assert notice.translation_placeholders["new_version"] == "2.4.6"


async def test_remove_entry_deletes_notices(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """Removing the integration removes its notices."""
    aioclient_mock.get("http://fire/php/UpdateErgebniss.php", text='﻿"5, Update fehlgeschlagen\\n"')
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    assert issue(hass, config_entry, "update_failed") is not None
    await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()
    assert issue(hass, config_entry, "update_failed") is None
