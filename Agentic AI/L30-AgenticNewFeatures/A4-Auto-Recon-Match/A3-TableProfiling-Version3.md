# GenAI Table Extractor — Executive-Ready Mermaid Diagrams

> Copy/paste into a Markdown viewer that supports Mermaid (GitHub, mkdocs-material, etc.)

---

## 1) Executive Overview (Clean, High-Impact)

```mermaid
flowchart LR
  A["Messy Excel/CSV<br/>Titles - Notes - Tables - Footers<br/>1k-1M+ rows"] --> B["Structural Scan (Code)<br/>fast - deterministic"]
  B --> C["LLM Structure Reasoner<br/>detect header + start/end bounds<br/>metadata only"]
  C --> D["Deterministic Extraction (Pandas)<br/>slice - set headers - cleanup"]
  D --> E{"Quality Gate"}
  E -->|Pass| F["Publish Clean Table<br/>Parquet/CSV/DB + metadata"]
  E -->|Warn/Fail| G["Optional LLM Validation<br/>schema + noise checks"]
  G --> H["Auto-fix bounds (1 retry)<br/>or Human Review Queue"]
  H --> F
```

---

## 2) Component Architecture (Component-by-Component)

```mermaid
flowchart TB
  subgraph S1["Input Layer"]
    I1["Excel (.xlsx/.xls)"]
    I2["CSV (.csv)"]
  end

  subgraph S2["Core Pipeline (Hybrid AI)"]
    L["File Loader (Code)<br/>header=None - sheet selection"]
    P["Structural Profiler (Code)<br/>row stats - type hints - samples"]
    R["Candidate Region Builder (Code)<br/>density runs - window scoring"]
    LLM1["Structure Reasoner (LLM)<br/>outputs: header_row, data_start, data_end"]
    X["Deterministic Extractor (Pandas)<br/>slice + header assign + normalize"]
    V{"Validation Gate"}
    LLM2["Validation Agent (LLM, optional)<br/>sanity + totals/noise check"]
  end

  subgraph S3["Outputs"]
    O1["Clean DataFrame"]
    O2["Persisted Table<br/>CSV/Parquet/DB"]
    O3["Extraction Metadata<br/>bounds + confidence + warnings"]
  end

  subgraph S4["Ops and Governance"]
    OBS["Observability<br/>logs - metrics - traces"]
    AUDIT["Governance<br/>prompt versioning - audit trail"]
  end

  I1 --> L
  I2 --> L
  L --> P --> R --> LLM1 --> X --> V
  V -->|PASS| O1
  O1 --> O2
  V -->|WARN/FAIL| LLM2 --> X
  X --> O3

  L -.-> OBS
  P -.-> OBS
  R -.-> OBS
  X -.-> OBS
  O3 -.-> OBS
  LLM1 -.-> AUDIT
  LLM2 -.-> AUDIT
```
---

## 3) Sequence Diagram (What Happens at Runtime)

```mermaid
sequenceDiagram
  autonumber
  participant Client as Client / API
  participant Orchestrator as Orchestrator
  participant Loader as File Loader (Code)
  participant Profiler as Profiler (Code)
  participant Region as Region Builder (Code)
  participant LLM as LLM Structure Reasoner
  participant Extractor as Extractor (Pandas)
  participant Validator as Validator (Code)
  participant LLMV as LLM Validation (Optional)
  participant Store as Output Store

  Client->>Orchestrator: submit(file, sheet?)
  Orchestrator->>Loader: read(header=None)
  Loader-->>Orchestrator: raw_df + file_metadata

  Orchestrator->>Profiler: profile_rows(raw_df)
  Profiler-->>Orchestrator: row_profiles (metadata)

  Orchestrator->>Region: build_candidate_windows(row_profiles)
  Region-->>Orchestrator: candidate_windows

  Orchestrator->>LLM: detect_bounds(row_metadata)
  LLM-->>Orchestrator: {header_row, data_start, data_end, confidence}

  Orchestrator->>Extractor: extract(raw_df, bounds)
  Extractor-->>Orchestrator: extracted_df + extraction_report

  Orchestrator->>Validator: validate(extracted_df)
  alt PASS
    Validator-->>Orchestrator: PASS
    Orchestrator->>Store: write(table + metadata)
    Store-->>Client: output locations + summary
  else WARN/FAIL
    Validator-->>Orchestrator: WARN/FAIL
    Orchestrator->>LLMV: validate_summary(extracted_df_summary)
    LLMV-->>Orchestrator: fix suggestions / adjusted bounds
    Orchestrator->>Extractor: re-extract(adjusted bounds)
    Extractor-->>Orchestrator: extracted_df (rev2)
    Orchestrator->>Store: write(table + metadata)
    Store-->>Client: output locations + summary
  end
```

---

## 4) Executive “Why It Scales” Diagram (Cost + Token Control)

```mermaid
flowchart LR
  A["Raw file can be huge<br/>1M+ rows"] --> B["Code computes structure<br/>O(n) scan and chunking"]
  B --> C["Metadata only to LLM<br/>row index + non-null + samples"]
  C --> D["Single LLM call per file<br/>structure decision only"]
  D --> E["Deterministic extraction<br/>fast + reproducible"]
  E --> F["Optional second LLM call<br/>only on low confidence"]
```

---

## 5) Control Flow (Agentic State Machine)

```mermaid
stateDiagram-v2
  [*] --> LoadFile
  LoadFile --> ProfileRows
  ProfileRows --> BuildCandidates
  BuildCandidates --> LLMDetectBounds
  LLMDetectBounds --> ExtractTable
  ExtractTable --> Validate

  Validate --> WriteOutput: PASS
  Validate --> LLMValidate: WARN/FAIL
  LLMValidate --> ExtractTable: Adjust bounds (<= 1 retry)
  WriteOutput --> [*]
```

---

## 6) Deployment (Exec-Friendly Operating Model)

```mermaid
flowchart TB
  subgraph Users[Business Users / Upstream Systems]
    U1[Finance / Ops]
    U2[Automations]
  end

  subgraph Platform[Enterprise Data Platform]
    API[Ingestion API<br/>FastAPI / Gateway]
    OBJ[Object Storage<br/>S3/ADLS/GCS]
    Q[Job Queue<br/>SQS/Celery/Kafka]
    W[Worker Service<br/>Python + Pandas]
    LLMG[LLM Gateway<br/>model routing + policy]
    META[Metadata Store<br/>Postgres/Elastic]
    DWH[Lakehouse / Warehouse<br/>Parquet/Delta/Snowflake]
    MON[Monitoring<br/>logs/metrics/traces]
  end

  U1 --> API
  U2 --> API
  API --> OBJ
  API --> Q
  Q --> W
  W --> OBJ
  W --> LLMG
  W --> META
  W --> DWH
  API --> META
  META --> MON
  W --> MON
  LLMG --> MON
```

---
End of diagrams.
