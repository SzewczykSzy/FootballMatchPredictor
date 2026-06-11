# Quickstart: Streamlit UI

## Overview
This feature introduces `app.py`, a Streamlit-based web interface that serves as the local presentation layer for the EV Prediction system.

## Usage Example

### Running the Application

1. Open your terminal in the project root.
2. Activate your virtual environment if applicable.
3. Run the Streamlit server:
```bash
streamlit run app.py
```
4. Your default web browser will automatically open and navigate to `http://localhost:8501`.

### Generating Predictions

1. Locate the large Text Area field labeled "Paste Bookmaker Odds".
2. Paste the multi-line text containing the match listings and odds from your source.
3. Click the **Generate Predictions** button.
4. The system will process the text synchronously and output a scannable Markdown/HTML table below the button with the Recommended Exact Scores and their Expected Values.

## Testing

To run the UI-specific tests using the Streamlit AppTest framework:
```bash
pytest tests/ui/test_app.py -v
```
