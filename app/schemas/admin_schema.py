from pydantic import BaseModel
from datetime import datetime
from typing import List

class ReportResponse(BaseModel):
    user_id: str
    reported_by: str
    reason: str
    timestamp: datetime

    class Config:
        orm_mode = True

class AdminStatsResponse(BaseModel):
    total_users: int
    total_verified_users: int
    total_banned_users: int
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    total_reports: int
    unresolved_reports: int
    total_reviews: int
    average_trust_score: float
    match_requests_sent: int
    match_requests_received: int
    total_messages_sent: int

class BasicAdminActionResponse(BaseModel):
    user_id: str
    status: str
