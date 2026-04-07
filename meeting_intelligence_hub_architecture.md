# Meeting Intelligence Hub - Detailed System Architecture

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Layers](#architecture-layers)
4. [Component Design](#component-design)
5. [Technology Stack](#technology-stack)
6. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
7. [Database Schema](#database-schema)
8. [API Design](#api-design)
9. [AI/ML Pipeline](#aiml-pipeline)
10. [Frontend Architecture](#frontend-architecture)
11. [Security & Authentication](#security--authentication)
12. [Deployment Architecture](#deployment-architecture)
13. [Scalability Considerations](#scalability-considerations)

---

## 1. Executive Summary

**Meeting Intelligence Hub** is an AI-powered application that transforms raw meeting transcripts into actionable intelligence by automatically extracting decisions, action items, and enabling natural language queries across historical meeting data.

**Core Capabilities:**
- Automated extraction of decisions and action items from transcripts
- Structured presentation of meeting outcomes with export capabilities
- Contextual chatbot for querying meeting history with citations
- Multi-format transcript ingestion (.TXT, .VTT)

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Upload UI  │  │  Dashboard   │  │   Chat UI    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │File Processor│  │AI Orchestrator│ │Query Engine  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI/ML SERVICES LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │LLM Service   │  │Vector Search │  │NER Pipeline  │      │
│  │(Claude API)  │  │(Embeddings)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │Vector Store  │  │File Storage  │      │
│  │  (Metadata)  │  │  (Pinecone/  │  │   (S3/Local) │      │
│  │              │  │   Chroma)    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 System Context

**Primary Users:**
- Team members who attend meetings
- Project managers tracking action items
- Executives reviewing decisions
- Anyone needing to reference past discussions

**Key Use Cases:**
1. Upload meeting transcript → Extract insights
2. View all action items → Export for tracking
3. Ask questions → Get cited answers
4. Search decisions → Find context

---

## 3. Architecture Layers

### 3.1 Presentation Layer (Frontend)

**Purpose:** User interface for interaction with the system

**Components:**
- **Upload Portal:** Drag-and-drop interface for transcript files
- **Intelligence Dashboard:** Tabular view of decisions and action items
- **Query Interface:** Chat-style Q&A with context
- **Export Module:** Generate CSV/PDF reports

**Technology:** React.js with TypeScript

### 3.2 Application Layer (Backend)

**Purpose:** Business logic and orchestration

**Components:**
- **File Processing Service:** Validate, parse, and preprocess transcripts
- **AI Orchestration Service:** Coordinate LLM calls and processing
- **Query Engine:** Handle natural language queries
- **Export Service:** Generate reports in various formats

**Technology:** Python (FastAPI) or Node.js (Express)

### 3.3 AI/ML Services Layer

**Purpose:** Intelligence extraction and semantic search

**Components:**
- **LLM Service:** Claude API for extraction and Q&A
- **Embedding Service:** Generate vector representations
- **Entity Recognition:** Extract names, dates, tasks

### 3.4 Data Layer

**Purpose:** Persistent storage

**Components:**
- **Relational Database:** Meeting metadata, extracted items
- **Vector Database:** Semantic search capability
- **Object Storage:** Raw transcript files

---

## 4. Component Design

### 4.1 File Processor Component

**Responsibility:** Ingest and preprocess transcript files

**Functions:**
```python
class FileProcessor:
    def validate_file(file: UploadFile) -> ValidationResult
    def parse_txt(file_path: str) -> ParsedTranscript
    def parse_vtt(file_path: str) -> ParsedTranscript
    def extract_metadata(content: str) -> TranscriptMetadata
    def chunk_transcript(content: str, chunk_size: int) -> List[Chunk]
```

**Input Validation:**
- File type: .txt, .vtt only
- File size: Max 50MB
- Encoding: UTF-8
- Content: Non-empty, valid format

**Output:**
```json
{
  "transcript_id": "uuid",
  "original_filename": "weekly_standup_2026-04-01.txt",
  "file_type": "txt",
  "content": "raw transcript text...",
  "chunks": ["chunk1...", "chunk2..."],
  "metadata": {
    "upload_date": "2026-04-07T10:30:00Z",
    "speaker_count": 5,
    "word_count": 3421,
    "duration_estimate": "45 minutes"
  }
}
```

### 4.2 AI Orchestrator Component

**Responsibility:** Coordinate AI-powered extraction and analysis

**Core Functions:**

#### 4.2.1 Decision Extractor
```python
def extract_decisions(transcript: str) -> List[Decision]:
    """
    Uses Claude API to identify all decisions made during the meeting.
    
    Prompt Strategy:
    - Identify statements indicating consensus or finalization
    - Look for phrases like "we decided", "let's go with", "agreed on"
    - Ignore hypothetical discussions
    
    Returns structured decision objects with context
    """
    
    prompt = """
    Analyze this meeting transcript and extract all DECISIONS made.
    A decision is a concrete conclusion or agreement the team reached.
    
    For each decision, provide:
    1. The decision statement (what was decided)
    2. The reasoning/context (why this was decided)
    3. The timestamp/section where it appears
    
    Format as JSON array.
    
    Transcript:
    {transcript}
    """
```

**Decision Object Schema:**
```json
{
  "id": "decision_uuid",
  "statement": "We will use React for the frontend",
  "reasoning": "Team has more React experience, faster development",
  "context_snippet": "After discussing Vue vs React...",
  "confidence_score": 0.95,
  "section_index": 2,
  "mentioned_by": ["Sarah", "Mike"]
}
```

#### 4.2.2 Action Item Extractor
```python
def extract_action_items(transcript: str) -> List[ActionItem]:
    """
    Extract all tasks assigned to specific individuals.
    
    Identification Criteria:
    - Explicit assignments: "John, can you..."
    - Volunteer statements: "I'll handle..."
    - Task language: "prepare", "create", "send", "review"
    - Deadlines: "by Friday", "next week", "before the launch"
    
    Returns structured action items with WHO/WHAT/WHEN
    """
    
    prompt = """
    Extract all ACTION ITEMS from this meeting transcript.
    
    For each action item, identify:
    1. WHO is responsible (person's name)
    2. WHAT they need to do (specific task)
    3. WHEN it's due (deadline or timeframe)
    4. CONTEXT (why this task matters)
    
    If any field is unclear, mark it as "Not Specified"
    
    Return as JSON array.
    
    Transcript:
    {transcript}
    """
```

**Action Item Object Schema:**
```json
{
  "id": "action_uuid",
  "assigned_to": "John Smith",
  "task_description": "Prepare Q2 budget proposal with revised projections",
  "deadline": "2026-04-15",
  "deadline_raw": "by next Friday",
  "priority": "high",
  "status": "pending",
  "context": "Needed for board meeting on April 20",
  "section_index": 5,
  "confidence_score": 0.88
}
```

### 4.3 Query Engine Component

**Responsibility:** Handle natural language questions with citations

**Architecture:**

```
User Question
     │
     ▼
┌─────────────────────┐
│  Query Processor    │
│  - Classify intent  │
│  - Extract entities │
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Retrieval Engine   │
│  - Vector search    │
│  - Filter by date   │
│  - Rank by relevance│
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Answer Generator   │
│  - LLM synthesis    │
│  - Citation linking │
│  - Confidence score │
└─────────────────────┘
     │
     ▼
  Answer + Sources
```

**Implementation:**
```python
class QueryEngine:
    def process_query(self, question: str, user_filters: dict) -> QueryResult:
        # Step 1: Generate embedding for question
        question_embedding = self.embedding_service.embed(question)
        
        # Step 2: Vector search across transcript chunks
        relevant_chunks = self.vector_store.similarity_search(
            embedding=question_embedding,
            top_k=5,
            filters=user_filters  # e.g., date_range, meeting_type
        )
        
        # Step 3: Use Claude to synthesize answer
        answer = self.llm_service.generate_answer(
            question=question,
            context_chunks=relevant_chunks,
            instruction="Answer based ONLY on provided context. Always cite sources."
        )
        
        # Step 4: Format with citations
        return self.format_with_citations(answer, relevant_chunks)
```

**Citation Format:**
```json
{
  "answer": "The API launch was delayed because the security audit revealed...",
  "citations": [
    {
      "meeting_id": "meeting_uuid_123",
      "meeting_title": "Product Roadmap Review - March 2026",
      "meeting_date": "2026-03-15",
      "chunk_text": "...security audit revealed three critical vulnerabilities...",
      "relevance_score": 0.92,
      "speakers": ["Security Lead", "CTO"]
    }
  ],
  "confidence": 0.85,
  "answer_type": "factual"  // factual, opinion, or uncertain
}
```

### 4.4 Export Service Component

**Formats Supported:**
1. **CSV Export** - Action items in spreadsheet format
2. **PDF Report** - Formatted meeting summary
3. **JSON** - Raw structured data

**PDF Template Structure:**
```
┌────────────────────────────────────────┐
│  MEETING INTELLIGENCE REPORT           │
│  Meeting: Weekly Standup - April 1     │
│  Date: 2026-04-01                      │
├────────────────────────────────────────┤
│  DECISIONS (3)                         │
│  1. [Decision statement]               │
│     Context: [reasoning]               │
│                                        │
│  ACTION ITEMS (7)                      │
│  ┌─────────┬────────┬──────────┐      │
│  │ Owner   │ Task   │ Deadline │      │
│  ├─────────┼────────┼──────────┤      │
│  │ John    │ ...    │ Apr 15   │      │
│  └─────────┴────────┴──────────┘      │
└────────────────────────────────────────┘
```

---

## 5. Technology Stack

### 5.1 Recommended Stack

#### Frontend
- **Framework:** React 18 with TypeScript
- **State Management:** Zustand or Redux Toolkit
- **UI Library:** Material-UI (MUI) or shadcn/ui
- **File Upload:** react-dropzone
- **Charts/Tables:** TanStack Table (react-table)
- **Chat Interface:** Custom component with streaming support

#### Backend
- **Framework:** FastAPI (Python) or Express (Node.js)
- **Language:** Python 3.11+ or Node.js 18+
- **API Documentation:** OpenAPI/Swagger (auto-generated by FastAPI)
- **Validation:** Pydantic (Python) or Zod (TypeScript)

#### AI/ML Services
- **Audio STT & Diarization:** Deepgram API (Nova-2 model, Option A)
- **LLM:** Anthropic Claude API (Claude Sonnet 4)
- **Embeddings:** 
  - Option 1: OpenAI text-embedding-3-small
  - Option 2: Sentence Transformers (all-MiniLM-L6-v2) - free, local
- **Vector Store:**
  - Option 1: Pinecone (hosted, easy)
  - Option 2: Chroma (local, free)
  - Option 3: pgvector (PostgreSQL extension)

#### Databases
- **Primary DB:** PostgreSQL 15+
- **Vector DB:** Chroma or Pinecone
- **Caching:** Redis (optional, for performance)

#### File Storage
- **Development:** Local filesystem
- **Production:** AWS S3 or MinIO (self-hosted S3-compatible)

#### Deployment
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Docker Compose (simple) or Kubernetes (scalable)
- **Hosting:** 
  - Frontend: Vercel/Netlify
  - Backend: Railway/Render/AWS
  - Database: Supabase/Render/AWS RDS

### 5.2 Alternative Stack (Cost-Optimized)

For maximum cost efficiency:
- **LLM:** Claude API with caching
- **Embeddings:** Sentence Transformers (free, run locally)
- **Vector DB:** Chroma (free, embedded mode)
- **Database:** PostgreSQL with pgvector extension (one DB for all)
- **Deployment:** Single VPS (Hetzner/DigitalOcean) with Docker Compose

---

## 6. Data Flow & Processing Pipeline

### 6.1 Audio Upload Flow (Deepgram Pipeline)

```
┌────────────────────────┐
│ 1. User Uploads Audio  │
│    (.mp3, .wav, .mp4)  │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 2. Audio Pipeline      │
│  a. Ingestion/Validate │
│  b. Deepgram API (STT) │
│  c. Diarization (Who)  │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 3. Generated Transcript│
│    (Auto-creates Text) │
└──────┬─────────────────┘
       │
       ▼
      (Goes to Step 6.2)
```

### 6.2 Transcript Upload Flow

```
┌──────────────┐
│ User uploads │
│ transcript   │
└──────┬───────┘
       │
       ▼
┌────────────────────────┐
│ 1. File Validation     │
│    - Format check      │
│    - Size check        │
│    - Virus scan        │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 2. File Storage        │
│    - Save to S3/local  │
│    - Generate UUID     │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 3. Parsing             │
│    - Extract text      │
│    - Detect speakers   │
│    - Segment chunks    │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 4. Embedding           │
│    - Generate vectors  │
│    - Store in VectorDB │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 5. AI Extraction       │
│    - Extract decisions │
│    - Extract actions   │
│    - Store results     │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ 6. Notification        │
│    - Update UI         │
│    - Show results      │
└────────────────────────┘
```

### 6.2 Query Processing Flow

```
User Question: "Why was the API launch delayed?"
       │
       ▼
┌────────────────────────┐
│ Embedding Generation   │
│ [0.23, -0.45, ...]     │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ Vector Search          │
│ Top 5 relevant chunks: │
│ 1. "...security audit..│
│ 2. "...API testing...  │
│ 3. "...timeline...     │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ Claude API Call        │
│ Prompt:                │
│ "Based on these chunks │
│  answer: [question]"   │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ Response Formatting    │
│ - Add citations        │
│ - Link to meetings     │
│ - Calculate confidence │
└──────┬─────────────────┘
       │
       ▼
   Display Answer
```

---

## 7. Database Schema

### 7.1 PostgreSQL Schema

```sql
-- Meetings Table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    meeting_date DATE NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    original_filename VARCHAR(255),
    file_type VARCHAR(10),
    file_path TEXT,
    file_size_bytes INTEGER,
    processing_status VARCHAR(50) DEFAULT 'pending',
    word_count INTEGER,
    speaker_count INTEGER,
    duration_estimate VARCHAR(50),
    created_by UUID,
    tags TEXT[],
    metadata JSONB
);

-- Transcript Chunks (for retrieval)
CREATE TABLE transcript_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT NOT NULL,
    speaker VARCHAR(255),
    timestamp_start VARCHAR(50),
    timestamp_end VARCHAR(50),
    embedding_id VARCHAR(255),  -- Reference to vector DB
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decisions Table
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    statement TEXT NOT NULL,
    reasoning TEXT,
    context_snippet TEXT,
    section_index INTEGER,
    confidence_score DECIMAL(3,2),
    mentioned_by TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Action Items Table
CREATE TABLE action_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    assigned_to VARCHAR(255) NOT NULL,
    task_description TEXT NOT NULL,
    deadline DATE,
    deadline_raw TEXT,
    priority VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pending',
    context TEXT,
    section_index INTEGER,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

-- Query History (for analytics)
CREATE TABLE query_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT,
    citations JSONB,
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id UUID
);

-- Indexes for performance
CREATE INDEX idx_meetings_date ON meetings(meeting_date DESC);
CREATE INDEX idx_action_items_assignee ON action_items(assigned_to);
CREATE INDEX idx_action_items_status ON action_items(status);
CREATE INDEX idx_action_items_deadline ON action_items(deadline);
CREATE INDEX idx_transcript_chunks_meeting ON transcript_chunks(meeting_id);
```

### 7.2 Vector Database Schema (Chroma/Pinecone)

```python
# Vector storage structure
{
    "id": "chunk_uuid",
    "embedding": [0.23, -0.45, 0.67, ...],  # 384 or 1536 dimensions
    "metadata": {
        "meeting_id": "uuid",
        "meeting_title": "Weekly Standup",
        "meeting_date": "2026-04-01",
        "chunk_index": 3,
        "speaker": "John",
        "content": "raw text of chunk",
        "type": "transcript_chunk"  # or "decision" or "action_item"
    }
}
```

---

## 8. API Design

### 8.1 RESTful Endpoints

#### File Upload
```
POST /api/v1/transcripts/upload
Content-Type: multipart/form-data

Request:
- file: File (required)
- title: string (optional)
- meeting_date: date (optional)
- tags: string[] (optional)

Response:
{
  "transcript_id": "uuid",
  "status": "processing",
  "message": "File uploaded successfully. Processing started."
}
```

#### Get Processing Status
```
GET /api/v1/transcripts/{transcript_id}/status

Response:
{
  "transcript_id": "uuid",
  "status": "completed",  // pending, processing, completed, failed
  "progress_percentage": 100,
  "decisions_count": 3,
  "action_items_count": 7,
  "error_message": null
}
```

#### Get Decisions
```
GET /api/v1/meetings/{meeting_id}/decisions

Response:
{
  "meeting_id": "uuid",
  "meeting_title": "Product Review",
  "decisions": [
    {
      "id": "decision_uuid",
      "statement": "We will launch the beta in Q2",
      "reasoning": "Market conditions are favorable",
      "confidence": 0.95,
      "mentioned_by": ["CEO", "Product Lead"]
    }
  ]
}
```

#### Get Action Items
```
GET /api/v1/action-items?status=pending&assigned_to=John

Query Parameters:
- status: pending|completed|all
- assigned_to: string (filter by person)
- deadline_before: date
- deadline_after: date
- meeting_id: uuid

Response:
{
  "action_items": [
    {
      "id": "action_uuid",
      "assigned_to": "John Smith",
      "task": "Prepare budget proposal",
      "deadline": "2026-04-15",
      "priority": "high",
      "status": "pending",
      "meeting": {
        "id": "meeting_uuid",
        "title": "Q2 Planning",
        "date": "2026-04-01"
      }
    }
  ],
  "total_count": 15,
  "page": 1
}
```

#### Query Chatbot
```
POST /api/v1/query

Request:
{
  "question": "Why did we delay the API launch?",
  "filters": {
    "date_range": {
      "start": "2026-03-01",
      "end": "2026-04-01"
    },
    "meeting_ids": ["uuid1", "uuid2"]
  }
}

Response:
{
  "answer": "The API launch was delayed because...",
  "citations": [
    {
      "meeting_id": "uuid",
      "meeting_title": "Product Review",
      "meeting_date": "2026-03-15",
      "excerpt": "...security audit revealed...",
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.85
}
```

#### Export Data
```
POST /api/v1/export

Request:
{
  "format": "pdf",  // pdf, csv, json
  "type": "action_items",  // action_items, decisions, full_report
  "filters": {
    "meeting_ids": ["uuid1"],
    "date_range": {...}
  }
}

Response:
{
  "download_url": "/downloads/report_uuid.pdf",
  "expires_at": "2026-04-08T10:30:00Z"
}
```

### 8.2 WebSocket for Real-time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://api.example.com/ws/processing/{transcript_id}');

// Receive real-time updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  /*
  {
    "event": "processing_progress",
    "transcript_id": "uuid",
    "stage": "extracting_decisions",  // parsing, embedding, extracting_decisions, extracting_actions
    "progress": 45,
    "message": "Analyzing meeting content..."
  }
  */
};
```

---

## 9. AI/ML Pipeline

### 9.1 Claude API Integration

#### Prompt Engineering Strategy

**Decision Extraction Prompt:**
```python
DECISION_EXTRACTION_PROMPT = """
You are analyzing a meeting transcript to extract DECISIONS.

A DECISION is:
- A concrete conclusion or agreement the team reached
- Something they committed to doing or changing
- A settled question where alternatives were considered

NOT a decision:
- Open questions or discussions
- Hypothetical scenarios
- Individual opinions without consensus

Transcript:
{transcript}

Extract all decisions in this JSON format:
[
  {
    "statement": "Clear, concise decision statement",
    "reasoning": "Why this decision was made",
    "context": "Relevant surrounding discussion",
    "confidence": 0.0-1.0,
    "mentioned_by": ["Speaker names"]
  }
]

Only include items you are confident are actual decisions.
"""
```

**Action Item Extraction Prompt:**
```python
ACTION_ITEM_EXTRACTION_PROMPT = """
You are analyzing a meeting transcript to extract ACTION ITEMS.

An ACTION ITEM is:
- A specific task assigned to a person
- Has a clear deliverable
- May or may not have an explicit deadline

Extract these elements:
1. WHO: Person's name (if not specified, say "Not Assigned")
2. WHAT: Specific task description
3. WHEN: Deadline or timeframe (if mentioned)
4. WHY: Context or reason for the task

Transcript:
{transcript}

Return JSON array:
[
  {
    "assigned_to": "Full name",
    "task": "Specific task description",
    "deadline": "YYYY-MM-DD or null",
    "deadline_raw": "Original text like 'by Friday'",
    "context": "Why this task matters",
    "confidence": 0.0-1.0
  }
]

Be conservative - only extract clear, actionable items.
"""
```

**Query Answering Prompt:**
```python
QUERY_ANSWER_PROMPT = """
You are a helpful assistant that answers questions about meeting transcripts.

Question: {question}

Relevant transcript excerpts:
{context_chunks}

Instructions:
1. Answer ONLY based on the provided excerpts
2. If the answer isn't in the excerpts, say "I don't have enough information"
3. Always cite which meeting and which part you're referencing
4. Be concise but complete
5. If there are conflicting statements, mention both

Format your answer like:
"[Your answer here]

Sources:
- Meeting: [Title] on [Date] - [Brief excerpt]"
"""
```

### 9.2 Embedding Strategy

**Purpose:** Enable semantic search across all transcript content

**Implementation:**
```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        # Using all-MiniLM-L6-v2: 384 dimensions, fast, good quality
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed_chunk(self, text: str) -> List[float]:
        """Generate embedding for a single text chunk"""
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding for efficiency"""
        return self.model.encode(texts, batch_size=32).tolist()
```

**Chunking Strategy:**
```python
def chunk_transcript(transcript: str, chunk_size: int = 500) -> List[str]:
    """
    Smart chunking that preserves context
    
    Strategy:
    1. Split by speaker changes when possible
    2. Keep chunks around 500 words (2-3 paragraphs)
    3. Overlap chunks by 50 words for context preservation
    """
    words = transcript.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - 50):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks
```

### 9.3 Vector Search Pipeline

```python
class VectorSearchEngine:
    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict = None
    ) -> List[SearchResult]:
        """
        Find most relevant transcript chunks for a query
        
        Process:
        1. Embed the query
        2. Search vector DB
        3. Apply metadata filters
        4. Re-rank by relevance
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_chunk(query)
        
        # Search vector database
        results = self.vector_db.search(
            vector=query_embedding,
            top_k=top_k * 2,  # Get more than needed
            filter=filters  # e.g., date_range, meeting_type
        )
        
        # Re-rank using cross-encoder for better precision
        reranked = self.rerank(query, results)
        
        return reranked[:top_k]
```

---

## 10. Frontend Architecture

### 10.1 Component Structure

```
src/
├── components/
│   ├── Upload/
│   │   ├── DropZone.tsx
│   │   ├── FileValidator.tsx
│   │   ├── UploadProgress.tsx
│   │   └── ProcessingStatus.tsx
│   │
│   ├── Dashboard/
│   │   ├── MeetingsList.tsx
│   │   ├── DecisionsTable.tsx
│   │   ├── ActionItemsTable.tsx
│   │   ├── FilterBar.tsx
│   │   └── ExportButton.tsx
│   │
│   ├── Chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   ├── QueryInput.tsx
│   │   ├── CitationCard.tsx
│   │   └── SuggestedQuestions.tsx
│   │
│   └── Common/
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       └── Toast.tsx
│
├── pages/
│   ├── HomePage.tsx
│   ├── UploadPage.tsx
│   ├── DashboardPage.tsx
│   ├── ChatPage.tsx
│   └── MeetingDetailPage.tsx
│
├── services/
│   ├── api.ts
│   ├── websocket.ts
│   └── export.ts
│
├── store/
│   ├── meetingsStore.ts
│   ├── actionItemsStore.ts
│   └── chatStore.ts
│
└── types/
    ├── meeting.ts
    ├── actionItem.ts
    └── query.ts
```

### 10.2 Key UI Components

#### Upload Component
```typescript
// components/Upload/DropZone.tsx
import { useDropzone } from 'react-dropzone';

interface DropZoneProps {
  onFileAccepted: (file: File) => void;
}

const DropZone: React.FC<DropZoneProps> = ({ onFileAccepted }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'text/vtt': ['.vtt']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileAccepted(acceptedFiles[0]);
      }
    }
  });

  return (
    <div {...getRootProps()} className="dropzone">
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Drop the transcript here...</p>
      ) : (
        <p>Drag & drop a transcript, or click to select</p>
      )}
    </div>
  );
};
```

#### Action Items Table
```typescript
// components/Dashboard/ActionItemsTable.tsx
import { DataGrid, GridColDef } from '@mui/x-data-grid';

interface ActionItemsTableProps {
  actionItems: ActionItem[];
  onStatusChange: (id: string, newStatus: string) => void;
}

const ActionItemsTable: React.FC<ActionItemsTableProps> = ({
  actionItems,
  onStatusChange
}) => {
  const columns: GridColDef[] = [
    { field: 'assigned_to', headerName: 'Assigned To', width: 150 },
    { field: 'task', headerName: 'Task', width: 300, flex: 1 },
    { field: 'deadline', headerName: 'Deadline', width: 120 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <select
          value={params.value}
          onChange={(e) => onStatusChange(params.id, e.target.value)}
        >
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      )
    },
    {
      field: 'meeting',
      headerName: 'Source',
      width: 200,
      renderCell: (params) => params.value.title
    }
  ];

  return (
    <DataGrid
      rows={actionItems}
      columns={columns}
      pageSize={10}
      checkboxSelection
      disableSelectionOnClick
    />
  );
};
```

#### Chat Interface
```typescript
// components/Chat/ChatInterface.tsx
const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.query({ question: input });
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        confidence: response.confidence
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <MessageList messages={messages} />
      <QueryInput
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        loading={loading}
      />
    </div>
  );
};
```

### 10.3 State Management

```typescript
// store/actionItemsStore.ts
import create from 'zustand';

