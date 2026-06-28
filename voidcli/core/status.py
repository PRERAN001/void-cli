from enum import Enum


class TaskStatus(Enum):

    CREATED = "CREATED"

    PLANNING = "PLANNING"

    EXECUTING = "EXECUTING"

    WAITING_TOOL = "WAITING_TOOL"

    REVIEWING = "REVIEWING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"