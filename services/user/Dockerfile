FROM python:3.9.0-buster

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip3 install -r requirements.txt

ENV FLASK_APP=app.py \
    FLASK_DEBUG=1

CMD flask run --port=8080 --host="0.0.0.0"