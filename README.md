### python project template 
python项目脚手架，可以快速创建项目，使用conda、make、poetry、docker、fastapi、gunicorn、uvicorn、pyinstaller、pre-commit-config

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
```
```
help                           print help message
deps-install                   install dependencies
deps-install-ci                install CI
deps-update                    update dependencies
format                         format code
lint                           static code check
test                           code test
run-ci                         run ci
run-task                       run python task
build-task-exe                 build task exe
run-web-dev                    run web app dev
run-web                        run python web
run                            run main python app
dc-build                       build web_dev、web_ci、web image
dc-push                        push web_dev and web docker image
dc-ci                          run web_ci, end delete
dc-up                          run web dev app image
dc-exec                        run web_dev exec /bin/bash
dc-stop                        stop docker server
dc-down                        stop and delete docker server

```



