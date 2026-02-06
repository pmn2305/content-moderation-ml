import time
from collections import defaultdict

class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.latencies = defaultdict(list)

    def inc(self, name: str, value: int = 1):
        self.counters[name] += value

    def observe(self, name: str, value: float):
        self.latencies[name].append(value)

    def snapshot(self):
        return {
            "counters": dict(self.counters),
            "latencies": {
                k: {
                    "count": len(v),
                    "avg": round(sum(v) / len(v), 3) if v else 0.0,
                    "max": round(max(v), 3) if v else 0.0,
                }
                for k, v in self.latencies.items()
            },
        }


metrics = Metrics()
