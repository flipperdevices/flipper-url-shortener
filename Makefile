VERSION := 0.0.0
PYTHON_VERSION := 3.11


.PHONY: run
uvicorn: venv requirements
	poetry run uvicorn --reload --log-level=info --workers 2 --host 0.0.0.0 --port 8000 app.main:app

venv:
	pip install jsonschema==4.17.3 poetry
	poetry env use ${PYTHON_VERSION}

#.PHONY: migration
#migration: venv requirements
#	poetry run migrate-tool generate ${NAME}
#
#.PHONY: migrate
#migrate: venv requirements
#	poetry run migrate-tool migrate ${NAME}
#
#.PHONY: downgrade
#downgrade: venv requirements
#	poetry run migrate-tool downgrade ${NAME}

.PHONY: pre
pre:
	ruff . --fix
	isort . --profile black
	black . --skip-string-normalization --line-length=120

.PHONY: tests
tests: venv requirements
	poetry run pytest tests -s

.PHONY: requirements
requirements: venv
	poetry install

.PHONY: clean
clean:
	poetry env remove ${PYTHON_VERSION}
	rm -rf dist

.PHONY: docker_build
docker_build:
	docker build . --tag "3dexperience:${VERSION}"

.PHONY: docker_uvicorn
docker_uvicorn: docker_build
	docker run -it -p 8000:8000 --rm "3dexperience:${VERSION}"

.PHONY: docker_uvicorn_env_file
docker_uvicorn_env_file: docker_build
	docker run -it --env-file=.env -p 8000:8000 --rm "3dexperience:${VERSION}"

.PHONY: helm_package
helm_package:
	helm package helm -d dist --version=${VERSION}

.PHONY: helm_install
helm_install:
	helm install shortener helm

.PHONY: helm_upgrade
helm_upgrade:
	helm upgrade shortener helm

.PHONY: helm_uninstall
helm_uninstall:
	helm uninstall shortener

.PHONY: helm_reinstall
helm_reinstall:
	helm uninstall shortener || true
	helm install shortener helm

.PHONY: release
release: docker_build helm_package
	docker save "shortener:${VERSION}" | gzip -c > dist/3dexperience-${VERSION}.docker.tgz
