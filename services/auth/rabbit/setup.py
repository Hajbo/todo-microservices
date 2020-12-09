from .consumer import ConsumerThread
from .callbacks import delete_user_callback

consumers = [
    ConsumerThread(
        host="rabbit",
        queue_name="auth_user_delete",
        callback_func=delete_user_callback,
    )
]


def run_consumers():
    for thread in consumers:
        thread.start()
