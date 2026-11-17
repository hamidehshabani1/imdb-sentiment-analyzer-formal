# Formal Use Case Specifications & System Contracts

## 1. Actors
* **User (Primary Actor):** Interacts with the system to analyze single reviews or batch CSV datasets, view statistical dashboards, and export labeled results.
* **Sentiment Engine (Secondary/System Actor):** Pretrained DistilBERT NLP pipeline responsible for text preprocessing and sentiment classification.

---

## 2. Use Case Specifications

| ID | Use Case Name | Actor(s) | Main Flow | Alternative / Exception Flows |
| :--- | :--- | :--- | :--- | :--- |
| **UC-1** | **Analyze Single Review** | `User`, `Sentiment Engine` | 1. User enters raw review text.<br>2. System invokes `UC-3` (`<<include>>`).<br>3. Engine predicts sentiment label and confidence.<br>4. UI displays results. | If input is empty or contains only HTML/URLs, `ValueError` (`Pre-condition Failed`) is raised and shown to the user. |
| **UC-2** | **Analyze Batch CSV** | `User`, `Sentiment Engine` | 1. User uploads a `.csv` file.<br>2. System validates schema (`review`, `text`, `comment`, or `tweet`).<br>3. User selects row limit and triggers execution.<br>4. System runs `UC-3` and inference per row. | If CSV is empty or lacks a valid text column, execution halts with a schema validation error. |
| **UC-3** | **Validate & Preprocess Text** | `Sentiment Engine` | 1. Strip IMDB HTML tags (`<br />`).<br>2. Remove URLs (`http/www`).<br>3. Normalize whitespace. | In batch mode (`UC-2`), empty rows are assigned `("INVALID_EMPTY", 0.0)` instead of terminating the batch job. |
| **UC-4** | **View Sentiment Dashboard** | `User` | Optional extension (`<<extend>>`) to `UC-2`. Renders total count, positive/negative metrics, and a bar chart distribution. | Hidden if the user unchecks the dashboard toggle. |
| **UC-5** | **Export Labeled CSV** | `User` | Optional extension (`<<extend>>`) to `UC-2`. Generates and downloads `labeled_reviews.csv` with `sentiment` and `confidence` columns. | Unavailable until `UC-2` completes successfully. |

---

## 3. Formal Pre-conditions, Post-conditions & Invariants

### Pre-conditions
* **UC-1 (Single Review):**
  $$\text{text} \neq \text{null} \land \text{length}(\text{trim}(\text{clean}(\text{text}))) > 0$$
* **UC-2 (Batch CSV):**
  $$\text{file.extension} = \text{".csv"} \land \text{rows}(\text{df}) \ge 1 \land (\exists c \in \text{df.columns} : c \in \{\text{"review"}, \text{"text"}, \text{"comment"}, \text{"tweet"}\})$$

### Post-conditions
* For every valid input review $r$:
  $$\text{sentiment}(r) \in \{\text{"POSITIVE"}, \text{"NEGATIVE"}\} \land 0.5 \le \text{confidence}(r) \le 1.0$$

### System Invariants
* **Batch Cardinality Preservation:**
  $$\text{rows}(\text{output\_df}) = \text{rows}(\text{input\_subset\_df})$$
  *(Enforced at runtime in `app.py` via `assert len(output_df) == len(df)`).*