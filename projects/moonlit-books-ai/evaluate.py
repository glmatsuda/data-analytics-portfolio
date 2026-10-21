#!/usr/bin/env python3
"""Run real local inference; never substitutes example model responses."""
import json
from pathlib import Path
import core
if __name__=='__main__':
    status=core.model_status()
    if not status['ready']:
        raise SystemExit(status['message'])
    report=core.run_evaluation(lambda p: print(f"{p['completed']}/{p['total']} complete",flush=True))
    path=Path(__file__).resolve().parent/'results/evaluation.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report,indent=2))
    print(json.dumps(report['summary'],indent=2))
    print(f'Saved {path}')
