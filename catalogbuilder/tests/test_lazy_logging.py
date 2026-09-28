import ast
from pathlib import Path


LOGGER_METHODS = {"debug", "info", "warning", "error", "critical", "exception"}
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (PACKAGE_ROOT / "intakebuilder", PACKAGE_ROOT / "scripts")


def _is_eager_logging_message(message):
    if isinstance(message, ast.JoinedStr):
        return True
    if isinstance(message, ast.BinOp) and isinstance(message.op, (ast.Add, ast.Mod)):
        return True
    if isinstance(message, ast.Call) and isinstance(message.func, ast.Attribute) and message.func.attr == "format":
        return True
    return False


def test_logger_calls_use_lazy_formatting():
    violations = []

    for source_dir in SOURCE_DIRS:
        for path in source_dir.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute) or node.func.attr not in LOGGER_METHODS:
                    continue
                if not isinstance(node.func.value, ast.Name) or node.func.value.id != "logger":
                    continue
                if not node.args:
                    continue

                if _is_eager_logging_message(node.args[0]):
                    violations.append(f"{path}:{node.lineno}")

    assert not violations, "Non-lazy logger calls found:\n" + "\n".join(sorted(violations))
