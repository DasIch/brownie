help:
	@echo "Possible targets:"
	@echo "    test           - runs the testsuite"
	@echo "    doc            - builds the html documentation"
	@echo "    view-doc       - opens the documentation in your web browser"
	@echo "    dev-env <DIR=> - creates a development environment"
	@echo "    clean          - deletes every generated file"

test:
	@make -C docs/ doctest
	@tox

doc:
	@make -C docs/ html

view-doc: doc
	@python -c "import webbrowser; webbrowser.open('docs/_build/html/index.html')"

DIR ?= env
dev-env:
	@virtualenv $(DIR)
	@. $(DIR)/bin/activate && pip install sphinx attest tox

clean:
	@make -C docs/ clean
	@find . -iname "*.pyc" -delete
	@rm -rf .tox Brownie.egg-info
