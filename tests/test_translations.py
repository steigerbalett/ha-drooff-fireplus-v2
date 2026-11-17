"""Tests for the translations of the integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

COMPONENT = Path(__file__).parent.parent / "custom_components" / "drooff_fireplus_v2"


def keys(data: dict, prefix: str = "") -> set[str]:
    """Return the dotted keys of a translation file."""
    result = set()
    for key, value in data.items():
        if isinstance(value, dict):
            result |= keys(value, f"{prefix}{key}.")
        else:
            result.add(f"{prefix}{key}")
    return result


def placeholders(text: str) -> set[str]:
    """Return the placeholders like {host} of a text."""
    return {part.split("}")[0] for part in text.split("{")[1:]}


@pytest.mark.parametrize("language", ["de", "en", "fr"])
def test_translation_has_every_key(language: str) -> None:
    """Every language translates exactly the texts of strings.json, with the same placeholders."""
    strings = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
    translation = json.loads((COMPONENT / "translations" / f"{language}.json").read_text(encoding="utf-8"))
    assert keys(translation) == keys(strings)

    def lookup(data: dict, key: str) -> str:
        for part in key.split("."):
            data = data[part]
        return data

    for key in keys(strings):
        assert placeholders(lookup(translation, key)) == placeholders(lookup(strings, key)), key
