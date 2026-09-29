"""Running service scaffold; persistence and statistics remain unimplemented."""
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.running_record import RunningRecordUpdate


class RunningNotImplementedError(Exception):
    """An explicitly unfinished running feature."""


class RunningService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user_id = current_user.id

    def start(self):
        # Session persistence and request fields require an agreed contract.
        raise RunningNotImplementedError

    def end(self, session_id: str):
        # Save the record and update shoe totals in one transaction.
        raise RunningNotImplementedError

    def list_records(self, skip: int, limit: int):
        # Every query must be restricted to self.user_id.
        raise RunningNotImplementedError

    def get_record(self, record_id: int):
        # Filter by both record ID and self.user_id; absent records return 404.
        raise RunningNotImplementedError

    def update_record(self, record_id: int, request: RunningRecordUpdate):
        # Check record/shoe ownership; update old and new shoe totals atomically.
        raise RunningNotImplementedError

    def delete_record(self, record_id: int):
        # Delete only the owner's record and subtract shoe totals atomically.
        raise RunningNotImplementedError

    def summary(self):
        raise RunningNotImplementedError

    def weekly(self):
        # Agree on timezone, week boundaries and bucket keys first.
        raise RunningNotImplementedError

    def monthly(self):
        raise RunningNotImplementedError
