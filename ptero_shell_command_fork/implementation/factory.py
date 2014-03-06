from . import backend

__all__ = ['Factory']


class Factory(object):
    def __init__(self):
        self._initialized = False

    def create_backend(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialize()
            self._initialzied = True

        return backend.Backend()

    def _initialize(self):
        pass
