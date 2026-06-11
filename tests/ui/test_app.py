import pytest
from streamlit.testing.v1 import AppTest
from src.ui.components import process_odds_and_predict

def test_process_odds_and_predict_unit():
    """
    Unit test for the backend integration function process_odds_and_predict.
    """
    raw_text = """
    France - Germany
    Bet365 1.85 3.60 4.20
    Pinnacle 1.90 3.55 4.30
    """
    # Using default parameters if matches.db is empty, but we can verify it doesn't crash
    results = process_odds_and_predict(raw_text)
    assert len(results) == 1
    assert results[0]["MatchID"] == "France vs Germany"
    assert "Recommended Prediction" in results[0]
    assert isinstance(results[0]["Expected Value"], float)
    assert results[0]["Status"] == "Success"

def test_app_loads():
    """
    Verify the Streamlit application loads without errors and renders the main title.
    """
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception
    assert any("Football Match Predictor" in title.value for title in at.title)

def test_app_elements_exist():
    """
    Verify that the input text area and action button exist on load.
    """
    at = AppTest.from_file("app.py")
    at.run()
    assert len(at.text_area) >= 1
    assert len(at.button) >= 1
    assert at.text_area[0].label == "Paste Bookmaker Odds"
    assert at.button[0].label == "Generate Predictions"

def test_app_generate_predictions_success():
    """
    Verify that pasting valid odds and clicking the button renders the prediction table.
    """
    at = AppTest.from_file("app.py")
    at.run()
    
    # Enter valid odds text
    valid_text = """
    France - Germany
    Bet365 1.85 3.60 4.20
    Pinnacle 1.90 3.55 4.30
    """
    at.text_area[0].set_value(valid_text)
    at.button[0].click().run()
    
    assert not at.exception
    # Verify table has been rendered (should render using st.table)
    assert len(at.table) == 1

def test_app_generate_predictions_invalid():
    """
    Verify that pasting invalid text displays an error message.
    """
    at = AppTest.from_file("app.py")
    at.run()
    
    # Enter invalid text
    invalid_text = "Not odds data at all"
    at.text_area[0].set_value(invalid_text)
    at.button[0].click().run()
    
    assert not at.exception
    # Should display error alert
    assert len(at.error) >= 1
    assert any("No matches" in error.value or "parsing" in error.value.lower() for error in at.error)
