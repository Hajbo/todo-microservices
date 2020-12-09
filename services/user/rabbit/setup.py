from .consumer import ConsumerThread
from .callbacks import create_user_callback

consumers = [
    ConsumerThread(
        host="rabbit",
        queue_name="user_create",
        callback_func=create_user_callback,
    )
]


def run_consumers():
    for thread in consumers:
        thread.start()
