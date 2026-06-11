import streamlit as st
from src.ui.components import process_odds_and_predict, render_predictions_table

def main():
    st.set_page_config(
        page_title="Football Match Predictor",
        page_icon="⚽",
        layout="centered"
    )

    st.title("⚽ Football Match Predictor")
    st.write(
        "Paste your raw match listings and bookmaker odds below to generate "
        "mathematically optimal Expected Value (EV) predictions."
    )

    # Large text area for odds pasting (T007)
    odds_input = st.text_area(
        label="Paste Bookmaker Odds",
        height=300,
        placeholder="Example:\nFrance - Germany\nBet365 1.85 3.60 4.20\nPinnacle 1.90 3.55 4.30"
    )

    # Action button to trigger predictions (T007)
    if st.button("Generate Predictions"):
        if not odds_input.strip():
            st.error("Please paste some bookmaker odds first.")
            return

        try:
            # Spinner to give visual feedback during processing
            with st.spinner("Processing odds and calculating optimal predictions..."):
                predictions = process_odds_and_predict(odds_input)
            
            st.success(f"Successfully generated predictions for {len(predictions)} match(es)!")
            
            # Display results in a clean table (T010)
            render_predictions_table(predictions)

        except ValueError as ve:
            # User-friendly error message for parsing/validation failures (T008)
            st.error(f"Parsing Error: {str(ve)}")
        except Exception as e:
            # General fallback to prevent raw stack traces from crashing the UI (T008)
            st.error(f"An unexpected error occurred during prediction generation: {str(e)}")

if __name__ == "__main__":
    main()
