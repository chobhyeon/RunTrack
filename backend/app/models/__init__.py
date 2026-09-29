"""Import all models so SQLAlchemy can register tables and relationships."""

from app.models.user import User
from app.models.shoe import Shoe
from app.models.running_record import RunningRecord

__all__ = ["User", "Shoe", "RunningRecord"]