interface ActionItemsStore {
  actionItems: ActionItem[];
  loading: boolean;
  filters: Filters;
  
  fetchActionItems: (filters?: Filters) => Promise<void>;
  updateStatus: (id: string, status: string) => Promise<void>;
  setFilters: (filters: Filters) => void;
}

export const useActionItemsStore = create<ActionItemsStore>((set, get) => ({
  actionItems: [],
  loading: false,
  filters: {},
  
  fetchActionItems: async (filters) => {
    set({ loading: true });
    try {
      const items = await api.getActionItems(filters || get().filters);
      set({ actionItems: items, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },
  
  updateStatus: async (id, status) => {
    await api.updateActionItemStatus(id, status);
    await get().fetchActionItems();
  },
  
  setFilters: (filters) => {
    set({ filters });
    get().fetchActionItems();
  }
}));
```

---

## 11. Security & Authentication

### 11.1 Authentication Strategy

**Option 1: JWT-based Auth**
```python
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user = await get_user_by_id(payload["user_id"])
    return user
```

**Option 2: Session-based Auth**
- Use secure HTTP-only cookies
- Redis for session storage
- CSRF protection

### 11.2 Authorization Levels

```python
class UserRole(Enum):
    VIEWER = "viewer"      # Can view meetings and query
    CONTRIBUTOR = "contributor"  # Can upload transcripts
    ADMIN = "admin"        # Can manage all data

class PermissionChecker:
    @staticmethod
    def can_upload(user: User) -> bool:
        return user.role in [UserRole.CONTRIBUTOR, UserRole.ADMIN]
    
    @staticmethod
    def can_delete_meeting(user: User, meeting: Meeting) -> bool:
        return user.role == UserRole.ADMIN or meeting.created_by == user.id
```

### 11.3 Security Best Practices

1. **File Upload Security:**
   - Validate file types using magic numbers, not just extensions
   - Scan for malware
   - Store in isolated directory
   - Generate random filenames

2. **API Security:**
   - Rate limiting (e.g., 100 requests/hour per user)
   - Input validation and sanitization
   - SQL injection prevention (use parameterized queries)
   - CORS configuration

3. **Data Protection:**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Sanitize data before sending to LLM
   - Implement data retention policies

```python
# Rate limiting example
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/query")
@limiter.limit("30/minute")
async def query_endpoint(request: Request, query: QueryRequest):
    # Process query
    pass
```

### 11.4 Data Privacy & PII Scrubbing Pipeline
To ensure enterprise compliance (SOC 2, GDPR) and prevent sensitive data leakage to third-party LLMs, the system implements a local sanitization layer.

* **Detection Engine:** Utilizes Microsoft Presidio for local Named Entity Recognition (NER) combined with regex patterns to identify names, financials, and proprietary terms.
* **Tokenization & Re-hydration:** 
  1. Sensitive entities are replaced with deterministic tokens (e.g., `<PERSON_1>`) before API transmission.
  2. A temporary mapping is stored securely in the local context (or Redis cache).
  3. Upon receiving the LLM's response, the backend "re-hydrates" the payload by swapping the tokens back to their original values before serving the data to the frontend.

---

## 12. Deployment Architecture

### 12.1 Development Setup (Docker Compose)

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/meetings_db
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - CHROMA_HOST=chromadb
    depends_on:
      - postgres
      - chromadb
    volumes:
      - ./uploads:/app/uploads

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=meetings_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  chroma_data:
```

### 12.2 Production Deployment

**Architecture:**
```
                     ┌─────────────┐
                     │   CDN/Edge  │
                     │   (Cloudflare)
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │   Frontend  │
                     │  (Vercel)   │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │ API Gateway │
                     │ (Load Bal.) │
                     └──────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ Backend │         │ Backend │         │ Backend │
   │ Instance│         │ Instance│         │ Instance│
   └────┬────┘         └────┬────┘         └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         ┌────▼────┐                 ┌────▼────┐
         │PostgreSQL                 │ Chroma  │
         │  (RDS)  │                 │ (Docker)│
         └─────────┘                 └─────────┘
```

**Infrastructure as Code (Terraform example):**
```hcl
# terraform/main.tf
resource "aws_ecs_cluster" "meeting_intelligence" {
  name = "meeting-intelligence-cluster"
}

resource "aws_ecs_service" "backend" {
  name            = "backend-service"
  cluster         = aws_ecs_cluster.meeting_intelligence.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 3
  
  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
}
```

### 12.3 Environment Variables

```bash
# .env.production
# Database
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/meetings_db
VECTOR_DB_URL=http://chroma.internal:8000

# AI Services
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Storage
S3_BUCKET=meeting-transcripts-prod
AWS_REGION=us-east-1

# Security
JWT_SECRET=your-secret-key
CORS_ORIGINS=https://app.example.com

# Monitoring
SENTRY_DSN=https://...
```

---

## 13. Scalability Considerations

### 13.1 Performance Optimization

**1. Caching Strategy:**
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=1000)
def get_embeddings(text: str) -> List[float]:
    """Cache embeddings to avoid recomputation"""
    cache_key = f"embedding:{hash(text)}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    embedding = embedding_service.embed(text)
    redis_client.setex(cache_key, 3600, json.dumps(embedding))
    return embedding
```

**2. Async Processing:**
```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_transcript_async(transcript_id: str):
    """Process transcript in background"""
    transcript = get_transcript(transcript_id)
    
    # Extract decisions and actions in parallel
    decisions_future = extract_decisions.delay(transcript.content)
    actions_future = extract_action_items.delay(transcript.content)
    
    # Generate embeddings
    embeddings_future = generate_embeddings.delay(transcript.chunks)
    
    # Wait for all tasks
    decisions = decisions_future.get()
    actions = actions_future.get()
    embeddings = embeddings_future.get()
    
    # Store results
    save_results(transcript_id, decisions, actions, embeddings)
```

**3. Database Optimization:**
```sql
-- Partitioning for large tables
CREATE TABLE meetings_2026 PARTITION OF meetings
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Materialized views for common queries
CREATE MATERIALIZED VIEW pending_action_items AS
SELECT ai.*, m.title as meeting_title, m.meeting_date
FROM action_items ai
JOIN meetings m ON ai.meeting_id = m.id
WHERE ai.status = 'pending'
ORDER BY ai.deadline ASC;

-- Refresh periodically
REFRESH MATERIALIZED VIEW pending_action_items;
```

### 13.2 Scaling Dimensions

**Horizontal Scaling:**
- Multiple backend instances behind load balancer
- Stateless API design
- Shared Redis cache
- Database read replicas

**Vertical Scaling:**
- Increase instance size for AI workloads
- Use GPU instances for embeddings (if using large models)
- Optimize vector search with HNSW indices

**Batch Processing:**
```python
def process_batch_of_transcripts(transcript_ids: List[str]):
    """Process multiple transcripts efficiently"""
    
    # Load all transcripts
    transcripts = load_transcripts(transcript_ids)
    
    # Batch embedding generation (much faster)
    all_chunks = [chunk for t in transcripts for chunk in t.chunks]
    embeddings = embedding_service.embed_batch(all_chunks)
    
    # Batch LLM calls with Claude's batch API
    extraction_results = claude_batch_api.extract_all(transcripts)
    
    # Bulk insert to database
    bulk_insert_results(extraction_results)
```

### 13.3 Cost Optimization

**LLM Cost Management:**
```python
# Use prompt caching for repeated system prompts
def extract_with_caching(transcript: str) -> dict:
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": EXTRACTION_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}  # Cache this
            }
        ],
        messages=[{"role": "user", "content": transcript}]
    )
    return response

