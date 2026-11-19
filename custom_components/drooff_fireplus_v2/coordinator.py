"""DataUpdateCoordinator for drooff_fireplus_v2."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import FireplusApiClientError, FireplusUpdateResult
from .const import DOMAIN, LOGGER, UPDATE_FAILED_MSG
from .statistics import FireplusStatistics, parse_events

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import HomeAssistant

    from .api import FireplusResponse, FireplusUpdateStatus
    from .data import FireplusConfigEntry


STATISTICS_STORAGE_VERSION = 1
# Delay before the statistics are written to disk (s)
STATISTICS_SAVE_DELAY = 30

# Like the web app: warn when the door is open longer than 5 minutes while the stove is hotter than 40 °C
DOOR_OPEN_TEMPERATURE = 40
DOOR_OPEN_TOO_LONG = timedelta(minutes=5)

# Without an enabled update sensor, the update status is only read this often for the notices
UPDATE_NOTICE_INTERVAL = timedelta(minutes=10)

# The web app says to disconnect the fire+ 2 minutes after shutting it down; an answer after this
# time means it was started again
SHUTDOWN_DURATION = timedelta(minutes=3)

# Notices (repairs) for these update results, removed when the result changes
UPDATE_ISSUES = {
    FireplusUpdateResult.POSTPONED: "update_postponed",
    FireplusUpdateResult.FAILED: "update_failed",
}


def statistics_store(hass: HomeAssistant, entry_id: str) -> Store[dict]:
    """Return the store of the statistics of a config entry."""
    return Store(hass, STATISTICS_STORAGE_VERSION, f"{DOMAIN}.{entry_id}.statistics")


def versions_store(hass: HomeAssistant, entry_id: str) -> Store[dict]:
    """Return the store of the last known software versions of a config entry."""
    return Store(hass, 1, f"{DOMAIN}.{entry_id}.versions")


def issue_id(key: str, entry_id: str) -> str:
    """Return the id of a notice (repair) of a config entry."""
    return f"{key}_{entry_id}"


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class FireplusDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Drooff fire+ API."""

    config_entry: FireplusConfigEntry
    host: str

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: FireplusConfigEntry,
        update_interval: timedelta,
        host: str,
    ) -> None:
        """Initialize the FireplusDataUpdateCoordinator."""
        self.host = host
        self.statistics = FireplusStatistics()
        # None until the event log was read once, False if the fire+ has none
        self.events_supported: bool | None = None
        self._statistics_store: Store[dict] = statistics_store(hass, config_entry.entry_id)
        # Since when the door is open while the stove is hot
        self.door_open_since: datetime | None = None
        self.door_open_too_long: bool | None = None
        # None until read once, False if the fire+ does not report its updates
        self.update_status: FireplusUpdateStatus | None = None
        self.update_supported: bool | None = None
        # Number of enabled sensors that show the update status
        self.update_sensors = 0
        self._update_read: datetime | None = None
        # Software versions of the fire+ when it was last seen, None until loaded
        self._versions_store: Store[dict] = versions_store(hass, config_entry.entry_id)
        self._versions: dict[str, str | None] | None = None
        # When the fire+ was shut down from Home Assistant
        self.shut_down_at: datetime | None = None
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=update_interval,
            # entities are only written when the fire+ reports something new
            always_update=False,
        )

    async def _async_update_data(self) -> Any:
        """Retrieve updated data from Drooff fire+ API."""
        retries = 0
        max_retries = 3

        while retries < max_retries:
            try:
                data = await self.config_entry.runtime_data.client.async_get_data()
            except FireplusApiClientError as exception:
                retries += 1
                if retries < max_retries:
                    await asyncio.sleep(1)
                else:
                    raise UpdateFailed(exception) from exception
            else:
                self._track_door(data)
                self._track_versions(data)
                self._track_shut_down()
                return data

        raise UpdateFailed(UPDATE_FAILED_MSG)

    def _track_door(self, data: FireplusResponse) -> None:
        """Track how long the door has been open while the stove is hot."""
        if data.door_open is None:
            too_long = None
        else:
            if data.door_open and data.temperature > DOOR_OPEN_TEMPERATURE:
                if self.door_open_since is None:
                    self.door_open_since = dt_util.utcnow()
            else:
                self.door_open_since = None
            too_long = self.door_open_since is not None and dt_util.utcnow() - self.door_open_since > DOOR_OPEN_TOO_LONG
        if too_long != self.door_open_too_long:
            self.door_open_too_long = too_long
            # identical responses of the fire+ do not update the entities, so do it here
            if self.data is not None and data == self.data:
                self.async_update_listeners()

    def _track_versions(self, data: FireplusResponse) -> None:
        """Show a notice when the software of the fire+ has changed since it was last seen."""
        if self._versions is None:
            return
        versions = {"firmware": str(data.version), "web_app": data.web_app_version}
        if versions == self._versions:
            return
        old = self._versions
        self._versions = versions
        self._versions_store.async_delay_save(lambda: versions, 0)
        if not old:
            # first start, nothing to compare with
            return
        LOGGER.info("The software of the fire+ changed from %s to %s", old, versions)
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            issue_id("firmware_updated", self.config_entry.entry_id),
            is_fixable=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="firmware_updated",
            translation_placeholders={
                "name": self.config_entry.title,
                "old_version": _describe_versions(old),
                "new_version": _describe_versions(versions),
            },
        )
        # the device page shows the new version without a reload
        registry = dr.async_get(self.hass)
        for device in dr.async_entries_for_config_entry(registry, self.config_entry.entry_id):
            registry.async_update_device(device.id, sw_version=versions["firmware"])

    async def async_load_versions(self) -> None:
        """Restore the software versions the fire+ had when it was last seen."""
        self._versions = await self._versions_store.async_load() or {}
        if self.data is not None:
            self._track_versions(self.data)

    def async_shut_down(self) -> None:
        """Show a notice after the fire+ was shut down, until it answers again."""
        self.shut_down_at = dt_util.utcnow()
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            issue_id("shut_down", self.config_entry.entry_id),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="shut_down",
            translation_placeholders={"name": self.config_entry.title},
        )

    def _track_shut_down(self) -> None:
        """Remove the notice once the fire+ answers again after it was shut down."""
        if self.shut_down_at is None or dt_util.utcnow() - self.shut_down_at < SHUTDOWN_DURATION:
            return
        self.shut_down_at = None
        ir.async_delete_issue(self.hass, DOMAIN, issue_id("shut_down", self.config_entry.entry_id))

    async def async_load_statistics(self) -> None:
        """Restore the statistics of the last run."""
        self.statistics = FireplusStatistics.from_dict(await self._statistics_store.async_load())

    async def async_save_statistics(self) -> None:
        """Write the statistics now, for example before the entry is unloaded."""
        await self._statistics_store.async_save(self.statistics.as_dict())

    async def async_update_statistics(self, _now: datetime | None = None) -> None:
        """Read new entries of the event log and update the statistics."""
        try:
            response = await self.config_entry.runtime_data.client.async_get_events(self.statistics.last_event)
        except FireplusApiClientError as exception:
            # older firmware has no event log; the statistics are not important enough for an error
            if self.events_supported is None:
                self.events_supported = False
                self.async_update_listeners()
            LOGGER.debug("Reading the event log failed: %s", exception)
            return
        first = self.events_supported is not True
        self.events_supported = True
        weight = self.data.weight if self.data is not None else None
        if self.statistics.process(parse_events(response), weight):
            self._statistics_store.async_delay_save(self.statistics.as_dict, STATISTICS_SAVE_DELAY)
            self.async_update_listeners()
        elif first:
            self.async_update_listeners()

    async def async_update_update_status(self, _now: datetime | None = None, *, force: bool = False) -> None:
        """
        Read the result of the last software update.

        Every minute while one of its sensors is enabled, otherwise every 10 minutes for the
        notices about a postponed or failed update.
        """
        now = dt_util.utcnow()
        if (
            not force
            and not self.update_sensors
            and self._update_read is not None
            and now - self._update_read < UPDATE_NOTICE_INTERVAL
        ):
            return
        self._update_read = now
        try:
            status = await self.config_entry.runtime_data.client.async_get_update_status()
        except FireplusApiClientError as exception:
            if self.update_supported is None:
                self.update_supported = False
                self.async_update_listeners()
            LOGGER.debug("Reading the update status failed: %s", exception)
            return
        self.update_supported = True
        if status != self.update_status:
            self.update_status = status
            self._update_issues(status)
            self.async_update_listeners()

    def _update_issues(self, status: FireplusUpdateStatus) -> None:
        """Show a notice while an update waits for the stove to be off or has failed."""
        for result, key in UPDATE_ISSUES.items():
            if status.result is result:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    issue_id(key, self.config_entry.entry_id),
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key=key,
                    translation_placeholders={"name": self.config_entry.title, "message": status.message or "-"},
                )
            else:
                ir.async_delete_issue(self.hass, DOMAIN, issue_id(key, self.config_entry.entry_id))


def _describe_versions(versions: dict[str, str | None]) -> str:
    """Describe the firmware and web app version, e.g. 2.4.6 / 2.1.8."""
    if versions.get("web_app"):
        return f"{versions['firmware']} / {versions['web_app']}"
    return str(versions["firmware"])
