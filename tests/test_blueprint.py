"""Tests for the wood required blueprint and its installation."""

from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
import yaml
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed, async_mock_service

from custom_components.drooff_fireplus_v2 import (
    BLUEPRINTS,
    SHIPPED_BLUEPRINTS,
    async_install_blueprints,
    blueprint_store,
)

from .conftest import mock_fireplus, setup_integration

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

BLUEPRINT = "drooff_fireplus_v2/wood_required_notification.yaml"
STATUS = "sensor.drooff_fire_operation_status"
KEY = "automation/wood_required_notification.yaml"


def installed(hass: HomeAssistant) -> Path:
    """Return the path of the installed blueprint."""
    return Path(hass.config.path("blueprints", "automation", BLUEPRINT))


async def test_blueprint_is_installed_and_updated(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, config_entry: MockConfigEntry
) -> None:
    """The blueprint is installed, an unchanged older copy is updated and automations reloaded."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    source = BLUEPRINTS / "automation" / "wood_required_notification.yaml"
    assert installed(hass).read_bytes() == source.read_bytes()

    reloads = async_mock_service(hass, "automation", "reload")
    await async_install_blueprints(hass)
    assert reloads == []

    # an older version the integration installed itself
    old = b"old version"
    installed(hass).write_bytes(old)
    await blueprint_store(hass).async_save({KEY: hashlib.sha256(old).hexdigest()})
    await async_install_blueprints(hass)
    assert installed(hass).read_bytes() == source.read_bytes()
    assert len(reloads) == 1


async def test_changed_blueprint_is_kept(hass: HomeAssistant) -> None:
    """A copy the user changed is neither overwritten at the next start nor by an update."""
    reloads = async_mock_service(hass, "automation", "reload")
    await async_install_blueprints(hass)
    changed = installed(hass).read_text(encoding="utf-8").replace("Holz nachlegen", "Holz holen")
    installed(hass).write_text(changed, encoding="utf-8")

    await async_install_blueprints(hass)
    assert installed(hass).read_text(encoding="utf-8") == changed

    # also when the integration ships a new version
    await blueprint_store(hass).async_save({KEY: "hash of an older version"})
    await async_install_blueprints(hass)
    assert installed(hass).read_text(encoding="utf-8") == changed
    assert reloads == []


@pytest.mark.parametrize("shipped", sorted(SHIPPED_BLUEPRINTS[KEY]))
async def test_unchanged_copy_of_an_earlier_version_is_updated(hass: HomeAssistant, shipped: str) -> None:
    """Copies installed before the hash was stored are updated when they match a shipped version."""
    reloads = async_mock_service(hass, "automation", "reload")
    old = b"shipped by an earlier version"
    installed(hass).parent.mkdir(parents=True, exist_ok=True)
    installed(hass).write_bytes(old)
    with patch.dict(SHIPPED_BLUEPRINTS, {KEY: {shipped, hashlib.sha256(old).hexdigest()}}):
        await async_install_blueprints(hass)
    source = BLUEPRINTS / "automation" / "wood_required_notification.yaml"
    assert installed(hass).read_bytes() == source.read_bytes()
    assert len(reloads) == 1


async def test_unknown_copy_without_hash_is_kept(hass: HomeAssistant) -> None:
    """A copy that matches no shipped version and has no stored hash is treated as changed by the user."""
    installed(hass).parent.mkdir(parents=True, exist_ok=True)
    installed(hass).write_bytes(b"my own version")
    await async_install_blueprints(hass)
    assert installed(hass).read_bytes() == b"my own version"


async def test_deleted_blueprint_is_installed_again(hass: HomeAssistant) -> None:
    """A deleted copy is installed again."""
    await async_install_blueprints(hass)
    installed(hass).unlink()
    await async_install_blueprints(hass)
    assert installed(hass).is_file()


def notify(action: str, **data: Any) -> list[dict[str, Any]]:
    """Return a notify action as the blueprint editor creates it."""
    return [{"action": action, "data": {"title": "{{ title }}", "message": "{{ text }}", **data}}]


async def setup_automation(hass: HomeAssistant, inputs: dict[str, Any]) -> None:
    """Install the blueprint and create an automation from it."""
    await async_install_blueprints(hass)
    hass.states.async_set(STATUS, "regular")
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": {
                "id": "wood",
                "use_blueprint": {"path": BLUEPRINT, "input": {"status_sensor": STATUS, **inputs}},
            }
        },
    )
    await hass.async_block_till_done()


async def settle() -> None:
    """Let the automation run until it waits for a delay (async_block_till_done would wait for the delay too)."""
    for _ in range(50):
        await asyncio.sleep(0)


async def set_status(hass: HomeAssistant, status: str) -> None:
    """Change the operation status."""
    hass.states.async_set(STATUS, status)
    await settle()


async def wait(hass: HomeAssistant, minutes: int) -> None:
    """Let some minutes pass."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=minutes, seconds=1))
    await settle()


