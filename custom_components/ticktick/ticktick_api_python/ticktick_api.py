"""TickTick API Client."""

import json
from urllib.parse import urlencode

from aiohttp import ClientResponse, ClientSession
from custom_components.ticktick.const import (
    COMPLETE_TASK,
    CREATE_TASK,
    DELETE_TASK,
    GET_HABIT,
    GET_HABIT_CHECKINS,
    GET_HABIT_SECTIONS,
    GET_HABITS,
    GET_PROJECTS,
    GET_PROJECTS_WITH_TASKS,
    GET_TASK,
    UPDATE_TASK,
    UPSERT_HABIT_CHECKIN,
)

from .models.habit import Habit, HabitCheckin, HabitCheckinData
from .models.project import Kind, Project
from .models.project_with_tasks import ProjectWithTasks
from .models.task import Task


class TickTickAPIClient:
    """TickTick API Client."""

    def __init__(self, access_token: str, session: ClientSession) -> None:
        """Initialize the TickTick API client."""
        self._headers = {"Authorization": f"Bearer {access_token}"}
        self._session = session

    # === Task Scope ===
    async def get_task(
        self, projectId: str, taskId: str, returnAsJson: bool = False
    ) -> Task:
        """Return a task."""
        response = await self._get(GET_TASK.format(projectId=projectId, taskId=taskId))
        if returnAsJson:
            return response

        return Task.from_dict(response)

    async def create_task(self, task: Task, returnAsJson: bool = False) -> Task:
        """Create a task."""
        json = task.toJSON()
        response = await self._post(CREATE_TASK, json)
        if returnAsJson:
            return response

        return Task.from_dict(response)

    async def update_task(self, task: Task, returnAsJson: bool = False) -> Task:
        """Update a task."""
        json = task.toJSON()
        response = await self._post(UPDATE_TASK.format(taskId=task.id), json)
        if returnAsJson:
            return response

        return Task.from_dict(response)

    async def complete_task(self, projectId: str, taskId: str) -> str:
        """Complete a task."""
        return await self._post(
            COMPLETE_TASK.format(projectId=projectId, taskId=taskId)
        )

    async def delete_task(self, projectId: str, taskId: str) -> str:
        """Delete a task."""
        return await self._delete(
            DELETE_TASK.format(projectId=projectId, taskId=taskId)
        )

    # === Project Scope ===
    async def get_projects(self, returnAsJson: bool = False) -> list[Project]:
        """Return a dict of all projects basic informations."""
        response = await self._get(GET_PROJECTS)
        if returnAsJson:
            return response

        mappedResponse = [Project.from_dict(project) for project in response]
        filtered_projects = list(
            filter(
                lambda project: project.kind == Kind.TASK and not project.closed,
                mappedResponse,
            )  # Filtering out for now Notes
        )
        return filtered_projects

    async def get_project_with_tasks(self, projectId: str) -> list[ProjectWithTasks]:
        """Return a dict of tasks for project."""
        response = await self._get(GET_PROJECTS_WITH_TASKS.format(projectId=projectId))
        return ProjectWithTasks.from_dict(response)

    # === Habit Scope ===
    async def get_habits(self, returnAsJson: bool = False) -> list[Habit]:
        """Return all habits."""
        response = await self._get(GET_HABITS)
        if returnAsJson:
            return response

        return [Habit.from_dict(habit) for habit in response]

    async def get_habit(self, habitId: str, returnAsJson: bool = False) -> Habit:
        """Return a habit."""
        response = await self._get(GET_HABIT.format(habitId=habitId))
        if returnAsJson:
            return response

        return Habit.from_dict(response)

    async def get_habit_sections(self, returnAsJson: bool = True) -> list[dict]:
        """Return habit sections."""
        return await self._get(GET_HABIT_SECTIONS)

    async def get_habit_checkins(
        self,
        habitIds: list[str],
        fromStamp: int,
        toStamp: int,
        returnAsJson: bool = False,
    ) -> list[HabitCheckin]:
        """Return check-ins of habits between two YYYYMMDD date stamps."""
        query = urlencode(
            {"habitIds": ",".join(habitIds), "from": fromStamp, "to": toStamp},
            safe=",",
        )
        response = await self._get(f"{GET_HABIT_CHECKINS}?{query}")
        if returnAsJson:
            return response

        return [HabitCheckin.from_dict(checkin) for checkin in response]

    async def upsert_habit_checkin(
        self, habitId: str, checkin: HabitCheckinData, returnAsJson: bool = False
    ) -> HabitCheckin:
        """Create or update a habit check-in."""
        response = await self._post(
            UPSERT_HABIT_CHECKIN.format(habitId=habitId),
            json.dumps(checkin.to_dict()),
        )
        if returnAsJson:
            return response

        return HabitCheckin.from_dict(response)

    async def _get(self, url: str) -> ClientResponse:
        response = await self._session.get(f"https://{url}", headers=self._headers)
        return await self._get_response(response)

    async def _post(self, url: str, json_body: str | None = None) -> ClientResponse:
        self._headers["Content-Type"] = "application/json"
        response = await self._session.post(
            f"https://{url}",
            headers=self._headers,
            data=json_body if json_body else None,
        )
        return await self._get_response(response)

    async def _delete(self, url: str) -> ClientResponse:
        response = await self._session.delete(f"https://{url}", headers=self._headers)
        return await self._get_response(response)

    async def _get_response(
        self, response: ClientResponse
    ) -> tuple[ClientResponse, bool]:
        if response.ok:
            try:
                json_data = await response.json()
            except Exception:  # noqa: BLE001
                return {"status": "Success"}

            if json_data is None:  # Handle case when the response body is null
                return {"status": "Success"}
            return json_data
        raise Exception(  # noqa: TRY002
            f"Unsucessful response from TickTick, status code: {response.status}, content: {await response.json()}"
        )