# Estimate costs before processing
def estimate_processing_cost(file_size_kb: int) -> float:
    """Rough cost estimation"""
    tokens_estimate = file_size_kb * 250  # ~250 tokens per KB
    input_cost = (tokens_estimate / 1_000_000) * 3.00  # $3 per MTok
    output_cost = (tokens_estimate * 0.2 / 1_000_000) * 15.00  # $15 per MTok
    return input_cost + output_cost
```

**Infrastructure Costs:**
- Use serverless for low-traffic periods (AWS Lambda, Cloud Run)
- Spot instances for batch processing
- S3 Glacier for old transcripts (archive tier)
- Chroma self-hosted instead of Pinecone (save $70-300/mo)

---

## 14. Testing Strategy

### 14.1 Unit Tests

```python
# tests/test_extraction.py
import pytest
from services.ai_orchestrator import extract_decisions

def test_decision_extraction():
    transcript = """
    Sarah: After reviewing all options, I think we should go with React.
    Mike: I agree, that makes the most sense.
    Team: Agreed.
    """
    
    decisions = extract_decisions(transcript)
    
    assert len(decisions) == 1
    assert "React" in decisions[0]["statement"]
    assert decisions[0]["confidence"] > 0.8

def test_action_item_extraction():
    transcript = """
    Sarah: Mike, can you prepare the budget proposal by next Friday?
    Mike: Sure, I'll have it ready by April 15th.
    """
    
    actions = extract_action_items(transcript)
    
    assert len(actions) == 1
    assert actions[0]["assigned_to"] == "Mike"
    assert "budget proposal" in actions[0]["task"].lower()
    assert actions[0]["deadline"] == "2026-04-15"
