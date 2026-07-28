from enum import Enum


class TaskStatus(Enum):
    Waiting = 0
    Pending = 1
    Processing = 2
    Failed = 3
    Succeeded = 4
    Cancelling = 5
    Cancelled = 6