"""Performance metrics for environment setup."""

import time
from typing import Dict, Any


class PerformanceMetrics:
    """Track performance metrics for environment setup operations."""

    def __init__(self):
        """Initialize performance metrics."""
        self.venv_create_time: float = 0.0
        self.install_time: float = 0.0
        self.download_time: float = 0.0
        self._start_times: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation.

        Args:
            operation: Name of the operation
        """
        self._start_times[operation] = time.time()

    def stop_timer(self, operation: str) -> float:
        """Stop timing an operation and record duration.

        Args:
            operation: Name of the operation

        Returns:
            Duration in seconds
        """
        if operation not in self._start_times:
            return 0.0

        duration = time.time() - self._start_times[operation]

        # Record to appropriate field
        if operation == "venv_create":
            self.venv_create_time = duration
        elif operation == "install":
            self.install_time = duration
        elif operation == "download":
            self.download_time = duration

        del self._start_times[operation]
        return duration

    def record_venv_create(self, duration: float) -> None:
        """Record venv creation time.

        Args:
            duration: Duration in seconds
        """
        self.venv_create_time = duration

    def record_install(self, duration: float) -> None:
        """Record dependency installation time.

        Args:
            duration: Duration in seconds
        """
        self.install_time = duration

    def record_download(self, duration: float) -> None:
        """Record download time.

        Args:
            duration: Duration in seconds
        """
        self.download_time = duration

    def get_total_time(self) -> float:
        """Get total time for all operations.

        Returns:
            Total duration in seconds
        """
        return self.venv_create_time + self.install_time + self.download_time

    def report(self) -> None:
        """Print performance report."""
        total = self.get_total_time()
        print(f"\n⚡ Performance Report:")
        if self.download_time > 0:
            print(f"   - Download: {self.download_time:.2f}s")
        print(f"   - Create venv: {self.venv_create_time:.2f}s")
        print(f"   - Install dependencies: {self.install_time:.2f}s")
        print(f"   - Total: {total:.2f}s")

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary.

        Returns:
            Dictionary with all metrics
        """
        return {
            "venv_create_time": self.venv_create_time,
            "install_time": self.install_time,
            "download_time": self.download_time,
            "total_time": self.get_total_time(),
        }