```

### 14.2 Integration Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_transcript():
    with open("test_transcript.txt", "rb") as f:
        response = client.post(
            "/api/v1/transcripts/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    assert "transcript_id" in response.json()

def test_query_endpoint():
    response = client.post(
        "/api/v1/query",
        json={"question": "What was decided about the launch date?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
```

### 14.3 E2E Tests

```typescript
// e2e/upload-flow.spec.ts
import { test, expect } from '@playwright/test';

test('upload and process transcript', async ({ page }) => {
  await page.goto('http://localhost:3000/upload');
  
  // Upload file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('test-data/meeting.txt');
  
  // Wait for processing
  await expect(page.locator('.processing-status')).toContainText('completed');
  
  // Check results
  await page.goto('http://localhost:3000/dashboard');
  await expect(page.locator('.action-items-table')).toBeVisible();
});
```

---

## 15. Monitoring & Observability

### 15.1 Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
transcripts_uploaded = Counter('transcripts_uploaded_total', 'Total transcripts uploaded')
decisions_extracted = Counter('decisions_extracted_total', 'Total decisions extracted')
action_items_created = Counter('action_items_created_total', 'Total action items created')
queries_processed = Counter('queries_processed_total', 'Total queries processed')

# Performance metrics
processing_time = Histogram('transcript_processing_seconds', 'Time to process transcript')
query_response_time = Histogram('query_response_seconds', 'Query response time')
llm_api_latency = Histogram('llm_api_call_seconds', 'LLM API call duration')

