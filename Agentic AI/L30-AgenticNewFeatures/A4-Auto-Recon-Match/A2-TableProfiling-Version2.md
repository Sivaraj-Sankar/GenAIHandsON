# GenAI Table Extractor — Architecture (Component + Low‑Level Design)

Current Date: 2026-02-11  
Owner: `sivaraj-enverus`  
Primary Module: `genai_table_extractor.py`

---

## 1) Purpose

Design a scalable, production-grade workflow to extract **true tabular regions** from messy Excel/CSV files (titles, summaries, footnotes, totals, multiple sections), while minimizing LLM usage by sending only **structural metadata** (not raw data).

**Core principle:** *LLMs should reason about structure; deterministic code should do data processing.*

---

## 2) System Context (High-Level)

### Inputs
- Excel: `.xlsx`, `.xls` (potentially multiple sheets)
- CSV: `.csv` (optionally with delimiter inference)
- Constraints: can be 1k–1M+ rows, unknown headers, extra text blocks

### Outputs
- Extracted table as:
  - `pandas.DataFrame`
  - persisted formats: CSV / Parquet / JSON
- Extraction metadata:
  - detected header row, start/end bounds
  - confidence score
  - validation findings / warnings

### Non-Goals
- Full semantic understanding of every cell
- Fully autonomous multi-table extraction (optional extension)

---

## 3) Component Architecture (Component-by-Component)

```text
+-----------------------------------------------------------------------------------+
|                                GenAI Table Extractor                              |
|                                                                                   |
|  +------------------+      +-------------------+      +------------------------+  |
|  |  File Loader     | ---> |  Structural       | ---> |  Structure Reasoner    |  |
|  |  (Code)          |      |  Profiler (Code)  |      |  (LLM)                 |  |
|  +------------------+      +-------------------+      +------------------------+  |
|           |                          |                           |                 |
|           |                          v                           v                 |
|           |                  +-------------------+      +------------------------+ |
|           |                  | Candidate Region  |      | JSON Boundary Contract | |
|           |                  | Builder (Code)    |      | (strict schema)        | |
|           |                  +-------------------+      +------------------------+ |
|           |                                                          |            |
|           v                                                          v            |
|  +------------------+      +-------------------+      +------------------------+ |
|  | Deterministic    | <--- | Extraction        | <--- | Validation Agent (LLM) | |
|  | Extraction       |      | Orchestrator      |      | (optional)             | |
|  | (Pandas)         |      | (Agentic control) |      +------------------------+ |
|  +------------------+      +-------------------+                 |               |
|           |                                                          v            |
|           v                                                   +------------------+|
|  +------------------+                                         | Output Writer    ||
|  | Observability    |                                         | (CSV/Parquet/DB) ||
|  | (logs/metrics)   |                                         +------------------+|
|  +------------------+                                                               
+-----------------------------------------------------------------------------------+
```

### 3.1 File Loader (Code)
**Responsibility**
- Read file without assumptions about header rows.
- Normalize into an internal “raw dataframe” representation.

**Key behaviors**
- Excel: `pd.read_excel(..., header=None, sheet_name=...)`
- CSV: `pd.read_csv(..., header=None, sep=..., engine="python")`

**Outputs**
- `raw_df` (`DataFrame`) with integer column indices
- `file_metadata` (sheet name, size, encoding, delimiter)

---

### 3.2 Structural Profiler (Code)
**Responsibility**
- Compute lightweight row-level statistics to infer structure without semantics.

**Row features (recommended)**
- `row_index`
- `non_null_count`
- `non_empty_string_count`
- `unique_type_signature` (approx types: number/date/text/empty)
- `leading_empty_cells` (helps detect indentation)
- `sample_values` (first N non-null as strings; N small like 3–5)
- `row_width_estimate` (max contiguous non-null span)

**Outputs**
- `row_profiles: List[RowProfile]`
- `column_profiles` (optional; helpful for type consistency checks)

---

### 3.3 Candidate Region Builder (Code)
**Responsibility**
- Reduce search space before LLM call.

**Techniques**
- Row density histogram: detect bands of high `non_null_count`.
- Contiguous “dense” row runs: potential table blocks.
- Skip very sparse intro/outro rows.
- Optionally detect “TOTAL” rows heuristically (but don’t remove yet).

