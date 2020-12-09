import pika
import json
import requests


def emit_user_creation(username, uuid):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbit"))
    channel = connection.channel()

    data = {"username": username, "uuid": uuid}

    channel.queue_declare(queue='user_create', durable=True)
    channel.basic_publish(exchange='', routing_key='user_create', body=json.dumps(data))

    connection.close()

    # Start User consumers by this ping
    requests.get("http://user:8080/users")
    