from pathlib import Path

import pytest
from dotenv import load_dotenv

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@pytest.fixture
def load_document():
    def _load(name: str) -> str:
        return (FIXTURES_DIR / name).read_text(encoding="utf-8")

    return _load
