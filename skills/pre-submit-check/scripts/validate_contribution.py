# /// script
# requires-python = ">=3.10"
# ///
"""Pre-submission validation for langchain-aws contributions.

Checks code quality, test coverage, file placement, and CI readiness.
Designed to catch common issues before a PR is submitted.

Usage:
    python3 scripts/validate_contribution.py --repo-root /path/to/langchain-aws
    python3 scripts/validate_contribution.py --repo-root . --changed-files file1.py file2.py
    python3 scripts/validate_contribution.py --help

Exit codes:
    0 - All checks pass (or only warnings)
    1 - One or more checks failed
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path


def find_changed_files(repo_root: Path) -> list[Path]:
    """Detect changed files via git diff against main."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "main", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [repo_root / f for f in result.stdout.strip().split("\n")]
    except FileNotFoundError:
        pass
    return []


def check_test_presence(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check that new source files have corresponding unit tests."""
    checks = []
    source_dirs = {
        "libs/aws/langchain_aws": "libs/aws/tests/unit_tests",
        "libs/langgraph-checkpoint-aws/langgraph_checkpoint_aws": "libs/langgraph-checkpoint-aws/tests",
        "libs/agentcore-codeinterpreter/langchain_agentcore_codeinterpreter": "libs/agentcore-codeinterpreter/tests",
    }

    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        for src_dir, test_dir in source_dirs.items():
            if rel.startswith(src_dir) and rel.endswith(".py"):
                fname = f.name
                if fname.startswith("_") or fname == "__init__.py":
                    continue
                relative_to_src = rel[len(src_dir) + 1 :]
                test_path = repo_root / test_dir / relative_to_src.replace(
                    fname, f"test_{fname}"
                )
                if not test_path.exists():
                    checks.append({
                        "name": "test_presence",
                        "status": "fail",
                        "message": f"Missing unit test. Create: {test_path.relative_to(repo_root)}",
                        "file": rel,
                    })
                else:
                    checks.append({
                        "name": "test_presence",
                        "status": "pass",
                        "message": "Unit test exists",
                        "file": rel,
                    })
    return checks


def check_integration_test_gating(
    repo_root: Path, changed_files: list[Path]
) -> list[dict]:
    """Check that integration tests won't break CI."""
    checks = []
    gating_patterns = [
        "pytest.mark.skip",
        "pytest.mark.skipif",
        "pytest.importorskip",
        "os.environ.get(",
        'os.environ["',
        "os.getenv(",
    ]

    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        if "integration_tests" not in rel:
            continue
        if not rel.endswith(".py") or f.name == "__init__.py":
            continue

        content = f.read_text()
        has_gating = any(pattern in content for pattern in gating_patterns)

        if not has_gating and "def test_" in content:
            checks.append({
                "name": "integration_gating",
                "status": "fail",
                "message": "Integration test missing skip/gate. Add @pytest.mark.skipif(not os.environ.get('AWS_ACCESS_KEY_ID'), reason='...')",
                "file": rel,
            })
        elif "def test_" in content:
            checks.append({
                "name": "integration_gating",
                "status": "pass",
                "message": "Integration test properly gated",
                "file": rel,
            })
    return checks


def check_docstrings_and_types(
    repo_root: Path, changed_files: list[Path]
) -> list[dict]:
    """Check public methods have docstrings and type hints."""
    checks = []
    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        if not rel.startswith("libs/") or not rel.endswith(".py"):
            continue
        if "test" in rel or f.name.startswith("_"):
            continue

        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            checks.append({
                "name": "syntax",
                "status": "fail",
                "message": "File has syntax errors",
                "file": rel,
            })
            continue

        missing_docs = []
        missing_types = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                if not ast.get_docstring(node):
                    missing_docs.append(node.name)
                if node.returns is None:
                    missing_types.append(node.name)

        if missing_docs:
            names = ", ".join(missing_docs[:3])
            suffix = f" (+{len(missing_docs) - 3} more)" if len(missing_docs) > 3 else ""
            checks.append({
                "name": "docstrings",
                "status": "warn",
                "message": f"Missing docstrings: {names}{suffix}",
                "file": rel,
            })

        if missing_types:
            names = ", ".join(missing_types[:3])
            suffix = f" (+{len(missing_types) - 3} more)" if len(missing_types) > 3 else ""
            checks.append({
                "name": "type_hints",
                "status": "warn",
                "message": f"Missing return type hints: {names}{suffix}",
                "file": rel,
            })

        if not missing_docs and not missing_types:
            has_funcs = any(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not n.name.startswith("_")
                for n in ast.walk(tree)
            )
            if has_funcs:
                checks.append({
                    "name": "code_quality",
                    "status": "pass",
                    "message": "Docstrings and type hints present",
                    "file": rel,
                })
    return checks


def check_bare_except(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check for bare except clauses."""
    checks = []
    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        if not rel.endswith(".py"):
            continue

        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                checks.append({
                    "name": "bare_except",
                    "status": "fail",
                    "message": f"Bare 'except:' at line {node.lineno}. Catch specific exceptions.",
                    "file": rel,
                })
                break
    return checks


def check_init_exports(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check new public classes are exported in __init__.py."""
    checks = []
    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        if not rel.startswith("libs/aws/langchain_aws"):
            continue
        if not rel.endswith(".py") or f.name.startswith("_") or f.name == "__init__.py":
            continue

        init_path = f.parent / "__init__.py"
        if not init_path.exists():
            continue

        init_content = init_path.read_text()
        module_name = f.stem
        if module_name not in init_content:
            checks.append({
                "name": "init_exports",
                "status": "warn",
                "message": f"Module '{module_name}' not referenced in {init_path.relative_to(repo_root)}. Add exports if it contains public classes.",
                "file": rel,
            })
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-submission validation for langchain-aws contributions.",
        epilog="Exit code 1 if any check fails. Warnings don't cause failure.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Path to the langchain-aws repository root (default: current directory)",
    )
    parser.add_argument(
        "--changed-files",
        nargs="*",
        help="Files to check. If omitted, detects via git diff against main.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.changed_files:
        changed_files = [repo_root / f for f in args.changed_files]
    else:
        changed_files = find_changed_files(repo_root)

    if not changed_files:
        print("No changed files detected. Nothing to validate.")
        return

    changed_files = [f for f in changed_files if f.exists()]

    all_checks: list[dict] = []
    all_checks.extend(check_test_presence(repo_root, changed_files))
    all_checks.extend(check_integration_test_gating(repo_root, changed_files))
    all_checks.extend(check_docstrings_and_types(repo_root, changed_files))
    all_checks.extend(check_bare_except(repo_root, changed_files))
    all_checks.extend(check_init_exports(repo_root, changed_files))

    fails = sum(1 for c in all_checks if c["status"] == "fail")
    warns = sum(1 for c in all_checks if c["status"] == "warn")
    passes = sum(1 for c in all_checks if c["status"] == "pass")

    if args.format == "text":
        if all_checks:
            for check in all_checks:
                icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}[check["status"]]
                print(f"{icon} [{check['name']}] {check['file']}: {check['message']}")
            print(f"\n{'─' * 40}")
            print(f"Results: {passes} pass, {warns} warnings, {fails} failures")
            if fails > 0:
                print("\n❌ Fix failures before submitting your PR.")
            elif warns > 0:
                print("\n⚠️  Warnings won't block merge but should be addressed.")
            else:
                print("\n✅ All checks pass. Ready to submit!")
        else:
            print("No applicable checks for the changed files.")
    else:
        result = {
            "checks": all_checks,
            "summary": {"total": len(all_checks), "pass": passes, "warn": warns, "fail": fails},
        }
        print(json.dumps(result, indent=2))

    if fails > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
