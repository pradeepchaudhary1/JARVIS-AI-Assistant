"""Background checker for due reminders."""

from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Callable, Optional

from memory.scheduler_store import SchedulerStore


class SchedulerRunner:
    def __init__(self, store=None, check_interval=1.0, on_due=None):
        self.store = store or SchedulerStore()
        self.check_interval = float(check_interval)
        self.on_due = on_due
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        """Start the background polling thread if it is not already running."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="SchedulerRunner",
                daemon=True,
            )
            self._thread.start()

    def stop(self):
        """Signal the background thread to stop and wait for it to finish."""
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=max(1.0, self.check_interval * 3 + 1.0))
        self._thread = None

    def _run(self):
        while not self._stop_event.is_set():
            try:
                due_items = self.store.get_due()
                for reminder in due_items:
                    if self.on_due is not None:
                        try:
                            self.on_due(reminder)
                        except Exception:
                            pass
                    try:
                        self.store.mark_fired(reminder["id"])
                    except Exception:
                        pass
            except Exception:
                pass
            self._stop_event.wait(self.check_interval)


__all__ = ["SchedulerRunner"]
