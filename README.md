### Create environment

```bash
PROJECT_NAME = python-project
PYTHON_VERSION = 3.8

conda create --name $PROJECT_NAME --yes python=$PYTHON_VERSION
conda activate $PROJECT_NAME
```

### Install dependencies

```bash
make deps-install
```
### make help

```bash
make help 

help                           print help message
deps-install                   install dependencies
run-ci                         run ci
run-task                       run python task
run-web                        run python web
run                            run main python app
dc-build                       build app image
dc-up                          run app image

```



