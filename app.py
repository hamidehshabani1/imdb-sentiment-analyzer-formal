import re
import pandas as pd
import streamlit as st
from transformers import pipeline

# ==========================================
# System Configuration & Model Initialization
# ==========================================
st.set_page_config(page_title="IMDB Sentiment Analyzer", page_icon="🎬", layout="wide")


@st.cache_resource
def load_sentiment_engine():
    """Loads a lightweight pretrained DistilBERT model for sentiment analysis."""
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512,
    )


# ==========================================
# UC-3: Validate & Preprocess Text (<<include>>)
# ==========================================
def validate_and_preprocess(text: str) -> str:
    """
    Pre-condition: text must be a non-empty string after stripping whitespace.
    Cleans IMDB HTML tags (<br />), URLs, and extra spaces.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Pre-condition Failed: Input text cannot be empty.")

    cleaned = re.sub(r"<br\s*/?>", " ", text)  # Remove IMDB HTML line breaks
    cleaned = re.sub(r"http\S+|www\S+", "", cleaned)  # Remove URLs (useful for Twitter)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        raise ValueError("Pre-condition Failed: Text contains no valid characters after cleaning.")
    return cleaned


# ==========================================
# UC-1: Analyze Single Review
# ==========================================
def analyze_single_review(raw_text: str, engine) -> dict:
    """Executes UC-3 (include) then predicts sentiment label and confidence."""
    clean_text = validate_and_preprocess(raw_text)
    result = engine(clean_text)[0]
    return {
        "cleaned_text": clean_text,
        "sentiment": result["label"],  # Post-condition: 'POSITIVE' or 'NEGATIVE'
        "confidence": round(float(result["score"]), 4),  # Post-condition: [0.5, 1.0]
    }


# ==========================================
# UC-2: Analyze Batch CSV
# ==========================================
def validate_csv_schema(df: pd.DataFrame) -> str:
    """
    Pre-condition: CSV must not be empty and must contain a 'review' or 'text' column.
    Returns the detected text column name.
    """
    if df.empty:
        raise ValueError("Pre-condition Failed: Uploaded CSV file is empty.")

    for candidate in ["review", "text", "comment", "tweet"]:
        if candidate in df.columns:
            return candidate

    raise ValueError("Pre-condition Failed: CSV must contain a 'review' or 'text' column.")


def analyze_batch_csv(df: pd.DataFrame, text_col: str, engine) -> pd.DataFrame:
    """
    Processes all rows while maintaining System Invariant: N_out == N_in.
    """
    output_df = df.copy()
    sentiments = []
    confidences = []

    for raw_item in output_df[text_col].fillna(""):
        try:
            clean_item = validate_and_preprocess(str(raw_item))
            pred = engine(clean_item)[0]
            sentiments.append(pred["label"])
            confidences.append(round(float(pred["score"]), 4))
        except ValueError:
            sentiments.append("INVALID_EMPTY")
            confidences.append(0.0)

    output_df["sentiment"] = sentiments
    output_df["confidence"] = confidences

    # System Invariant Check
    assert len(output_df) == len(df), "Invariant Violated: Row count mismatch!"
    return output_df


# ==========================================
# User Interface (Actor: User)
# ==========================================
def main():
    st.title("🎬 IMDB & Social Media Sentiment Analyzer")
    st.caption("Formal Methods Project Prototype — Interactive AI Sentiment Analysis")

    engine = load_sentiment_engine()

    tab_single, tab_batch = st.tabs(["📝 Single Review (UC-1)", "📂 Batch CSV Analysis (UC-2)"])

    # --- Tab 1: Single Review ---
    with tab_single:
        user_review = st.text_area(
            "Enter a movie review or comment:",
            placeholder="Example: The cinematography was breathtaking, though the pacing in the second act felt slow.<br />Overall a masterpiece!",
            height=130,
        )
        if st.button("Analyze Review", type="primary"):
            try:
                res = analyze_single_review(user_review, engine)
                col1, col2 = st.columns(2)
                col1.metric("Predicted Sentiment", res["sentiment"])
                col2.metric("Confidence Score", f"{res['confidence'] * 100:.2f}%")
                with st.expander("View Preprocessed Text (UC-3 Output)"):
                    st.write(res["cleaned_text"])
            except ValueError as err:
                st.error(str(err))

    # --- Tab 2: Batch CSV ---
    with tab_batch:
        uploaded_file = st.file_uploader("Upload CSV file (must include 'review' or 'text' column)", type=["csv"])

        # Sample CSV generator for quick testing
        sample_csv = pd.DataFrame({
            "review": [
                "An absolute masterpiece! Brilliant acting and gripping story.<br />10/10.",
                "Waste of two hours. Predictable plot and terrible dialogue.",
                "Visual effects were stunning, but the ending made zero sense.",
                "One of the best sci-fi movies I have watched in years!",
                "Boring, slow, and completely forgettable.",
            ]
        }).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Sample IMDB CSV for Testing", sample_csv, "sample_imdb.csv", "text/csv")

        if uploaded_file is not None:
            try:
                raw_df = pd.read_csv(uploaded_file)
                text_col = validate_csv_schema(raw_df)

                max_rows = st.slider("Number of rows to analyze (for fast execution):", 1, len(raw_df), min(50, len(raw_df)))
                subset_df = raw_df.head(max_rows)

                if st.button("Run Batch Analysis", type="primary"):
                    with st.spinner("Running Sentiment Engine..."):
                        result_df = analyze_batch_csv(subset_df, text_col, engine)
                        st.session_state["result_df"] = result_df

                if "result_df" in st.session_state:
                    res_df = st.session_state["result_df"]
                    st.success(f"Analysis Complete! Processed {len(res_df)} records.")

                    # UC-4: View Sentiment Dashboard (<<extend>>)
                    if st.checkbox("📊 Show Sentiment Dashboard (UC-4)", value=True):
                        counts = res_df["sentiment"].value_counts()
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Total Reviews", len(res_df))
                        c2.metric("Positive", int(counts.get("POSITIVE", 0)))
                        c3.metric("Negative", int(counts.get("NEGATIVE", 0)))
                        st.bar_chart(counts)

                    st.dataframe(res_df, use_container_width=True)

                    # UC-5: Export Labeled CSV (<<extend>>)
                    csv_out = res_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="💾 Export Labeled CSV (UC-5)",
                        data=csv_out,
                        file_name="labeled_reviews.csv",
                        mime="text/csv",
                    )
            except Exception as err:
                st.error(f"Error: {err}")


if __name__ == "__main__":
    main()