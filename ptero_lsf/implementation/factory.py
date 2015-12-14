from ptero_lsf.factories.bigfactory import BigFactory
import os


__all__ = ['Factory']


class Factory(BigFactory):
    def base_dir(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