async def test_default_is_a_home_assistant_notification(hass: HomeAssistant) -> None:
    """By default a Home Assistant notification is created."""
    persistent = async_mock_service(hass, "notify", "persistent_notification")
    await setup_automation(hass, {})
    await set_status(hass, "wood_required")
    assert [call.data for call in persistent] == [{"title": "Kaminofen", "message": "Bitte Holz nachlegen."}]


async def test_all_channels_can_be_empty(hass: HomeAssistant, caplog: pytest.LogCaptureFixture) -> None:
    """Every channel is optional."""
    persistent = async_mock_service(hass, "notify", "persistent_notification")
    await setup_automation(hass, {"notify_actions": []})
    await set_status(hass, "wood_required")
    await wait(hass, 1)
    assert persistent == []
    assert "Error" not in caplog.text


async def test_pushover_preset_is_off(hass: HomeAssistant) -> None:
    """The preset Pushover action is switched off, the Home Assistant notification is on."""
    persistent = async_mock_service(hass, "notify", "persistent_notification")
    pushover = async_mock_service(hass, "notify", "pushover")
    await setup_automation(hass, {})
    await set_status(hass, "wood_required")
    assert len(persistent) == 1
    assert pushover == []


def preset(key: str) -> list[dict[str, Any]]:
    """Return the default of an input of the blueprint."""
    loader = type("Loader", (yaml.SafeLoader,), {})
    loader.add_constructor("!input", lambda ldr, node: ldr.construct_scalar(node))
    source = (BLUEPRINTS / "automation" / "wood_required_notification.yaml").read_text(encoding="utf-8")
    blueprint = yaml.load(source, Loader=loader)["blueprint"]  # noqa: S506
    sections = blueprint["input"].values()
    return next(section["input"][key]["default"] for section in sections if key in section.get("input", {}))


@pytest.mark.parametrize(
    ("key", "status", "priority", "sound"),
    [
        ("notify_actions", "wood_required", 0, "pushover"),
        ("urgent_notify_actions", "wood_urgently_required", 1, "siren"),
    ],
)
async def test_pushover_preset_switched_on(
    hass: HomeAssistant, key: str, status: str, priority: int, sound: str
) -> None:
    """Switching the preset Pushover action on sends title, message, priority and sound."""
    pushover = async_mock_service(hass, "notify", "pushover")
    actions = [{**action, "enabled": True} for action in preset(key) if action["action"] == "notify.pushover"]
    await setup_automation(hass, {"urgent_enabled": True, key: actions})
    await set_status(hass, status)
    assert len(pushover) == 1
    assert pushover[0].data["data"] == {"priority": priority, "sound": sound}
    assert pushover[0].data["title"] == "Kaminofen"


