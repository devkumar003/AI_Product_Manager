from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.membership import Membership
from app.models.user import User
from app.schemas.executive import (
    CEOGenerationRequest,
    CEOReportResponse,
    COOGenerationRequest,
    COOReportResponse,
    CTOGenerationRequest,
    CTOReportResponse,
)
from app.services.executive.ceo import ceo_service
from app.services.executive.coo import coo_service
from app.services.executive.cto import cto_service

router = APIRouter()


def check_workspace_access(db: Session, user_id: UUID, workspace_id: UUID):
    """
    Checks workspace membership for the user.
    """
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user_id, Membership.workspace_id == workspace_id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access permissions for this workspace.",
        )


@router.post("/ceo/report", response_model=CEOReportResponse)
def generate_ceo_report(
    req: CEOGenerationRequest,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    try:
        return ceo_service.generate_ceo_report(
            db=db,
            workspace_id=workspace_id,
            product_idea=req.product_idea,
            target_industry=req.target_industry or "Tech",
            competitors=req.competitors,
            budget=req.budget or 100000.0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CEO report: {str(e)}",
        )


@router.get("/ceo/reports", response_model=list[CEOReportResponse])
def get_ceo_reports(
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return ceo_service.get_ceo_reports(db, workspace_id)


@router.post("/cto/report", response_model=CTOReportResponse)
def generate_cto_report(
    req: CTOGenerationRequest,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    try:
        return cto_service.generate_cto_report(
            db=db,
            workspace_id=workspace_id,
            product_spec=req.product_spec,
            preferred_cloud=req.preferred_cloud or "AWS",
            compliance_needs=req.compliance_needs,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CTO report: {str(e)}",
        )


@router.get("/cto/reports", response_model=list[CTOReportResponse])
def get_cto_reports(
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return cto_service.get_cto_reports(db, workspace_id)


@router.post("/coo/report", response_model=COOReportResponse)
def generate_coo_report(
    req: COOGenerationRequest,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    try:
        return coo_service.generate_coo_report(
            db=db,
            workspace_id=workspace_id,
            sprint_name=req.sprint_name,
            team_members=req.team_members,
            total_budget=req.total_budget or 50000.0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate COO report: {str(e)}",
        )


@router.get("/coo/reports", response_model=list[COOReportResponse])
def get_coo_reports(
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return coo_service.get_coo_reports(db, workspace_id)


@router.get("/export/pdf")
def export_pdf_report(
    report_id: UUID,
    report_type: str = Query(..., pattern="^(ceo|cto|coo)$"),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Simulated executive business report PDF exporter.
    """
    check_workspace_access(db, current_user.id, workspace_id)
    return {
        "success": True,
        "message": f"Successfully compiled and generated PDF export for {report_type} report: {report_id}.",
        "download_url": f"/api/v1/executive/download/pdf/{report_id}",
    }


@router.get("/export/ppt")
def export_ppt_report(
    report_id: UUID,
    report_type: str = Query(..., pattern="^(ceo|cto|coo)$"),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Simulated executive presentation PPT exporter.
    """
    check_workspace_access(db, current_user.id, workspace_id)
    return {
        "success": True,
        "message": f"Successfully compiled and generated PPT slides deck export for {report_type} report: {report_id}.",
        "download_url": f"/api/v1/executive/download/ppt/{report_id}",
    }


@router.get("/download/pdf/{report_id}")
def download_pdf_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Serve the generated PDF report content (simulated format).
    """
    import io

    from fastapi.responses import StreamingResponse

    from app.models.executive import CEOReport, COOReport, CTOReport

    ceo = db.query(CEOReport).filter(CEOReport.id == report_id).first()
    title = "Executive Advisor Report"
    content = "Executive Summary:\n\n"
    if ceo:
        title = ceo.title
        content += f"Active Idea: {ceo.portfolio_data.get('active_idea', '')}\n"
        content += (
            f"Target Vertical: {ceo.portfolio_data.get('target_vertical', '')}\n\n"
        )
        content += "SWOT Analysis:\n"
        content += f"{ceo.strategy_data.get('swot', {}).get('swot_markdown', '')}\n\n"
        content += "PESTLE Analysis:\n"
        content += (
            f"{ceo.strategy_data.get('pestle', {}).get('pestle_markdown', '')}\n\n"
        )
        content += "Financial Forecast:\n"
        content += (
            f"{ceo.financials.get('forecast', {}).get('forecast_markdown', '')}\n\n"
        )
    else:
        cto = db.query(CTOReport).filter(CTOReport.id == report_id).first()
        if cto:
            title = cto.title
            content += f"Tech Stack Spec: {cto.spec_data.get('product_spec', '')}\n"
            content += f"Preferred Cloud: {cto.architecture_data.get('preferred_cloud', '')}\n\n"
            content += "System Design:\n"
            content += f"{cto.architecture_data.get('design_markdown', '')}\n\n"
            content += "API Specifications:\n"
            content += f"{cto.spec_data.get('api_markdown', '')}\n\n"
        else:
            coo = db.query(COOReport).filter(COOReport.id == report_id).first()
            if coo:
                title = coo.title
                content += (
                    f"Sprint Name: {coo.operations_data.get('sprint_name', '')}\n"
                )
                content += "Sprint Backlog & Tasks:\n"
                content += f"{coo.operations_data.get('tasks_markdown', '')}\n\n"
                content += "Team Resources:\n"
                content += f"{coo.resource_data.get('team_members', '')}\n\n"
            else:
                raise HTTPException(status_code=404, detail="Report not found")

    file_data = "===========================================\n"
    file_data += f"{title.upper()}\n"
    file_data += "===========================================\n\n"
    file_data += content
    file_data += f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    buf = io.BytesIO(file_data.encode("utf-8"))
    filename = f"{title.replace(' ', '_').lower()}.txt"
    return StreamingResponse(
        buf,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/download/ppt/{report_id}")
def download_ppt_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Serve the generated PPT slides report content (simulated format).
    """
    import io

    from fastapi.responses import StreamingResponse

    from app.models.executive import CEOReport, COOReport, CTOReport

    ceo = db.query(CEOReport).filter(CEOReport.id == report_id).first()
    title = "Executive Presentation"
    slides = []
    if ceo:
        title = ceo.title
        slides = [
            (
                "Slide 1: Title",
                f"Executive Presentation: {ceo.title}\nActive Idea: {ceo.portfolio_data.get('active_idea', '')}",
            ),
            (
                "Slide 2: SWOT Analysis",
                f"{ceo.strategy_data.get('swot', {}).get('swot_markdown', '')}",
            ),
            (
                "Slide 3: PESTLE Analysis",
                f"{ceo.strategy_data.get('pestle', {}).get('pestle_markdown', '')}",
            ),
            (
                "Slide 4: Financial Forecast & Budget",
                f"Initial Budget: ${ceo.financials.get('initial_budget', 0)}\nForecast Details: {ceo.financials.get('forecast', {}).get('forecast_markdown', '')}",
            ),
        ]
    else:
        cto = db.query(CTOReport).filter(CTOReport.id == report_id).first()
        if cto:
            title = cto.title
            slides = [
                (
                    "Slide 1: Architecture Overview",
                    f"Technical Specifications for: {cto.title}",
                ),
                (
                    "Slide 2: System Design & Strategy",
                    f"{cto.architecture_data.get('design_markdown', '')}",
                ),
                (
                    "Slide 3: API & Schema Specs",
                    f"{cto.spec_data.get('api_markdown', '')}",
                ),
            ]
        else:
            coo = db.query(COOReport).filter(COOReport.id == report_id).first()
            if coo:
                title = coo.title
                slides = [
                    (
                        "Slide 1: Operations Backlog",
                        f"Project Backlog and Sprint for: {coo.title}",
                    ),
                    (
                        "Slide 2: Sprint Board Status",
                        f"{coo.operations_data.get('tasks_markdown', '')}",
                    ),
                    (
                        "Slide 3: Team Resource Allocation",
                        f"{coo.resource_data.get('team_members', '')}",
                    ),
                ]
            else:
                raise HTTPException(status_code=404, detail="Report not found")

    file_data = "===========================================\n"
    file_data += f"{title.upper()} - PRESENTATION DECK SLIDES\n"
    file_data += "===========================================\n\n"
    for idx, (slide_title, slide_content) in enumerate(slides, 1):
        file_data += f"--- SLIDE {idx}: {slide_title} ---\n"
        file_data += f"{slide_content}\n\n"

    buf = io.BytesIO(file_data.encode("utf-8"))
    filename = f"{title.replace(' ', '_').lower()}_presentation.txt"
    return StreamingResponse(
        buf,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
