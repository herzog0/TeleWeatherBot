PROJECT = tele_weather_bot
VIRTUAL_ENV = env

install: virtual download_and_activate
build: clean_package build_package_tmp zip


virtual:
	@echo "--> Setup and activate virtualenv"
	if test ! -d "$(VIRTUAL_ENV)"; then \
		pip3 install virtualenv; \
		virtualenv -p python3 $(VIRTUAL_ENV); \
	fi
	@echo ""

download_and_activate:
	@echo "-->Activating virtual environment"
	if test -d "$(VIRTUAL_ENV)"; then \
		. ./$(VIRTUAL_ENV)/bin/activate; \
		pip3 install -r requirements.txt; \
	fi
	@echo "Now type 'source ./env/bin/activate' then 'python3 run.py'"

clean_package:
	rm -rf ./package/*

build_package_tmp:
	mkdir -p ./package/tmp/
	cp -a ./$(PROJECT) ./package/tmp/
	cp main.py ./package/tmp/
	cp TOKENS_HERE.py ./package/tmp/
	cp requirements.txt ./package/tmp/

copy_python:
	if test -d $(VIRTUAL_ENV)/lib; then \
		cp -a $(VIRTUAL_ENV)/lib/python3.6/site-packages/. ./package/tmp/; \
	fi
	if test -d $(VIRTUAL_ENV)/lib64; then \
		cp -a $(VIRTUAL_ENV)/lib64/python3.6/site-packages/. ./package/tmp/; \
	fi

remove_unused:
	rm -rf ./package/tmp/wheel*
	rm -rf ./package/tmp/easy-install*
	rm -rf ./package/tmp/setuptools*

zip:	
	cd ./package/tmp && zip -r ../$(PROJECT).zip ./

deploy_gcloud:
	gcloud functions deploy tele-weather-bot   --source https://source.developers.google.com/projects/vai-chover-bot/repos/WeatherBot/moveable-aliases/master/paths/  --runtime python37 --trigger-http --entry-point lambda_handler

