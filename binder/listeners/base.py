class BaseListener:
    def __init__(self, handler):
        self.handler = handler

    def start(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def resume(self):
        raise NotImplementedError()

    def subscribe_event(self, event):
        pass
