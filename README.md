# 🎬 IMDB & Social Media Sentiment Analyzer (Formal Methods Project)

An interactive NLP web application built with **Python**, **Streamlit**, and **Hugging Face Transformers (DistilBERT)** for sentiment analysis of movie reviews and social media comments. Designed and documented using **Formal Methods** principles, including UML behavioral/structural modeling, pre/post-conditions, and runtime invariants.

---

## ✨ Features
* **Single Review Analysis (`UC-1`):** Real-time sentiment classification (`POSITIVE` / `NEGATIVE`) with confidence score and text cleaning preview.
* **Batch CSV Processing (`UC-2`):** Supports IMDB and Twitter/social media datasets (`review`, `text`, `comment`, or `tweet` columns) with configurable row limits.
* **Automated Text Preprocessing (`UC-3`):** Strips HTML `<br />` tags, URLs, and redundant whitespace (`<<include>>`).
* **Interactive Analytics Dashboard (`UC-4`):** Optional visual breakdown of sentiment distribution (`<<extend>>`).
* **Labeled Dataset Export (`UC-5`):** One-click download of processed results as `labeled_reviews.csv` (`<<extend>>`).

---

## 📐 Formal Modeling & UML Diagrams

Full formal specifications, pre/post-conditions, and system invariants are documented in [`docs/formal_specs.md`](docs/formal_specs.md).

### 1. Use Case Diagram
![Use Case Diagram](docs/diagrams/use_case_diagram.png)

### 2. State Machine Diagram
![State Machine Diagram](docs/diagrams/state_machine_diagram.png)

### 3. Sequence Diagram
![Sequence Diagram](docs/diagrams/sequence_diagram.png)

---

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/imdb-sentiment-analyzer-formal.git
   cd imdb-sentiment-analyzer-formal