@pytest.mark.parametrize(
    "inputs",
    [
        {"notify_actions": [], "alexa_notify_entities": ["notify.kitchen_announce"]},
        {
            "notify_actions": None,
            "custom_actions": None,
            "alexa_media_players": None,
            "alexa_notify_entities": ["notify.kitchen_announce"],
            "notify_delay": None,
            "echo_delay": None,
            "custom_delay": None,
            "title": None,
            "message": None,
            "echo_message": None,
        },
    ],
)
async def test_echo_only(hass: HomeAssistant, inputs: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    """Echo alone is enough, also when the editor stores empty inputs as null."""
    persistent = async_mock_service(hass, "notify", "persistent_notification")
    send_message = async_mock_service(hass, "notify", "send_message")
    await setup_automation(hass, inputs)
    await set_status(hass, "wood_required")
    assert persistent == []
    assert [call.data for call in send_message] == [
        {"entity_id": ["notify.kitchen_announce"], "message": "Bitte Holz nachlegen."}
    ]
    assert "Error" not in caplog.text


async def test_notification_only(hass: HomeAssistant, caplog: pytest.LogCaptureFixture) -> None:
    """A notification alone is enough, Echo stays silent."""
    pushover = async_mock_service(hass, "notify", "pushover")
    alexa = async_mock_service(hass, "notify", "alexa_media")
    send_message = async_mock_service(hass, "notify", "send_message")
    await setup_automation(hass, {"notify_actions": notify("notify.pushover")})
    await set_status(hass, "wood_required")
    assert len(pushover) == 1
    assert alexa == []
    assert send_message == []
    assert "Error" not in caplog.text


async def test_each_channel_after_its_delay(hass: HomeAssistant) -> None:
    """Every channel waits for its own delay."""
    pushover = async_mock_service(hass, "notify", "pushover")
    alexa = async_mock_service(hass, "notify", "alexa_media")
    lights = async_mock_service(hass, "light", "turn_on")
    await setup_automation(
        hass,
        {
            "notify_actions": notify("notify.pushover", data={"priority": 1}),
            "alexa_media_players": ["media_player.kitchen"],
            "echo_message": "Holz bitte",
            "echo_delay": {"minutes": 5},
            "custom_actions": [{"action": "light.turn_on", "data": {"entity_id": "light.hall", "flash": "short"}}],
            "custom_delay": {"minutes": 10},
        },
    )
    await set_status(hass, "wood_required")
    assert len(pushover) == 1
    assert pushover[0].data == {"title": "Kaminofen", "message": "Bitte Holz nachlegen.", "data": {"priority": 1}}
    assert alexa == []

    await wait(hass, 5)
    assert len(alexa) == 1
    assert alexa[0].data == {"target": ["media_player.kitchen"], "message": "Holz bitte", "data": {"type": "announce"}}
    assert lights == []

    await wait(hass, 10)
    assert len(lights) == 1
    assert len(pushover) == 1


async def test_urgent_uses_normal_actions_until_enabled(hass: HomeAssistant) -> None:
    """Without own urgent actions, the actions for wood required are used with the urgent text."""
    pushover = async_mock_service(hass, "notify", "pushover")
    await setup_automation(
        hass, {"notify_actions": notify("notify.pushover"), "urgent_notify_actions": notify("notify.pushover")}
    )
    await set_status(hass, "wood_urgently_required")
    assert [call.data["message"] for call in pushover] == ["Dringend Holz nachlegen!"]


async def test_urgent_actions(hass: HomeAssistant) -> None:
    """With own urgent actions enabled, wood urgently required has its own channels."""
    pushover = async_mock_service(hass, "notify", "pushover")
    phone = async_mock_service(hass, "notify", "mobile_app_phone")
    sirens = async_mock_service(hass, "siren", "turn_on")
    lights = async_mock_service(hass, "light", "turn_on")
    await setup_automation(
        hass,
        {
            "notify_actions": notify("notify.mobile_app_phone"),
            "custom_actions": [{"action": "light.turn_on", "target": {"entity_id": "light.hall"}}],
            "urgent_enabled": True,
            "urgent_notify_actions": notify("notify.pushover", data={"priority": 2}),
            "urgent_custom_actions": [{"action": "siren.turn_on", "data": {"entity_id": "siren.hall"}}],
        },
    )
    await set_status(hass, "wood_required")
    assert len(phone) == 1
    assert len(lights) == 1

    await set_status(hass, "wood_urgently_required")
    assert [call.data for call in pushover] == [
        {"title": "Kaminofen", "message": "Dringend Holz nachlegen!", "data": {"priority": 2}}
    ]
    assert len(sirens) == 1
    assert len(phone) == 1
    assert len(lights) == 1


@pytest.mark.parametrize("new_status", ["regular", "unavailable"])
async def test_no_reminder_once_wood_was_added(hass: HomeAssistant, new_status: str) -> None:
    """A pending reminder is dropped when wood is no longer required."""
    phone = async_mock_service(hass, "notify", "mobile_app_phone")
    await setup_automation(hass, {"notify_actions": notify("notify.mobile_app_phone"), "notify_delay": {"minutes": 10}})
    await set_status(hass, "wood_required")
    await set_status(hass, new_status)
    await wait(hass, 10)
    assert phone == []


async def test_no_reminder_on_the_way_back_from_urgent(hass: HomeAssistant) -> None:
    """After wood was added, the fire+ passes from urgent through wood required to regular without a reminder."""
    persistent = async_mock_service(hass, "notify", "persistent_notification")
    await setup_automation(hass, {})
    await set_status(hass, "wood_urgently_required")
    assert [call.data["message"] for call in persistent] == ["Dringend Holz nachlegen!"]
    await set_status(hass, "wood_required")
    await set_status(hass, "regular")
    await wait(hass, 1)
    assert len(persistent) == 1


async def test_urgent_reminder_dropped_on_the_way_back(hass: HomeAssistant) -> None:
    """A pending urgent reminder is dropped once the status goes back to wood required."""
    phone = async_mock_service(hass, "notify", "mobile_app_phone")
    await setup_automation(hass, {"notify_actions": notify("notify.mobile_app_phone"), "notify_delay": {"minutes": 10}})
    await set_status(hass, "wood_urgently_required")
    await set_status(hass, "wood_required")
    await wait(hass, 10)
    assert phone == []


async def test_notify_entities_and_wood_load(hass: HomeAssistant) -> None:
    """Notify entities get the message with the recommended wood load."""
    send_message = async_mock_service(hass, "notify", "send_message")
    hass.states.async_set("sensor.drooff_fire_wood_load", "1.5")
    await setup_automation(
        hass,
        {
            "wood_load_sensor": "sensor.drooff_fire_wood_load",
            "notify_actions": [
                {
                    "action": "notify.send_message",
                    "target": {"entity_id": "notify.phone"},
                    "data": {"message": "{{ text }}"},
                }
            ],
            "alexa_notify_entities": ["notify.kitchen_announce"],
        },
    )
    await set_status(hass, "wood_required")
    assert sorted((str(call.data["entity_id"]), call.data["message"]) for call in send_message) == [
        ("['notify.kitchen_announce']", "Bitte Holz nachlegen. (2 Holzscheite)"),
        ("['notify.phone']", "Bitte Holz nachlegen. (2 Holzscheite)"),
    ]


@pytest.mark.parametrize(
    ("load", "inputs", "expected"),
    [
        # by default the number of logs, 0.7 kg per log
        ("1.4", {}, "Bitte Holz nachlegen. (2 Holzscheite)"),
        ("0.5", {}, "Bitte Holz nachlegen. (1 Holzscheit)"),
        # at least one log, also for a very small amount
        ("0.1", {}, "Bitte Holz nachlegen. (1 Holzscheit)"),
        ("2.6", {"log_weight": 1.3}, "Bitte Holz nachlegen. (2 Holzscheite)"),
        ("1.5", {"wood_load_unit": "kg"}, "Bitte Holz nachlegen. (1.5 kg)"),
        ("1.5", {"wood_load_unit": "both"}, "Bitte Holz nachlegen. (2 Holzscheite, 1.5 kg)"),
        ("2.1", {"language": "en"}, "Please add wood. (3 logs)"),
        ("0.6", {"language": "en"}, "Please add wood. (1 log)"),
        # no recommendation from the fire+, no amount
        ("0", {}, "Bitte Holz nachlegen."),
    ],
)
async def test_wood_load_as_logs_or_kg(hass: HomeAssistant, load: str, inputs: dict[str, Any], expected: str) -> None:
    """The wood load is shown as logs by default, or in kg, or both."""
    pushover = async_mock_service(hass, "notify", "pushover")
    hass.states.async_set("sensor.drooff_fire_wood_load", load)
    await setup_automation(
        hass,
        {"wood_load_sensor": "sensor.drooff_fire_wood_load", "notify_actions": notify("notify.pushover"), **inputs},
    )
    await set_status(hass, "wood_required")
    assert [call.data["message"] for call in pushover] == [expected]


async def test_english_and_own_texts(hass: HomeAssistant) -> None:
    """The language selects the default texts, own texts replace them."""
    pushover = async_mock_service(hass, "notify", "pushover")
    await setup_automation(
        hass,
        {
            "language": "en",
            "notify_actions": notify("notify.pushover"),
            "urgent_enabled": True,
            "urgent_notify_actions": notify("notify.pushover"),
            "urgent_title": "Stove",
            "urgent_message": "Wood, quickly!",
        },
    )
    await set_status(hass, "wood_required")
    await set_status(hass, "wood_urgently_required")
    assert [(call.data["title"], call.data["message"]) for call in pushover] == [
        ("Fireplace", "Please add wood."),
        ("Stove", "Wood, quickly!"),
    ]


def test_source_url_points_to_the_release() -> None:
    """The source_url names the tag of this version, so tools fetch exactly the installed blueprint."""
    manifest = json.loads((BLUEPRINTS.parent / "manifest.json").read_text(encoding="utf-8"))
    for path in BLUEPRINTS.glob("*/*.yaml"):
        text = path.read_text(encoding="utf-8")
        line = next(x for x in text.splitlines() if x.strip().startswith("source_url:"))
        rel = path.relative_to(BLUEPRINTS.parent.parent.parent).as_posix()
        assert line.split(":", 1)[1].strip() == (
            f"https://github.com/steigerbalett/ha-drooff-fireplus-v2/blob/v{manifest['version']}/{rel}"
        )
