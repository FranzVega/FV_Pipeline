# -*- coding: utf-8 -*-
"""
PKL Pipeline - Main Package
Pipeline de animacion para Maya
"""

from config import VERSION

__version__ = VERSION
__author__ = "Franz Vega"

# Exponer funcion principal
from ui.pipeline_ui import main

__all__ = ['main', '__version__']

print("PKL Pipeline v{} loaded".format(__version__))