build: install_req
	python -c "import vai_chover_bot"

install: install_req
	pip install .

install_req:
	pip install -r requirements.txt

test:
	nosetests tests
