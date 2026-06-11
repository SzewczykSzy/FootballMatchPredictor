import pytest
import sqlite3
from src.data.database import initialize_db, get_db_connection
from src.model.contracts import TeamParameters
from src.model.parameters import (
    save_team_parameters,
    get_team_parameters,
    get_all_team_parameters,
    save_model_config,
    get_model_config,
)

def test_team_parameters_and_config_persistence(tmp_path):
    db_file = tmp_path / "test_matches.db"
    db_path = str(db_file)
    
    # Initialize the database with our updated schema
    initialize_db(db_path)
    
    with get_db_connection(db_path) as conn:
        # Verify initial state
        assert get_model_config(conn) is None
        assert len(get_all_team_parameters(conn)) == 0
        assert get_team_parameters(conn, "France") is None
        
        # Test saving team parameters
        france_params = TeamParameters(team_id="France", alpha=1.5, beta=0.8)
        germany_params = TeamParameters(team_id="Germany", alpha=1.2, beta=0.9)
        
        save_team_parameters(conn, [france_params, germany_params])
        
        # Test retrieval
        retrieved_france = get_team_parameters(conn, "France")
        assert retrieved_france is not None
        assert retrieved_france.team_id == "France"
        assert retrieved_france.alpha == pytest.approx(1.5)
        assert retrieved_france.beta == pytest.approx(0.8)
        
        all_params = get_all_team_parameters(conn)
        assert len(all_params) == 2
        assert "France" in all_params
        assert "Germany" in all_params
        assert all_params["Germany"].alpha == pytest.approx(1.2)
        
        # Test upsert (update)
        updated_france = TeamParameters(team_id="France", alpha=1.6, beta=0.75)
        save_team_parameters(conn, [updated_france])
        
        retrieved_france_updated = get_team_parameters(conn, "France")
        assert retrieved_france_updated.alpha == pytest.approx(1.6)
        assert retrieved_france_updated.beta == pytest.approx(0.75)
        
        # Test model config persistence
        save_model_config(conn, gamma=1.1, rho=0.05)
        config1 = get_model_config(conn)
        assert config1 is not None
        assert config1["gamma"] == pytest.approx(1.1)
        assert config1["rho"] == pytest.approx(0.05)
        
        # Test latest config retrieval
        save_model_config(conn, gamma=1.15, rho=0.06)
        config2 = get_model_config(conn)
        assert config2 is not None
        assert config2["gamma"] == pytest.approx(1.15)
        assert config2["rho"] == pytest.approx(0.06)
