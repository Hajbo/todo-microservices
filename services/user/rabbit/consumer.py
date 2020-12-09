import pika
import threading


class ConsumerThread(threading.Thread):
    def __init__(self, host, queue_name, callback_func, *args, **kwargs):
        super(ConsumerThread, self).__init__(*args, **kwargs)

        self._host = host
        self._queue_name = queue_name
        self._callback_func = callback_func

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._host))
        channel = connection.channel()

        result = channel.queue_declare(queue=self._queue_name, durable=True)

        channel.basic_consume(queue=self._queue_name, on_message_callback=self.callback)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self._callback_func(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)
