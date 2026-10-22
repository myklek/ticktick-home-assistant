from enum import IntEnum


class HabitStatus(IntEnum):
    """Enum for a Habit status."""

    NORMAL = 0
    ARCHIVED = 1


class HabitCheckinStatus(IntEnum):
    """Enum for a Habit check-in status."""

    UNCHECKED = 0
    UNCOMPLETED = 1
    COMPLETED = 2


class Habit:
    """Habit Class for TickTick."""

    def __init__(
        self,
        id: str,
        name: str,
        status: HabitStatus | None = HabitStatus.NORMAL,
        type: str | None = None,  # "Boolean" or "Real"
        goal: float = 1.0,
        step: float | None = None,
        unit: str | None = None,
        encouragement: str | None = None,
        sortOrder: int | None = None,
        sectionId: str | None = None,
        repeatRule: str | None = None,  # Example "RRULE:FREQ=DAILY;INTERVAL=1"
        totalCheckIns: int | None = None,
        archivedTime: str | None = None,
    ) -> None:
        """Intialize a Habit object."""
        self.id = id
        self.name = name
        self.status = status
        self.type = type
        self.goal = goal
        self.step = step
        self.unit = unit
        self.encouragement = encouragement
        self.sortOrder = sortOrder
        self.sectionId = sectionId
        self.repeatRule = repeatRule
        self.totalCheckIns = totalCheckIns
        self.archivedTime = archivedTime

    @property
    def is_archived(self) -> bool:
        """Return True if the habit is archived."""
        return self.status == HabitStatus.ARCHIVED or self.archivedTime is not None

    @staticmethod
    def from_dict(data: dict) -> "Habit":
        """Create a Habit instance from a dictionary."""
        status = data.get("status")
        return Habit(
            id=data["id"],
            name=data.get("name") if data.get("name") else "Unnamed Habit",
            status=HabitStatus(status) if status in iter(HabitStatus) else None,
            type=data.get("type"),
            goal=data.get("goal") or 1.0,
            step=data.get("step"),
            unit=data.get("unit"),
            encouragement=data.get("encouragement"),
            sortOrder=data.get("sortOrder"),
            sectionId=data.get("sectionId"),
            repeatRule=data.get("repeatRule"),
            totalCheckIns=data.get("totalCheckIns"),
            archivedTime=data.get("archivedTime"),
        )


class HabitCheckinData:
    """Single day check-in of a Habit."""

    def __init__(
        self,
        stamp: int,  # Date in YYYYMMDD format, example 20260407
        value: float = 0.0,
        goal: float = 1.0,
        status: HabitCheckinStatus | None = None,
        id: str | None = None,
        time: str | None = None,
        opTime: str | None = None,
    ) -> None:
        """Intialize a HabitCheckinData object."""
        self.stamp = stamp
        self.value = value
        self.goal = goal
        self.status = status
        self.id = id
        self.time = time
        self.opTime = opTime

    @property
    def is_completed(self) -> bool:
        """Return True if the check-in reached its goal."""
        if self.status is not None:
            return self.status == HabitCheckinStatus.COMPLETED
        return self.value >= self.goal

    @staticmethod
    def from_dict(data: dict) -> "HabitCheckinData":
        """Create a HabitCheckinData instance from a dictionary."""
        status = data.get("status")
        return HabitCheckinData(
            stamp=int(data["stamp"]),
            value=data.get("value") or 0.0,
            goal=data.get("goal") or 1.0,
            status=HabitCheckinStatus(status)
            if status in iter(HabitCheckinStatus)
            else None,
            id=data.get("id"),
            time=data.get("time"),
            opTime=data.get("opTime"),
        )

    def to_dict(self) -> dict:
        """Convert this check-in to a JSON-ready dict."""
        d = {
            "stamp": self.stamp,
            "value": self.value,
            "goal": self.goal,
            "status": int(self.status) if self.status is not None else None,
            "time": self.time,
            "opTime": self.opTime,
        }
        # Drop None values so TickTick accepts it
        return {k: v for k, v in d.items() if v is not None}


class HabitCheckin:
    """Check-ins of a Habit for a year."""

    def __init__(
        self,
        habitId: str | None,
        year: int | None,
        checkins: list[HabitCheckinData],
    ) -> None:
        """Intialize a HabitCheckin object."""
        self.habitId = habitId
        self.year = year
        self.checkins = checkins

    @staticmethod
    def from_dict(data: dict) -> "HabitCheckin":
        """Create a HabitCheckin instance from a dictionary."""
        return HabitCheckin(
            habitId=data.get("habitId"),
            year=data.get("year"),
            checkins=[
                HabitCheckinData.from_dict(checkin)
                for checkin in data.get("checkins") or []
            ],
        )
