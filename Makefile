PROJECT = tele_weather_bot
VIRTUAL_ENV = env
SOURCE_DIR = $(shell pwd)

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
	@echo "Now type 'source ./env/bin/activate' and start coding!"

clean_package:
	rm -rf ./package/*

build_package_tmp:
	mkdir -p ./package/tmp/
	cp -a ./$(PROJECT) ./package/tmp/
	cp main.py ./package/tmp/
	cp requirements.txt ./package/tmp/
	@test -f .env.yaml && cp .env.yaml ./package/tmp/ || echo yaml not present

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

deploy_gcloud_without_commit:
	@test -f .env.yaml && gcloud functions deploy tele-weather-bot --entry-point lambda_handler --source $(SOURCE_DIR) --env-vars-file .env.yaml --runtime python37 --trigger-http || echo yaml not present, deploying without it;
	@test -f .env.yaml || gcloud functions deploy tele-weather-bot --entry-point lambda_handler --source $(SOURCE_DIR) --runtime python37 --trigger-http;

deploy_gcloud_release:
	@test -f .env.yaml && gcloud functions deploy tele-weather-bot --project vai-chover-bot --source https://source.developers.google.com/projects/vai-chover-bot/repos/WeatherBot/moveable-aliases/master/paths/ --env-vars-file .env.yaml --runtime python37 --trigger-http --entry-point lambda_handler || echo yaml not present, deploying without it; 
	@test -f .env.yaml || gcloud functions deploy tele-weather-bot --project vai-chover-bot --source https://source.developers.google.com/projects/vai-chover-bot/repos/WeatherBot/moveable-aliases/master/paths/ --runtime python37 --trigger-http --entry-point lambda_handler; 

deploy_gcloud_testing:
	@test -f .env.yaml && gcloud functions deploy tele-weather-bot --project vai-chover-bot --source https://source.developers.google.com/projects/vai-chover-bot/repos/WeatherBot/moveable-aliases/develop/paths/ --env-vars-file .env.yaml --runtime python37 --trigger-http --entry-point lambda_handler || echo yaml not present, deploying without it; 
	@test -f .env.yaml || gcloud functions deploy tele-weather-bot --project vai-chover-bot --source https://source.developers.google.com/projects/vai-chover-bot/repos/WeatherBot/moveable-aliases/develop/paths/ --runtime python37 --trigger-http --entry-point lambda_handler; 
