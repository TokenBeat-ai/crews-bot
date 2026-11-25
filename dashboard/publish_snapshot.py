#!/usr/bin/env python3
"""Publish a verified task snapshot. Does not inspect or run agent chats."""
import argparse
import json
import os
from pathlib import Path
from render_dashboard import render

def publish(tasks, workflows, output):
    output = Path(output).resolve()
    try:
        return render(Path(tasks), Path(workflows), output)
    except Exception:
        output.parent.mkdir(parents=True, exist_ok=True)
        error = output.with_suffix('.error.json')
        temp = error.with_suffix('.tmp')
        temp.write_text(json.dumps({'error': 'Validation or rendering failed. Check the task and workflow configuration; the previous snapshot was kept.'}))
        os.replace(temp, error)
        raise

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('tasks', 'workflows', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    print(publish(a.tasks, a.workflows, a.output))
