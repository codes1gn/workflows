"""workflow_runner CLI — wf command."""
import argparse
import sys

from workflow_runner.runner import WorkflowRunner
from workflow_runner.state import RunState


def cmd_run(args):
    runner = WorkflowRunner()
    workflow = runner.load(args.workflow_name)
    if workflow is None:
        print(f"[wf] Workflow '{args.workflow_name}' not found.", file=sys.stderr)
        print("[wf] Run 'wf list' to see available workflows.", file=sys.stderr)
        sys.exit(1)
    variables = {}
    if args.query:
        variables["query"] = " ".join(args.query)
    if args.var:
        for kv in args.var:
            if "=" in kv:
                k, v = kv.split("=", 1)
                variables[k.strip()] = v.strip()
    state = RunState(workflow["name"])
    runner.execute(workflow, variables, state, dry_run=args.dry_run, verbose=args.verbose)


def cmd_list(args):
    runner = WorkflowRunner()
    workflows = runner.list_all()
    if not workflows:
        print("[wf] No workflows found.")
        return
    print(f"\n{'NAME':<25} {'DESCRIPTION'}")
    print("-" * 70)
    for wf in workflows:
        print(f"  {wf['name']:<23} {wf.get('description', '')[:44]}")
    print()


def cmd_status(args):
    state = RunState.load_latest()
    if state is None:
        print("[wf] No recent workflow runs found.")
        return
    state.print_status()


def cmd_create(args):
    runner = WorkflowRunner()
    runner.scaffold(args.name, args.description or f"Custom workflow: {args.name}")
    print(f"[wf] Created workflow '{args.name}'")
    print(f"     Edit: ~/.copilot/skills/workflows/data/{args.name}.yaml")


def main():
    parser = argparse.ArgumentParser(
        prog="wf",
        description="Workflow runner for Cursor and GitHub Copilot — Claude Code workflows equivalent",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    p_run = sub.add_parser("run", help="Execute a workflow")
    p_run.add_argument("workflow_name", help="Name of workflow to run (e.g. deep-research)")
    p_run.add_argument("query", nargs="*", help="Query or topic (appended as 'query' variable)")
    p_run.add_argument("--var", action="append", metavar="KEY=VALUE", help="Extra variables")
    p_run.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    p_run.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    p_run.set_defaults(func=cmd_run)

    # list
    p_list = sub.add_parser("list", help="List available workflows")
    p_list.set_defaults(func=cmd_list)

    # status
    p_status = sub.add_parser("status", help="Show recent workflow run status")
    p_status.set_defaults(func=cmd_status)

    # create
    p_create = sub.add_parser("create", help="Scaffold a new workflow")
    p_create.add_argument("name", help="Workflow name (kebab-case)")
    p_create.add_argument("description", nargs="?", help="Short description")
    p_create.set_defaults(func=cmd_create)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
