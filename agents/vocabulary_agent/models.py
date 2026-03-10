from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class WordMemory(BaseModel):
    word: str
    phonetic: Optional[str] = None
    meaning_you_learned: str
    learn_scene: str
    learn_source: Optional[str] = None
    reference_type: Optional[str] = "web"
    reference_url: Optional[str] = None
    reference_title: Optional[str] = None
    reference_snippet: Optional[str] = None
    usage_old: Optional[str] = None
    usage_now: Optional[str] = None
    your_note: Optional[str] = None
    create_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    review_count: int = 0
    last_review_time: Optional[str] = None
    record_id: Optional[str] = None # Added for ID tracking

class WordQuery(BaseModel):
    query: str
    filter_scene: Optional[str] = None
    top_k: int = 3

class WordResponse(BaseModel):
    code: int
    msg: str
    record_id: Optional[str] = None
    create_time: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class RetrieveResponse(BaseModel):
    matches: List[Dict[str, Any]]
    ai_summary: str

class WordListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[WordMemory]

class ExtractRequest(BaseModel):
    text: Optional[str] = ""
    image: Optional[str] = None # Base64 encoded image string

class ExtractResponse(BaseModel):
    words: List[WordMemory]
