"""Test helpers for mocking database cursors."""

from collections import deque
from contextlib import AbstractContextManager
from typing import Any, Iterable, List, Optional, Sequence, Tuple


class FakeCursor:
    """Simple in-memory cursor stub that records executed statements."""

    def __init__(
        self,
        fetchone_results: Optional[Iterable[Any]] = None,
        fetchall_results: Optional[Iterable[Sequence[Any]]] = None,
        lastrowid: int = 1,
    ) -> None:
        self.fetchone_results = deque(fetchone_results or [])
        self.fetchall_results = deque(fetchall_results or [])
        self.executed: List[Tuple[str, Any]] = []
        self.lastrowid = lastrowid
        self.rowcount = 0
        self.closed = False

    def execute(self, query: str, params: Any = None) -> None:
        self.executed.append((self._normalize(query), params))

    def executemany(self, query: str, seq_of_params: Sequence[Any]) -> None:
        self.executed.append((self._normalize(query), list(seq_of_params)))

    def fetchone(self) -> Any:
        if self.fetchone_results:
            return self.fetchone_results.popleft()
        return None

    def fetchall(self) -> Any:
        if self.fetchall_results:
            return self.fetchall_results.popleft()
        return []

    def close(self) -> None:
        self.closed = True

    @staticmethod
    def _normalize(query: str) -> str:
        """Compress whitespace so asserts remain stable."""
        return " ".join(query.split())


class _CursorContext(AbstractContextManager):
    """Context manager wrapper for FakeCursor instances."""

    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor = cursor

    def __enter__(self) -> FakeCursor:
        return self.cursor

    def __exit__(self, exc_type, exc, exc_tb) -> bool:
        self.cursor.close()
        return False


def cursor_context(cursor: FakeCursor) -> AbstractContextManager:
    """Return a context manager compatible with utils.database.get_db_cursor."""
    return _CursorContext(cursor)
