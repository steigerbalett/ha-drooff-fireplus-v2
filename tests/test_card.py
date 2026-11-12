"""Tests for the dashboard card."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from .conftest import mock_fireplus, setup_integration

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
    from pytest_homeassistant_custom_component.typing import ClientSessionGenerator


async def test_card_is_served(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
) -> None:
    """The card is served by the integration."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    client = await hass_client()
    response = await client.get("/drooff_fireplus_v2/drooff-fireplus-card.js")
    assert response.status == 200
    assert "customElements.define" in await response.text()


async def test_stove_pictures_are_served(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
) -> None:
    """The product pictures of Drooff are served next to the card."""
    mock_fireplus(aioclient_mock)
    await setup_integration(hass, config_entry)
    client = await hass_client()
    response = await client.get("/drooff_fireplus_v2/stoves/brunello-2-l-stahl-schwarz.webp")
    assert response.status == 200
    assert (await response.read())[8:12] == b"WEBP"
    response = await client.get("/drooff_fireplus_v2/stoves/LICENSE.md")
    assert response.status == 200
    assert "DROOFF Kaminöfen GmbH & Co. KG" in await response.text()


def test_stove_pictures_match_the_card() -> None:
    """Every picture in the card has a preview and a picture in the repository, windows lie in the picture."""
    root = Path(__file__).parent.parent
    folder = root / "custom_components" / "drooff_fireplus_v2" / "frontend"
    pictures = root / "pictures" / "stoves"
    card = (folder / "drooff-fireplus-card.js").read_text(encoding="utf-8")
    table = card[card.index("const STOVE_PICTURES = {") :]
    table = table[: table.index("};")]
    models = card[card.index("const STOVE_MODELS = [") : card.index("const STOVES_URL")]
    model_ids = set(re.findall(r'^  \["(\w+)", ', models, re.MULTILINE))
    used = set()
    assert model_ids
    for model in re.findall(r"^  (\w+): \[", table, re.MULTILINE):
        assert model in model_ids
    for name, left, top, width, height in re.findall(
        r'\["([a-z0-9-]+)", "[^"]*", "[^"]*", \[([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\]\]', table
    ):
        used.add(name)
        assert (folder / "stoves" / f"{name}.webp").is_file(), name
        assert (pictures / f"{name}.webp").is_file(), name
        assert float(left) >= 0, name
        assert float(top) >= 0, name
        assert float(left) + float(width) <= 100.5, name
        assert float(top) + float(height) <= 100.5, name
    assert {p.stem for p in (folder / "stoves").glob("*.webp")} == used
    assert {p.stem for p in pictures.glob("*.webp")} == used
    assert (folder / "stoves" / "LICENSE.md").is_file()
    assert (pictures / "LICENSE.md").is_file()
    # only the small previews are part of the integration
    assert max(p.stat().st_size for p in (folder / "stoves").glob("*.webp")) < 8000
