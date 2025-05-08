from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate
import uuid
import datetime

from app.schemas.notification import NotificationCreate
from app.services.notification import create_notification


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

    # ✅ Notify admin (or staff account)
    notification = NotificationCreate(
        user_id="admin",  # 🔁 Replace with actual admin user ID if available
        title="New Report Submitted",
        message=f"A user has reported another user for: {report.reason}",
        notification_type="admin"
    )
    create_notification(db, notification)

    return db_report

def get_report(db: Session, report_id: str):
    return db.query(Report).filter(Report.report_id == report_id).first()

def update_report(db: Session, report_id: str, report_update: ReportUpdate):
    # Fetch the report by ID
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        return None  # Return None if the report is not found
    
    # Update the fields from the ReportUpdate schema
    for key, value in report_update.dict(exclude_unset=True).items():
        setattr(report, key, value)  # Update only the fields that are provided
    
    # Set the reviewed_at timestamp
    if report_update.reviewed_at:
        report.reviewed_at = datetime.datetime.utcnow()  # Update reviewed_at field with current time
    
    db.commit()  # Commit changes to the database
    db.refresh(report)  # Refresh the report object to get the updated data

    # ✅ Notify reporter
    notification = NotificationCreate(
        user_id=report.reporter_id,
        title="Report Reviewed",
        message=f"Your report has been reviewed and marked as: {report.status}",
        notification_type="admin"
    )
    create_notification(db, notification)
    
    return report  # Return the updated report



def list_reports(db: Session):
    return db.query(Report).all()
