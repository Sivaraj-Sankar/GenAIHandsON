# GenAI + Agentic AI Design for Extracting Tables from Excel/CSV Files

---

## 1. Problem Statement

Real-world Excel and CSV files rarely contain clean, machine-ready tables. Instead, they often include:

* Free-text summaries at the **top** (titles, reporting periods, notes)
* One or more **structured tables** in the middle
* Totals, footnotes, or explanations at the **bottom**
* Large row counts (1,000+ rows)

Passing the entire file directly to an LLM is **not feasible** due to:

* Context window limits
* Token generation limits
* Cost and latency
* Loss of determinism

The goal is to design a **scalable, production-grade GenAI + Agentic AI workflow** that:

* Reliably extracts only the real table
* Works even when header rows are unknown
* Handles large datasets efficiently
* Uses LLMs only where reasoning is required

---

## 2. Core Design Principle

> **LLMs should reason, not process raw data**

| Responsibility                 | Technology         |
| ------------------------------ | ------------------ |
| File reading & computation     | Pandas / Python    |
| Pattern detection & statistics | Deterministic code |
| Structural reasoning           | LLM                |
| Execution of filters           | Pandas / SQL       |

This leads to a **hybrid architecture**:

* **Code** performs heavy data operations
* **LLMs** identify structure, boundaries, and intent

---

## 3. High-Level System Architecture

```
┌──────────────┐
│  Excel File  │
└──────┬───────┘
       ↓
┌──────────────────────────┐
│ Chunked Structural Scan  │  (Code)
│ - Non-null counts        │
│ - Type consistency       │
│ - Row patterns           │
└────────┬─────────────────┘
         ↓
┌──────────────────────────┐
│ LLM Structure Reasoning  │
│ - Detect header row      │
│ - Detect data start/end  │
│ - Ignore summaries       │
└────────┬─────────────────┘
         ↓
┌──────────────────────────┐
│ Deterministic Extraction │  (Code)
│ - Slice rows             │
│ - Assign headers         │
└────────┬─────────────────┘
         ↓
┌──────────────────────────┐
│ Optional Validation LLM  │
│ - Schema sanity check    │
└──────────────────────────┘
```

---

## 4. Step-by-Step Workflow

### Step 1: Load Excel Without Assumptions

```python
import pandas as pd

df = pd.read_excel("input.xlsx", header=None)
```

Why `header=None`?

* Header row location is unknown
* Prevents accidental misalignment

---

### Step 2: Structural Profiling (Code Only)

Each row is profiled without semantic interpretation.

Captured metrics:

* Row index
* Number of non-null cells
* Sample cell values

```python
row_profiles = []

for idx, row in df.iterrows():
    row_profiles.append({
        "row": idx,
        "non_null": row.notna().sum(),
        "sample": row.dropna().astype(str).tolist()[:3]
    })
```

This produces **lightweight metadata**, not raw data.

---

### Step 3: Minimal Payload Sent to LLM

Only metadata is passed to the LLM.

```json
{
  "rows": [
    {"row": 0, "non_null": 2, "sample": ["Revenue Summary"]},
    {"row": 7, "non_null": 8, "sample": ["Account", "Amount", "Date"]},
    {"row": 8, "non_null": 8, "sample": ["Cash", "12000", "2023-04-01"]},
    {"row": 1009, "non_null": 2, "sample": ["Total", "20000"]}
  ]
}
```

This keeps token usage extremely low.

---

### Step 4: LLM Reasoning Task

**LLM Prompt Objective:**

> Identify the table header row, data start row, and data end row. Ignore summaries and totals.

**LLM Output (Strict JSON):**

```json
{
  "header_row": 7,
  "data_start": 8,
  "data_end": 1008,
  "confidence": 0.94
}
```

The LLM performs **structural reasoning**, not data processing.

---

### Step 5: Deterministic Table Extraction

```python
extracted_df = df.iloc[data_start:data_end + 1]
extracted_df.columns = df.iloc[header_row]
```

Benefits:

* Fast
* Reproducible
* Scales to millions of rows

---

### Step 6: Optional Validation Agent

A second LLM call can validate:

* Column name quality
* Data type consistency
* Presence of totals or noise

This step improves reliability in enterprise workflows.

---

## 5. Agentic AI Architecture (Production-Grade)

```
┌──────────────────────┐
│ File Loader Agent    │
│ - Reads Excel        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Profiler Agent       │  (Code)
│ - Row statistics     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Structure Agent      │  (LLM)
│ - Finds table bounds │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Extraction Agent     │  (Code)
│ - Slices dataframe   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Validation Agent     │  (LLM)
└──────────────────────┘
```

Each agent has a **single responsibility**, improving debuggability.

---

## 6. Agentic Control Flow (LangGraph-style)

```
START
  ↓
Load Excel
  ↓
Profile Rows
  ↓
LLM Detect Table Region
  ↓
Extract Table
  ↓
Validate Table?
  ├─ Yes → END
  └─ No  → Re-run boundary detection
```

---

## 7. Scaling Strategy for Very Large Files

| File Size | Strategy                             |
| --------- | ------------------------------------ |
| <10k rows | Full profile scan                    |
| 10k–100k  | Chunked profiling                    |
| 100k+     | Histogram-based row density analysis |

LLM is called **once per file**, regardless of size.

---

## 8. Key Architectural Insights

* LLMs detect **structure**, not rows
* Metadata ≫ raw data for AI reasoning
* Deterministic extraction ensures compliance
* Agentic separation improves maintainability

> This design effectively creates an **AI-powered Excel parser** suitable for enterprise systems.

---

## 9. Where This Fits in Real Systems

* Credit analysis automation
* Financial statement ingestion
* Regulatory reporting pipelines
* Agentic RAG preprocessing layer

---

## 10. Possible Extensions

* Multi-table detection
* Confidence scoring & human-in-the-loop
* Schema inference + validation rules
* Integration with FastAPI / Django
* RAG-ready structured output

---

**End of Documentation**
