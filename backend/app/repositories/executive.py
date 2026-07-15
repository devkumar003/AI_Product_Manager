from app.models.executive import CEOReport, CTOReport, COOReport
from app.repositories.base import BaseRepository


class CEOReportRepository(BaseRepository[CEOReport]):
    pass


class CTOReportRepository(BaseRepository[CTOReport]):
    pass


class COOReportRepository(BaseRepository[COOReport]):
    pass


ceo_report_repo = CEOReportRepository(CEOReport)
cto_report_repo = CTOReportRepository(CTOReport)
coo_report_repo = COOReportRepository(COOReport)
