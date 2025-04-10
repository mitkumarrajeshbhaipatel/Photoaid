from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate
import uuid
import datetime

def create_report(db: Session, report: ReportCreate):
    db_report = Report(
        report_id=str(uuid.uuid4()),
        session_id=report.session_id,
        reporter_id=report.reporter_id,
        target_user_id=report.target_user_id,
        reason=report.reason,
        status="pending"
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_report(db: Session, report_id: str):
    return db.query(Report).filter(Report.report_id == report_id).first()

def update_report(db: Session, report_id: str, report_update: ReportUpdate):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        return None
    for key, value in report_update.dict(exclude_unset=True).items():
        setattr(report, key, value)
    report.reviewed_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(report)
    return report

def list_reports(db: Session):
    return db.query(Report).all()
