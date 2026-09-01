"""FROZEN API CONTRACTS — Day 1.

Frontend codes against these; backend fills them in. Changing a field here means telling
the whole team. This is what keeps four people from colliding on Day 6.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class Intent(str, Enum):
    FIND_STANDARD = "find_standard"
    CERTIFICATION_REQUIRED = "certification_required"
    PROCESS_HOWTO = "process_howto"
    FIND_FORM = "find_form"
    EXPLAIN_STANDARD = "explain_standard"
    ROADMAP = "roadmap"
    OUT_OF_SCOPE = "out_of_scope"


class Citation(BaseModel):
    """What the Evidence Panel renders. Every field must be real — never synthesised."""

    chunk_id: int
    document_title: str
    heading: str | None = None
    page: int | None = None
    snippet: str
    source_url: str
    score: float = 0.0


# --- Chat ---


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=2000)
    language: str = "en"  # "en" | "hi"


class ChatResponse(BaseModel):
    session_id: str
    message_id: int | None = None
    answer: str
    intent: Intent
    confidence: Confidence
    citations: list[Citation] = []
    next_steps: list[str] = []
    related_questions: list[str] = []
    warnings: list[str] = []


# --- Product scanner ---


class ExtractedProduct(BaseModel):
    """Never used for matching until the user has confirmed it."""

    product_name: str | None = None
    category: str | None = None
    material: str | None = None
    capacity: str | None = None
    dimensions: str | None = None
    brand: str | None = None
    isi_mark_present: bool | None = None
    is_number_on_label: str | None = None
    label_claims: list[str] = []
    intended_use: str | None = None
    raw_label_text: str = ""
    field_confidence: dict[str, float] = {}


class ScanResponse(BaseModel):
    scan_id: int
    extracted: ExtractedProduct
    warnings: list[str] = []


# --- Standard matching ---


class ProductInput(BaseModel):
    product_name: str = Field(min_length=1, max_length=300)
    category: str | None = None
    material: str | None = None
    capacity: str | None = None
    intended_use: str | None = None
    description: str | None = None


class StandardMatch(BaseModel):
    standard_id: int
    is_number: str
    title: str
    score: float
    why: list[str]                 # written by the LLM, explaining a ranking it did not create
    matched_attributes: list[str]  # computed by the scorer, not the LLM
    scheme: str | None = None
    is_mandatory: bool = False
    source_url: str


class MatchResponse(BaseModel):
    matches: list[StandardMatch]
    confidence: Confidence
    warnings: list[str] = []


# --- Forms ---


class FormResult(BaseModel):
    form_id: int
    form_code: str
    name: str
    purpose: str
    scheme: str | None = None
    stage: str | None = None
    official_url: str
    relevance: float = 0.0


class FormSearchRequest(BaseModel):
    query: str
    scheme: str | None = None
    stage: str | None = None


# --- Roadmap ---


class RoadmapStep(BaseModel):
    index: int
    title: str
    status: str  # done | current | pending | not_applicable
    explanation: str
    required_forms: list[FormResult] = []
    sources: list[Citation] = []
    next_action: str | None = None


class RoadmapResponse(BaseModel):
    roadmap_id: int
    scheme: str | None = None
    steps: list[RoadmapStep]
    confidence: Confidence
    warnings: list[str] = []


class FeedbackRequest(BaseModel):
    message_id: int | None = None
    is_helpful: bool
    reason: str | None = None
