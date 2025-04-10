from sqlalchemy import Column, String, DateTime
from sqlalchemy.types import Text
from app.database import Base
import datetime

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, nullable=True)
    reporter_id = Column(String, nullable=False)
    target_user_id = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending | resolved
    action_taken = Column(String, nullable=True)  # ban | warn | ignore
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
