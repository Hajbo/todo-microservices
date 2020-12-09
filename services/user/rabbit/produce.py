import pika
import json


def emit_user_deletion(uuid, jwt):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbit"))
    channel = connection.channel()

    data = {"uuid": uuid, "jwt": jwt}

    channel.queue_declare(queue='auth_user_delete', durable=True)
    channel.basic_publish(exchange='', routing_key='auth_user_delete', body=json.dumps(data))

    channel.queue_declare(queue='todo_user_delete', durable=True)
    channel.basic_publish(exchange='', routing_key='todo_user_delete', body=json.dumps(data))

    connection.close()
