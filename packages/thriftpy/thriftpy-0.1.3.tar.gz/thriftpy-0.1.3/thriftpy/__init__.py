# -*- coding: utf-8 -*-

__all__ = ["install_import_hook", "remove_import_hook", "load"]


from .hook import install_import_hook, remove_import_hook
from .parser import load
