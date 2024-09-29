import abc

class Service(abc.ABC):
    @abc.abstractmethod
    def init_app(self, app):
        pass