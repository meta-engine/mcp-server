#!/usr/bin/env python3
"""Keep authoritative result totals; count messages, calls and characters separately."""
import argparse
import json
import sys
from stream_metrics import StreamMetrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-phase", choices=["warmup", "generation"], default="warmup")
    args = parser.parse_args()
    result = StreamMetrics().parse(sys.stdin)
    result["start_phase"] = args.start_phase
    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
