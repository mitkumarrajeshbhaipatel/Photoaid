from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.report import ReportCreate, ReportOut, ReportUpdate
from app.services.admin import create_report, get_report, update_report, list_reports

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/reports", response_model=ReportOut)
def submit_report(report: ReportCreate, db: Session = Depends(get_db)):
    return create_report(db, report)

@router.get("/reports/{report_id}", response_model=ReportOut)
def read_report(report_id: str, db: Session = Depends(get_db)):
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.put("/reports/{report_id}", response_model=ReportOut)
def review_report(report_id: str, report_update: ReportUpdate, db: Session = Depends(get_db)):
    updated = update_report(db, report_id, report_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")
    return updated

@router.get("/reports", response_model=list[ReportOut])
def get_all_reports(db: Session = Depends(get_db)):
    return list_reports(db)
