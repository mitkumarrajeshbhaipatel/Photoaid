from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportBase(BaseModel):
    session_id: Optional[str]
    reporter_id: str
    target_user_id: str
    reason: str

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    status: Optional[str]
    action_taken: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]

class ReportOut(ReportBase):
    report_id: str
    status: str
    action_taken: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]

    class Config:
        orm_mode = True


class ReportResponse(BaseModel):
    report_id: str
    user_id: str
    reported_by: str
    reason: str
    status: Optional[str]
    action_taken: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]