From alpine:latest
Run apk add --no-cache python3-dev
Run pip3 install --upgrade pip
Workdir /service
COPY ./app /service
Run pip3 install -r requirements.txt
expose 5000
workdir /service/demo/api
cmd python3 dentist.py
