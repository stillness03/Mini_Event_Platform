from app.schemas.events import UserContext


class EventPolicy:
    @staticmethod
    def _get_owner_id(event):
        return (
            event.get("owner_id")
            if isinstance(event, dict)
            else event.owner_id
        )

    @staticmethod
    def can_read(event, user: UserContext) -> bool:
        return True

    @staticmethod
    def can_modify(event, user: UserContext) -> bool:
        owner_id = (
            event.get("owner_id")
            if isinstance(event, dict)
            else event.owner_id
        )

        return (
            user.role == "admin"
            or str(owner_id) == user.owner_id
        )
