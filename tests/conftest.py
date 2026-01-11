import os
import pytest

@pytest.fixture(autouse=True)
def _set_pythonpath():
    # makes `import src....` work when running in docker
    os.environ.setdefault("PYTHONPATH", "/app")