**Outputs**
- `candidate_windows: List[CandidateWindow]`  
  Example: `[{start_row: 0, end_row: 200}, {start_row: 450, end_row: 1100}]`

---

### 3.4 Structure Reasoner (LLM)
**Responsibility**
- Choose which candidate window contains the table and identify:
  - header row index
  - data start
  - data end
  - confidence score
  - rationale codes (optional)

**What is sent to the LLM**
- Only metadata:
  - row indices
  - non-null counts
  - short samples
  - optional type hints
- Never send entire sheet values unless file is tiny and policy allows.

**Outputs (strict JSON)**
```json
{
  "header_row": 7,
  "data_start": 8,
  "data_end": 1008,
  "confidence": 0.94,
  "notes": "Header row has field-like strings; data rows have consistent width."
}
```

---

### 3.5 Deterministic Extraction (Pandas)
**Responsibility**
- Slice dataframe using LLM-provided bounds.
- Assign headers.
- Normalize column names and drop empty columns.

**Steps**
1. `table_df = raw_df.iloc[data_start:data_end+1].copy()`
2. `headers = raw_df.iloc[header_row].astype(str)`
3. Clean headers (strip, dedupe, replace “nan”, empty → fallback name)
4. Assign: `table_df.columns = cleaned_headers`
5. Drop columns that are fully null after slicing
6. Optional: type casting (numbers/dates) deterministically

**Outputs**
- `extracted_df`
- `extraction_report` (rows extracted, columns kept, header quality)

---

### 3.6 Validation Agent (Optional LLM)
**Responsibility**
- Validate the extracted result rather than raw file:
  - Are column names “field-like”?
  - Are there repeated header rows inside data?
  - Does the last row look like totals/footnotes?
  - Is there high null rate suggesting wrong bounds?

**Outputs**
- `validation_status: PASS|WARN|FAIL`
- `fix_suggestions` (e.g., “data_end should be 1007, last row is totals”)

---

### 3.7 Orchestrator (Agentic Control)
**Responsibility**
- Manage the workflow, retries, fallback rules, and stopping criteria.

**Typical policies**
- 1 LLM call for boundary detection (primary)
- Optional 1 LLM call for validation
- Retry boundary detection once if validation FAILs

---

### 3.8 Output Writer
**Responsibility**
- Persist results and metadata.

**Artifacts**
- `extracted_table.parquet`
- `extracted_table.csv`
- `extraction_metadata.json` (header row, bounds, confidence, warnings)

---

### 3.9 Observability / Operations
**Responsibility**
- Make production debugging possible.

**Log**
- file size, row/col count
- candidate windows considered
- LLM response + schema validation result
- extraction summary
- validation warnings

**Metrics**
- extraction success rate
- average confidence
- retries per file
- LLM tokens / latency
- percent of files requiring human review

---

## 4) Low-Level Design (LLD)

### 4.1 Core Data Contracts

#### RowProfile
```text
RowProfile
- row: int
- non_null: int
- non_empty_str: int
- leading_empty: int
- width_estimate: int
- type_signature: {num:int, date:int, text:int, empty:int}
- sample: list[str]   # first N non-null stringified values
```

#### CandidateWindow
```text
CandidateWindow
- start_row: int
- end_row: int
- score: float     # density-based score
- reason: str      # e.g., "dense-run", "type-consistent"
```

#### LLMBoundaryDecision (strict)
```json
{
  "header_row": "int (0..n-1)",
  "data_start": "int (0..n-1)",
  "data_end": "int (0..n-1)",
  "confidence": "float (0..1)",
  "notes": "string (optional)"
}
```

---

### 4.2 Algorithm Details (Deterministic Parts)

#### A) Profiling algorithm
- Iterate rows (vectorize where possible):
  - `non_null = row.notna().sum()`
  - `sample = row.dropna().astype(str).head(N).tolist()`
- Derive:
  - `leading_empty`: count from left until first non-null
  - `width_estimate`: `last_non_null_col - first_non_null_col + 1`

#### B) Candidate window detection
- Build `non_null_series` over rows
- Compute threshold `T = max(3, percentile(non_null, 75))` (tunable)
- Identify contiguous runs where `non_null >= T`
- Merge nearby runs separated by small gaps (e.g., <= 2 rows)
- Produce windows (cap to max windows, like top 3 by score)

