# Python Project

Starter template for python projects

### Create environment

Use Conda to create a virtual environment and activate it for the project.

```bash
PROJECT_NAME = python-project
PYTHON_VERSION = 3.8

conda create --name $PROJECT_NAME --yes python=$PYTHON_VERSION
conda activate $PROJECT_NAME
```

### Install dependencies

Install Poetry with pip. Then install project dependencies with Poetry.

```bash
make deps-install
```

Use Poetry to add project and development dependencies into `pyproject.toml`.

NOTE: Poetry must be included as a development dependency to prevent
Poetry from uninstalling itself and its dependencies.

