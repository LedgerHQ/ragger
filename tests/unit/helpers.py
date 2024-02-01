from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


@contextmanager
def temporary_directory():
    with TemporaryDirectory() as dir_path:
        yield Path(dir_path).resolve()
