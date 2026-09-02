import os
import shutil
import sys
import tempfile
from pathlib import Path
import duckdb
import pytest

# Ensure root directory is on sys.path for test discovery
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import DUCKDB_PATH


def get_safe_test_connection():
    """Return a safe database connection with file-lock recovery."""
    try:
        con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
        return con
    except Exception:
        temp_db = Path(tempfile.gettempdir()) / "retailsphere_test.duckdb"
        shutil.copy2(DUCKDB_PATH, temp_db)
        return duckdb.connect(str(temp_db), read_only=True)


@pytest.fixture(scope="session")
def db_conn():
    """Session-scoped shared database connection fixture."""
    con = get_safe_test_connection()
    yield con
    try:
        con.close()
    except Exception:
        pass
