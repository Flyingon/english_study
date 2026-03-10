from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from agents.vocabulary_agent.models import WordMemory, WordQuery, WordResponse, RetrieveResponse, WordListResponse, ExtractRequest, ExtractResponse
from agents.vocabulary_agent.services.chroma_service import ChromaService
from agents.vocabulary_agent.services.llm_service import LLMService
from typing import Optional
from functools import lru_cache

router = APIRouter()


@lru_cache
def get_chroma_service() -> ChromaService:
    return ChromaService()


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()

@router.post("/word/add", response_model=WordResponse)
async def add_word(word_memory: WordMemory):
    try:
        chroma_service = await run_in_threadpool(get_chroma_service)
        # Simply pass the memory object; embedding is handled internally
        record_id = await run_in_threadpool(chroma_service.add_word, word_memory)
        
        return WordResponse(
            code=200,
            msg="Success",
            record_id=record_id,
            create_time=word_memory.create_time,
            data=word_memory.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/word/delete", response_model=WordResponse)
async def delete_word(record_id: str):
    try:
        chroma_service = await run_in_threadpool(get_chroma_service)
        # Check if exists first (optional, but good for UX)
        word_data = await run_in_threadpool(chroma_service.get_word, record_id)
        if not word_data:
            return WordResponse(code=404, msg="Word not found")
            
        await run_in_threadpool(chroma_service.delete_word, record_id)
        return WordResponse(code=200, msg="Successfully deleted", record_id=record_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/word/retrieve", response_model=RetrieveResponse)
async def retrieve_word(query: WordQuery):
    try:
        chroma_service = await run_in_threadpool(get_chroma_service)
        llm_service = await run_in_threadpool(get_llm_service)
        where_filter = None
        if query.filter_scene:
            where_filter = {"learn_scene": query.filter_scene}
            
        # Pass the raw query text
        results = await run_in_threadpool(
            chroma_service.query_words,
            query.query,
            query.top_k,
            where_filter
        )
        
        matches = []
        if results['metadatas'] and len(results['metadatas']) > 0:
            # results['metadatas'] is a list of lists (one list per query)
            raw_matches = results['metadatas'][0]
            raw_distances = results['distances'][0] if 'distances' in results and results['distances'] else []
            
            # Filter by distance (L2 distance: lower is better)
            # Threshold 1.5 is a reasonable starting point for all-MiniLM-L6-v2 in Chroma
            DISTANCE_THRESHOLD = 1.5
            
            for i, match in enumerate(raw_matches):
                if i < len(raw_distances):
                    dist = raw_distances[i]
                    if dist > DISTANCE_THRESHOLD:
                        continue # Skip irrelevant results
                    # Inject distance for frontend display
                    match['distance'] = round(dist, 4)
                matches.append(match)
            
        ai_summary = await run_in_threadpool(llm_service.generate_summary, query.query, matches)
        
        return RetrieveResponse(matches=matches, ai_summary=ai_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/word/detail", response_model=WordResponse)
async def get_word_detail(record_id: str):
    try:
        chroma_service = await run_in_threadpool(get_chroma_service)
        word_data = await run_in_threadpool(chroma_service.get_word, record_id)
        if not word_data:
            return WordResponse(code=404, msg="Word not found")
            
        return WordResponse(code=200, msg="Success", data=word_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/word/list", response_model=WordListResponse)
async def list_words(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    learn_scene: Optional[str] = None
):
    try:
        chroma_service = await run_in_threadpool(get_chroma_service)
        offset = (page - 1) * size
        where_filter = {}
        where_document = None

        if learn_scene:
            where_filter["learn_scene"] = learn_scene
        if keyword:
            where_document = {"$contains": keyword}
        
        if not where_filter:
            where_filter = None
            
        results = await run_in_threadpool(
            chroma_service.list_words,
            size,
            offset,
            where_filter,
            where_document
        )
        
        items = []
        if results['metadatas'] and results['ids']:
            for i, m in enumerate(results['metadatas']):
                item_dict = m.copy()
                item_dict['record_id'] = results['ids'][i]
                items.append(WordMemory(**item_dict))
                
        total = await run_in_threadpool(
            chroma_service.count_words,
            where_filter,
            where_document
        )
        
        return WordListResponse(total=total, page=page, size=size, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/word/extract", response_model=ExtractResponse)
async def extract_word_info(request: ExtractRequest):
    try:
        llm_service = await run_in_threadpool(get_llm_service)
        words = await run_in_threadpool(llm_service.extract_words_from_text, request.text or "", request.image)
        return ExtractResponse(words=words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
