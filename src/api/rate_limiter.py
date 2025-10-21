import time

class RateLimiter:
    """Ограничитель частоты запросов"""

    def __init__(self, delay: float = 0.34):
        self.last_request_time = 0
        self.delay = delay

    def wait_if_needed(self):
        """Ждет если нужно соблюсти лимит"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()
