.PHONY: clean build upload test-upload install dev-install help

help:
	@echo "Available targets:"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build the distribution package"
	@echo "  test-upload  - Upload to TestPyPI"
	@echo "  upload       - Upload to PyPI"
	@echo "  install      - Install the package locally"
	@echo "  dev-install  - Install in development mode"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

build: clean
	venv/bin/python setup.py sdist bdist_wheel

create-venv:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip setuptools wheel twine

test-upload: build
	venv/bin/twine upload --repository testpypi dist/*

upload: build
	venv/bin/twine upload dist/*

install:
	pip install .

dev-install:
	pip install -e .
