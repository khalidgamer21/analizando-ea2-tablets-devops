from pathlib import Path

import pytest

from tablets_devops.data import replay_snapshot

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def dataset():
    return replay_snapshot(ROOT / "data" / "snapshot")[0]


@pytest.fixture
def focal_html():
    return (ROOT / "data" / "snapshot" / "fragmentos" / "6932554444525.html").read_bytes()