# System health
active_processing_jobs = Gauge('active_processing_jobs', 'Number of active processing jobs')
```

### 15.2 Logging Strategy

```python
import structlog

logger = structlog.get_logger()

def process_transcript(transcript_id: str):
    logger.info("transcript_processing_started", transcript_id=transcript_id)
    
    try:
        result = extract_all_data(transcript_id)
        logger.info(
            "transcript_processing_completed",
            transcript_id=transcript_id,
            decisions_count=len(result.decisions),
            actions_count=len(result.actions),
            processing_time_seconds=result.elapsed_time
        )
    except Exception as e:
        logger.error(
            "transcript_processing_failed",
            transcript_id=transcript_id,
            error=str(e),
            exc_info=True
        )
```

### 15.3 Error Tracking

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)

# Automatic error capture
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## 16. Future Enhancements

### 16.1 Phase 2 Features

1. **Speaker Diarization**
   - Automatically identify different speakers
   - Track who said what
   - Generate per-speaker summaries

2. **Multi-language Support**
   - Translate transcripts
   - Support non-English meetings
   - Cross-language search

3. **Real-time Transcription**
   - Integrate with Zoom/Teams
   - Live action item extraction
   - Real-time summarization

4. **Advanced Analytics**
   - Meeting effectiveness scores
   - Action item completion rates
   - Decision velocity tracking
   - Team participation metrics

5. **Integrations**
   - Slack notifications for new action items
   - Calendar integration for deadlines
   - Jira/Asana task creation
   - Email digest of pending items

### 16.2 Technical Improvements

1. **Fine-tuned Model**
   - Train custom extraction model on company data
   - Reduce LLM API costs
   - Faster processing

2. **Graph Database**
   - Track decision relationships
   - Show how decisions connect
   - Visualize meeting knowledge graph

3. **Mobile App**
   - iOS/Android native apps
   - Voice recording → transcription
   - Push notifications

---

## 17. Development Timeline

### Week 1: Foundation
- [ ] Set up project structure
- [ ] Configure databases (PostgreSQL + Chroma)
- [ ] Implement file upload and validation
- [ ] Basic authentication

### Week 2: AI Pipeline
- [ ] Integrate Claude API
- [ ] Implement decision extraction
- [ ] Implement action item extraction
- [ ] Set up embedding generation

### Week 3: Core Features
- [ ] Build dashboard UI
- [ ] Create tables for decisions/actions
- [ ] Implement export functionality
- [ ] Add basic filtering

### Week 4: Query System
- [ ] Build vector search
- [ ] Implement query chatbot
- [ ] Add citation system
- [ ] Polish UI/UX

### Week 5: Testing & Polish
- [ ] Write tests
- [ ] Fix bugs
- [ ] Performance optimization
- [ ] Documentation
- [ ] Deploy to production

---

## 18. Conclusion

This architecture provides a comprehensive foundation for building the **Meeting Intelligence Hub**. The system is designed to be:

- **Scalable:** Can handle thousands of meetings
- **Accurate:** Uses state-of-the-art LLMs for extraction
- **User-friendly:** Clean UI with export options
- **Cost-effective:** Optimized for API efficiency
- **Maintainable:** Well-structured codebase

**Key Success Factors:**
1. High-quality AI extraction (focus on prompt engineering)
2. Fast, accurate search (good embeddings + vector DB)
3. Intuitive UX (easy upload, clear results, helpful chat)
4. Reliable citations (always link back to source)

Good luck building your solution! 🚀
