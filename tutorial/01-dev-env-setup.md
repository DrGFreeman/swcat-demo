# Development environment setup


## Python Virtual Environment

Create a Python virtual environment (venv) using Python 3.12.

```
python3.12 -m venv .venv --prompt swcat-tuto --upgrade-deps
source .venv/bin/activate
```

Install pip-tools in the venv.

```
python -m pip install pip-tools
```

Use `pip-sync` command provided by pip-tools to install development dependencies.

```
pip-sync requirements-dev.txt
```

## Pre-Commit Hooks

Setup pre-commit hooks.

```
pre-commit install
```

## Software Catalog Module

Define a python module named swcat by creating a new empty file named `swcat/__init__.py`.