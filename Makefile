help:
	@echo "Possible targets:"
	@echo "    test           - to run the testsuite"
	@echo "    doc            - to build the html documentation"
	@echo "    view-doc       - to view the documentation in your web browser"
	@echo "    dev-env <DIR=> - to create a development environment"
	@echo "    clean          - cleans documentation build dir and deletes pyc files"

test:
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
