from multiprocessing import Queue


class BaseListener:
    def __init__(self, event_queue: Queue):
        self.event_queue = event_queue

    def start(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def resume(self):
        raise NotImplementedError()

    def join(self):
        raise NotImplementedError()

    def subscribe_event(self, event):
        pass
