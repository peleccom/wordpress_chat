import logging

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from es_website_chatbot.case_studies.documents_loader import convert_case_studies_to_bm25_documents
from es_website_chatbot.infrastructure.db.case_study_store import list_case_studies
from es_website_chatbot.infrastructure.db.database import Session
from es_website_chatbot.infrastructure.db.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)

AMOUNT_OF_DOCUMENTS_TO_RETURN = 4
VECTOR_SEARCH_TOP_K = 8
BM25_SEARCH_TOP_K = 8

_bm25_retriever: BM25Retriever | None = None


async def load_bm25_documents() -> list[Document]:
    async with Session() as session:
        case_study_items = await list_case_studies(session)
    return convert_case_studies_to_bm25_documents(case_study_items)


async def get_bm25_retriever() -> BM25Retriever | None:
    global _bm25_retriever
    if _bm25_retriever is not None:
        return _bm25_retriever

    documents = await load_bm25_documents()
    if not documents:
        logger.warning("No case study documents found for BM25 retriever")
        return None

    _bm25_retriever = BM25Retriever.from_documents(
        documents,
        k=BM25_SEARCH_TOP_K,
        bm25_params={"k1": 1.5, "b": 0.75},
    )
    logger.info("BM25 retriever initialized with %d documents", len(documents))
    return _bm25_retriever


async def retrieve(
    query: str,
    *,
    k: int = AMOUNT_OF_DOCUMENTS_TO_RETURN,
    filter_dict: dict | None = None,
) -> list[Document]:
    vectorstore = await get_vectorstore()
    search_kwargs: dict = {"k": VECTOR_SEARCH_TOP_K}
    if filter_dict:
        search_kwargs["filter"] = filter_dict
    vector_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )

    bm25_retriever = await get_bm25_retriever()
    retrievers: list = [vector_retriever]
    if bm25_retriever is not None:
        retrievers.append(bm25_retriever)

    if len(retrievers) == 1:
        return (await vector_retriever.ainvoke(query))[:k]

    ensemble = EnsembleRetriever(
        retrievers=retrievers,
        weights=[0.5, 0.5],
        id_key="url",
    )
    docs = await ensemble.ainvoke(query)
    return docs[:k]


async def init_bm25_retriever():
    await get_bm25_retriever()
