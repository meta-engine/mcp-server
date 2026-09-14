#!/usr/bin/env python3
"""Print one report, deriving observed metrics from its original streams."""
import sys
from pathlib import Path
from report import BenchmarkReport
from result_reader import ResultReader
from stream_metrics import StreamMetrics


def main():
    root = Path(sys.argv[1])
    print(BenchmarkReport().render(root.name, ResultReader(StreamMetrics()).collect(root)), end="")


if __name__ == "__main__":
    main()
