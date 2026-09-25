import enum


class UserRole(enum.StrEnum):
    CLIENT = "client"
    DRIVER = "driver"
    MANAGER = "manager"


class OrderStatus(enum.StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class RouteStatusEnum(enum.StrEnum):
    ASSIGNED = "assigned"
    LOADED = "loaded"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
