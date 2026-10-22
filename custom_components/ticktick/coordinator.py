"""DataUpdateCoordinator for the TickTick component."""

import asyncio
from dataclasses import dataclass
from datetime import date, timedelta
import logging

from custom_components.ticktick.ticktick_api_python.models.habit import (
    Habit,
    HabitCheckinData,
)
from custom_components.ticktick.ticktick_api_python.models.project import Project
from custom_components.ticktick.ticktick_api_python.models.project_with_tasks import (
    ProjectWithTasks,
)
from custom_components.ticktick.ticktick_api_python.ticktick_api import (
    TickTickAPIClient,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util


class TickTickCoordinator(DataUpdateCoordinator[list[ProjectWithTasks]]):
    """Coordinator for updating task data from TickTick."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        entry: ConfigEntry | None,
        update_interval: timedelta,
        api: TickTickAPIClient,
        access_token: str,
    ) -> None:
        """Initialize the TickTick coordinator."""
        super().__init__(
            hass,
            logger,
            config_entry=entry,
            name="TickTick",
            update_interval=update_interval,
        )
        self.api = api
        self._projects: list[Project] | None = None
        self.access_token = access_token

    async def _async_update_data(self) -> list[ProjectWithTasks]:
        """Fetch projects with tasks from the TickTick API."""
        try:
            if self._projects is None:
                await self.async_get_projects()

            fetch_projects_with_tasks = [
                self.api.get_project_with_tasks(project.id)
                for project in self._projects
            ]

            return await asyncio.gather(*fetch_projects_with_tasks)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_get_projects(self) -> list[Project]:
        """Return TickTick projects fetched at most once."""
        if self._projects is None:
            self._projects = await self.api.get_projects()
        return self._projects


@dataclass
class HabitWithCheckin:
    """Habit together with its check-in for today."""

    habit: Habit
    checkin: HabitCheckinData | None


def date_stamp(day: date) -> int:
    """Return the date as TickTick YYYYMMDD stamp."""
    return int(day.strftime("%Y%m%d"))


def today_stamp() -> int:
    """Return today's date in Home Assistant time zone as YYYYMMDD stamp."""
    return date_stamp(dt_util.now().date())


class TickTickHabitCoordinator(DataUpdateCoordinator[list[HabitWithCheckin]]):
    """Coordinator for updating habit data from TickTick."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        entry: ConfigEntry | None,
        update_interval: timedelta,
        api: TickTickAPIClient,
    ) -> None:
        """Initialize the TickTick habit coordinator."""
        super().__init__(
            hass,
            logger,
            config_entry=entry,
            name="TickTick Habits",
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> list[HabitWithCheckin]:
        """Fetch active habits with today's check-ins from the TickTick API."""
        try:
            habits = [
                habit
                for habit in await self.api.get_habits()
                if not habit.is_archived
            ]
            if not habits:
                return []

            today = dt_util.now().date()
            stamp = date_stamp(today)
            # TickTick excludes the `to` stamp, so ask up to tomorrow
            habit_checkins = await self.api.get_habit_checkins(
                [habit.id for habit in habits],
                stamp,
                date_stamp(today + timedelta(days=1)),
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        todays_checkins = {
            habit_checkin.habitId: checkin
            for habit_checkin in habit_checkins
            for checkin in habit_checkin.checkins
            if checkin.stamp == stamp
        }
        return [
            HabitWithCheckin(habit=habit, checkin=todays_checkins.get(habit.id))
            for habit in sorted(habits, key=lambda habit: habit.sortOrder or 0)
        ]


@dataclass
class TickTickData:
    """Coordinators of a TickTick config entry."""

    tasks: TickTickCoordinator
    habits: TickTickHabitCoordinator
