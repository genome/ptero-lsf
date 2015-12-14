from ptero_common.factories.bigfactory import BigFactory
from ptero_lsf.implementation import backend as _backend
import os


__all__ = ['Factory']


class Factory(BigFactory):

    @property
    def backend(self):
        return  _backend.Backend

    def base_dir(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
