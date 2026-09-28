import ast
from pathlib import Path


LOGGER_METHODS = {"debug", "info", "warning", "error", "critical", "exception"}
PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _package_python_files():
    for path in PACKAGE_ROOT.rglob("*.py"):
        if "tests" not in path.parts:
            yield path


def _is_eager_logging_message(message):
    if isinstance(message, ast.JoinedStr):
        return True
    if isinstance(message, ast.BinOp) and isinstance(message.op, (ast.Add, ast.Mod)):
        return True
    if isinstance(message, ast.Call) and isinstance(message.func, ast.Attribute) and message.func.attr == "format":
        return True
    return False


def _is_get_logger_call(node):
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "logging"
        and node.func.attr == "getLogger"
    )


def _logger_names(tree):
    names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _is_get_logger_call(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and _is_get_logger_call(node.value):
            names.add(node.target.id)

    return names


def _is_logger_receiver(node, logger_names):
    if isinstance(node, ast.Name):
        return node.id in logger_names
    if isinstance(node, ast.Attribute):
        return node.attr == "logger"
    return _is_get_logger_call(node)


def _lazy_logging_violations(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    logger_names = _logger_names(tree)
    violations = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr not in LOGGER_METHODS:
            continue
        if not _is_logger_receiver(node.func.value, logger_names):
            continue
        if not node.args:
            continue

        if _is_eager_logging_message(node.args[0]):
            violations.append(f"{path}:{node.lineno}")

    return violations


def test_logger_calls_use_lazy_formatting():
    violations = []

    for path in _package_python_files():
        violations.extend(_lazy_logging_violations(path))

    assert not violations, "Non-lazy logger calls found:\n" + "\n".join(sorted(violations))
