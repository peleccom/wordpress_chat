from datetime import timedelta

from cachier import cachier

from es_website_chatbot.infrastructure.db.case_study_store import list_distinct_domains
from es_website_chatbot.infrastructure.db.database import Session


@cachier(stale_after=timedelta(hours=1), backend="memory")
async def list_available_case_study_domains() -> list[str]:
    async with Session() as session:
        return await list_distinct_domains(session)
