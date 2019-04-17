from json import loads
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union

import nox
from nox.sessions import Session

DepsT = Union[List[str], Tuple[str]]
TEST_DEPENDENCIES = ("pytest", "pytest-mock", "webtest")
BLACK_DEPENDENCIES = ("black",)
BLACKEN_DEPENDENCIES = ("black",)
FLAKE8_DEPENDENCIES = (
    "flake8",
    "flake8-bugbear",
    "flake8-builtins",
    "flake8-commas",
    "flake8-comprehensions",
    "flake8-docstrings",
    "flake8-eradicate",
    "flake8-import-order",
    "flake8-pytest",
    "flake8-quotes",
    "flake8-super-call",
    "pep8-naming",
)

nox.options.sessions = ["black", "flake8", "tests", "example"]
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_missing_interpreters = True

PROJECT_ROOT = Path(__file__).parent
EXAMPLES_ROOT = Path(PROJECT_ROOT, "examples")


@nox.session(python="3.7")
def blacken(session: Session):
    install_dependencies(session, BLACKEN_DEPENDENCIES, install_self=False)
    show_environment_info(session, ("black", "--version"))
    session.run("black", ".")


@nox.session(python="3.7")
def black(session: Session):
    install_dependencies(session, BLACK_DEPENDENCIES, install_self=False)
    show_environment_info(session, ("black", "--version"))
    session.run("black", "--check", ".")


@nox.session(python="3.7")
def flake8(session: Session):
    install_dependencies(session, FLAKE8_DEPENDENCIES, install_self=False)
    show_environment_info(session, ("flake8", "--version"))
    session.run("flake8", ".")


@nox.session(python=["3.5", "3.6", "3.7"])
def tests(session: Session):
    install_dependencies(session, TEST_DEPENDENCIES)
    session.install(".")
    show_environment_info(session, ("pytest", "--version"))
    session.run("pytest")


def example_run(session: Session, name: str = None):
    descr = get_example_descr(name)

    install_dependencies(session, descr.get("requires", []))
    show_environment_info(session)

    session.log("Running example %r", descr.get("name"))
    session.chdir(str(descr["dir"].absolute()))
    result = session.run(*descr["command"], silent=True)

    output = get_contents(Path(descr["dir"], descr["output"]))

    if result != output:
        session.error(
            "Example output did not match expected output:\n"
            "===== EXPECTED OUTPUT BEGIN =====\n%s\n"
            "===== EXPECTED OUTPUT END =====\n"
            "===== ACTUAL OUTPUT BEGIN =====\n%s\n"
            "===== ACTUAL OUTPUT END =====\n",
            output,
            result,
        )
    session.log("Example output matched expected output, all is well.")


def install_dependencies(
    session: Session, dependencies: DepsT = None, install_self: bool = True
):
    if dependencies:
        session.install(*dependencies)
    if install_self:
        session.install(".")


def show_environment_info(session: Session, *args):
    session.run("python", "--version")
    session.run("pip", "--version")
    session.run("pip", "list", "--format=columns")
    for arg in args:
        session.run(*arg)


def get_contents(filename: Path) -> str:
    with filename.open("r") as f:
        return f.read()


def get_example_descr(name: str) -> Dict[str, Any]:
    example_dir = Path(EXAMPLES_ROOT, name)
    assert example_dir.exists()
    assert example_dir.is_dir()

    example_json = Path(example_dir, "example.json")
    assert example_json.exists()
    assert example_json.is_file()

    descr = loads(get_contents(example_json))
    descr.update({"dir": example_dir, "json": example_json})

    return descr


def get_all_example_names(examples_root: Path = EXAMPLES_ROOT) -> Iterable[str]:
    """Return a list of directories, that have 'example.py' file."""
    examples_dir = Path(examples_root)
    assert examples_dir.exists

    examples = []
    for item in examples_dir.iterdir():
        if not item.is_dir():
            continue
        example_json = Path(item, "example.json")
        if example_json.exists() and example_json.is_file():
            examples.append(item.name)
    return examples


EXAMPLES = get_all_example_names()


def example(session: Session, name: str = None):
    if name is None:
        session.log("There are no examples.")
        return
    example_run(session, name)


# Only create the actual example session, when there are examples present
if EXAMPLES:

    example = nox.parametrize("name", EXAMPLES)(example)
    example = nox.session(example, python=["3.5", "3.6", "3.7"])

else:
    example = nox.session(example)
