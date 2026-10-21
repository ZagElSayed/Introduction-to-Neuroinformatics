"""Student-run entry point; does not run during import."""
import argparse
import json
from pathlib import Path
from agent_studio import Studio, evaluate_cases

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', default='toy_good')
    parser.add_argument('--output', default='agent_outputs')
    parser.add_argument('--failures', type=int, default=0)
    parser.add_argument('--max-steps', type=int, default=8)
    parser.add_argument('--evaluate', action='store_true')
    args = parser.parse_args()
    if args.evaluate:
        rows = evaluate_cases(Path(args.output)/'evaluation')
        path = Path(args.output)/'evaluation_table.json'
        path.write_text(json.dumps(rows, indent=2, allow_nan=False))
        print(json.dumps({'table': str(path), 'cases': len(rows),
                          'matching_expectations': sum(r['matches_expected'] for r in rows)}, indent=2))
    else:
        run = Studio(args.output, failures=args.failures).run(args.dataset, max_steps=args.max_steps)
        print(json.dumps({'status': run['status'], 'reason': run['reason'],
                          'log': run['log'], 'artifact': run['values'].get('stage_report')}, indent=2))

if __name__ == '__main__':
    main()
