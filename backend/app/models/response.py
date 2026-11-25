from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from backend.app.core.utils import get_utc_now

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[DataT] = None
    is_demo_data: bool = True
    timestamp: datetime = Field(default_factory=get_utc_now)
