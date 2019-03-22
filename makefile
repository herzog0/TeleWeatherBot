build: install_req
	python -c "import bot"

install: install_req
	pip install .

install_req:
	pip install -r requirements.txt

