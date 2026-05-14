# /// script
# requires-python = ">=3.10"
# ///
"""Structural validation for langchain-aws contributions.

Checks file placement, test mirroring, __init__.py exports, and integration
test gating. Outputs structured JSON for agent consumption.

Usage:
    python scripts/check_structure.py --repo-root /path/to/langchain-aws
    python scripts/check_structure.py --repo-root . --changed-files libs/aws/langchain_aws/new_module.py
    python scripts/check_structure.py --help
"""

import argparse
import ast
import json
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


def check_test_mirroring(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check that new source files have corresponding test files."""
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
                # Skip __init__.py, __pycache__, private helpers
                fname = f.name
                if fname.startswith("_") or fname == "__init__.py":
                    continue

                # Compute expected test path
                relative_to_src = rel[len(src_dir) + 1 :]
                test_path = repo_root / test_dir / relative_to_src.replace(
                    fname, f"test_{fname}"
                )

                if not test_path.exists():
                    checks.append({
                        "name": "test_mirroring",
                        "status": "fail",
                        "message": f"Missing unit test file: {test_path.relative_to(repo_root)}",
                        "file": rel,
                    })
                else:
                    checks.append({
                        "name": "test_mirroring",
                        "status": "pass",
                        "message": f"Unit test exists: {test_path.relative_to(repo_root)}",
                        "file": rel,
                    })
    return checks


def check_init_exports(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check that new modules update their parent __init__.py."""
    checks = []
    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        if not rel.startswith("libs/aws/langchain_aws"):
            continue
        if not rel.endswith(".py") or f.name.startswith("_"):
            continue
        if f.name == "__init__.py":
            continue

        init_path = f.parent / "__init__.py"
        if not init_path.exists():
            checks.append({
                "name": "init_exports",
                "status": "warn",
                "message": f"No __init__.py in {f.parent.relative_to(repo_root)}",
                "file": rel,
            })
            continue

        init_content = init_path.read_text()
        module_name = f.stem
        if module_name not in init_content:
            checks.append({
                "name": "init_exports",
                "status": "warn",
                "message": f"Module '{module_name}' not referenced in {init_path.relative_to(repo_root)}",
                "file": rel,
            })
        else:
            checks.append({
                "name": "init_exports",
                "status": "pass",
                "message": f"Module '{module_name}' found in __init__.py",
                "file": rel,
            })
    return checks


def check_integration_test_gating(
    repo_root: Path, changed_files: list[Path]
) -> list[dict]:
    """Check that integration tests are properly gated."""
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
                "name": "integration_test_gating",
                "status": "fail",
                "message": "Integration test has no skip/gate — will fail in CI without AWS credentials",
                "file": rel,
            })
        elif "def test_" in content:
            checks.append({
                "name": "integration_test_gating",
                "status": "pass",
                "message": "Integration test is properly gated",
                "file": rel,
            })
    return checks


def check_file_placement(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check that files are in the correct directory based on content."""
    checks = []
    valid_source_dirs = {
        "chat_models",
        "llms",
        "embeddings",
        "retrievers",
        "vectorstores",
        "tools",
        "agents",
        "graphs",
        "chains",
        "middleware",
        "runnables",
        "document_compressors",
        "utilities",
        "data",
        "memory",
    }

    for f in changed_files:
        rel = str(f.relative_to(repo_root))
        if not rel.startswith("libs/aws/langchain_aws"):
            continue
        if not rel.endswith(".py") or f.name.startswith("_"):
            continue

        parts = Path(rel).parts
        # Expected: libs/aws/langchain_aws/<module_dir>/file.py
        if len(parts) >= 4:
            module_dir = parts[3]
            if module_dir not in valid_source_dirs and f.name != "__init__.py":
                # Top-level files (utils.py, function_calling.py) are ok
                if len(parts) == 4:
                    continue
                checks.append({
                    "name": "file_placement",
                    "status": "warn",
                    "message": f"File in unexpected directory '{module_dir}'. Expected one of: {sorted(valid_source_dirs)}",
                    "file": rel,
                })
            else:
                checks.append({
                    "name": "file_placement",
                    "status": "pass",
                    "message": f"File correctly placed in '{module_dir}/'",
                    "file": rel,
                })
    return checks


def check_docstrings(repo_root: Path, changed_files: list[Path]) -> list[dict]:
    """Check that public classes/methods have docstrings."""
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
                "name": "docstrings",
                "status": "fail",
                "message": "Syntax error — cannot parse file",
                "file": rel,
            })
            continue

        missing = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith("_"):
                    continue
                if not ast.get_docstring(node):
                    missing.append(node.name)

        if missing:
            names = ", ".join(missing[:5])
            suffix = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
            checks.append({
                "name": "docstrings",
                "status": "warn",
                "message": f"Public symbols missing docstrings: {names}{suffix}",
                "file": rel,
            })
        elif any(
            isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            for n in ast.walk(tree)
        ):
            checks.append({
                "name": "docstrings",
                "status": "pass",
                "message": "All public symbols have docstrings",
                "file": rel,
            })
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Structural validation for langchain-aws contributions.",
        epilog="Outputs JSON with check results. Exit code 1 if any check fails.",
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
        help="List of changed files to check. If omitted, detects via git diff against main.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.changed_files:
        changed_files = [repo_root / f for f in args.changed_files]
    else:
        changed_files = find_changed_files(repo_root)

    if not changed_files:
        result = {"checks": [], "summary": "No changed files detected."}
        print(json.dumps(result, indent=2))
        return

    # Filter to existing files only
    changed_files = [f for f in changed_files if f.exists()]

    all_checks: list[dict] = []
    all_checks.extend(check_test_mirroring(repo_root, changed_files))
    all_checks.extend(check_init_exports(repo_root, changed_files))
    all_checks.extend(check_integration_test_gating(repo_root, changed_files))
    all_checks.extend(check_file_placement(repo_root, changed_files))
    all_checks.extend(check_docstrings(repo_root, changed_files))

    fails = sum(1 for c in all_checks if c["status"] == "fail")
    warns = sum(1 for c in all_checks if c["status"] == "warn")
    passes = sum(1 for c in all_checks if c["status"] == "pass")

    result = {
        "checks": all_checks,
        "summary": {
            "total": len(all_checks),
            "pass": passes,
            "warn": warns,
            "fail": fails,
        },
    }

    if args.format == "text":
        for check in all_checks:
            icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}[check["status"]]
            print(f"{icon} [{check['name']}] {check['file']}: {check['message']}")
        print(f"\nSummary: {passes} pass, {warns} warn, {fails} fail")
    else:
        print(json.dumps(result, indent=2))

    if fails > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
