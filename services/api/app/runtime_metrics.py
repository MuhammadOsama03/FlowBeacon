from collections import defaultdict
from threading import Lock


class RuntimeMetrics:
    def __init__(self):
        self._lock = Lock()
        self._requests: dict[tuple[str, str, int], int] = defaultdict(int)
        self._duration_ms: dict[tuple[str, str], float] = defaultdict(float)

    def observe(self, method: str, route: str, status: int, duration_ms: float) -> None:
        with self._lock:
            self._requests[(method, route, status)] += 1
            self._duration_ms[(method, route)] += duration_ms

    def prometheus(self) -> str:
        lines = [
            "# HELP flowbeacon_http_requests_total HTTP requests processed.",
            "# TYPE flowbeacon_http_requests_total counter",
        ]
        with self._lock:
            for (method, route, status), value in sorted(self._requests.items()):
                labels = f'method="{method}",route="{route}",status="{status}"'
                lines.append(f"flowbeacon_http_requests_total{{{labels}}} {value}")
            lines.extend(["# HELP flowbeacon_http_request_duration_ms_total Cumulative request latency.",
                          "# TYPE flowbeacon_http_request_duration_ms_total counter"])
            for (method, route), value in sorted(self._duration_ms.items()):
                labels = f'method="{method}",route="{route}"'
                lines.append(f"flowbeacon_http_request_duration_ms_total{{{labels}}} {value:.3f}")
        return "\n".join(lines) + "\n"


runtime_metrics = RuntimeMetrics()