#### C) Header cleaning
- `strip()`, replace newlines with spaces
- treat `"nan"`, `"none"`, empty as missing → fallback `col_{i}`
- deduplicate: if duplicates exist, suffix `_2`, `_3`, …

---

### 4.3 LLM Prompting Strategy (Boundary Detection)

**Goal:** enforce strict schema + reduce hallucination.

**Inputs**
- Candidate windows summary (start/end)
- For each row in window: `(row_index, non_null, sample)`

**Constraints to include**
- `header_row < data_start <= data_end`
- Prefer header with mostly text-like tokens
- Data rows likely consistent width and type patterns
- Avoid “Total”, “Subtotal”, “Notes” rows as data_end (unless table genuinely ends)

---

### 4.4 Validation Rules (Code + Optional LLM)

**Code-only checks (fast)**
- extracted rows >= minimal (e.g., >= 3)
- extracted cols >= minimal (e.g., >= 2)
- header quality: % non-empty column names
- null density threshold across columns
- detect repeated header row inside data (row equals header strings)

**Escalate to LLM validation when**
- multiple candidate windows close in score
- confidence < threshold (e.g., 0.80)
- code checks produce ambiguous warnings

---

## 5) Sequence Diagram (End-to-End)

```text
Client
  |
  | 1) submit(file)
  v
Orchestrator
  |
  |--> FileLoader.read() --------------------> raw_df
  |
  |--> Profiler.profile(raw_df) -------------> row_profiles
  |
  |--> RegionBuilder.find_candidates(row_profiles) -> candidate_windows
  |
  |--> LLM.StructureReasoner(boundary_metadata) ---> boundary_decision(JSON)
  |
  |--> Extractor.extract(raw_df, boundary_decision) -> extracted_df
  |
  |--> Validator.check(extracted_df) -> PASS/WARN/FAIL
  |        |
  |        +--(optional) LLM.ValidationAgent(extracted_df_summary)
  |
  |--> OutputWriter.persist(extracted_df, metadata)
  |
  v
Client receives outputs + metadata
```

---

## 6) Agentic Control Flow (State Machine)

```text
[START]
  |
  v
[LOAD_FILE]
  |
  v
[PROFILE_ROWS]
  |
  v
[BUILD_CANDIDATES]
  |
  v
[LLM_DETECT_BOUNDS]
  |
  v
[EXTRACT_TABLE]
  |
  v
[VALIDATE]
  | \
  |  \-- if FAIL and retries_remaining --> [LLM_DETECT_BOUNDS]
  |
  v
[WRITE_OUTPUT]
  |
  v
[END]
```

**Stop conditions**
- PASS: finish
- WARN: finish (but tag for review)
- FAIL after retry: export best-effort + mark failed

---

## 7) Deployment View (Production)

### Runtime options
- Batch (Spark / Airflow / Dagster)
- Online (FastAPI service)
- Hybrid (async job queue: Celery / SQS)

### Suggested services
- API Service: accepts file, stores to object storage
- Worker: runs extraction pipeline
- LLM Gateway: central place for prompt templates, model selection, auditing
- Metadata Store: store extraction metadata + quality signals

---

## 8) Configuration (Tunable Parameters)

| Parameter | Default | Purpose |
|---|---:|---|
| `sample_size_per_row` | 3 | limits tokens |
| `dense_percentile` | 75 | candidate detection |
| `min_cols` | 2 | reject non-tables |
| `min_rows` | 3 | reject trivial extracts |
| `max_candidate_windows` | 3 | LLM focus |
| `confidence_threshold` | 0.80 | trigger validation/retry |
| `max_retries` | 1 | cost control |

---

## 9) Extensions (Roadmap)
- Multi-table detection per sheet (iterate windows and extract multiple tables)
- Human-in-the-loop UI for low confidence cases
- Schema inference rules (domain-specific)
- RAG-ready output (chunk tables + metadata for indexing)

---

## 10) Appendix — Minimal Interface Sketch

```text
class TableExtractionPipeline:
  - extract(file_path, sheet=None) -> (extracted_df, metadata)

metadata includes:
  - header_row, data_start, data_end
  - confidence
  - candidate_windows
  - validation_status, warnings
  - timings, token_usage
```

---

End of document.
