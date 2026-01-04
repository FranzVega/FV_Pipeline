# -*- coding: utf-8 -*-
"""
PKL Pipeline - Settings & Version Control
Configuracion central del pipeline
"""

# Version del pipeline (IMPORTANTE para updates desde GitHub)
VERSION = "1.0.0"
REPO_URL = "https://github.com/FranzVega/FV_Pipeline"
REPO_API = "https://api.github.com/repos/FranzVega/FV_Pipeline/contents/pkl_pipeline"

# Configuraciones generales
PIPELINE_NAME = "PKL Pipeline"
AUTHOR = "Franz Vega"

# Paths relativos (se calculan automaticamente)
import os
PIPELINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_PATH = os.path.join(PIPELINE_ROOT, "ui")
CORE_PATH = os.path.join(PIPELINE_ROOT, "core")
ICONS_PATH = os.path.join(PIPELINE_ROOT, "icons")

def get_version():
    """Retorna la version actual"""
    return VERSION

def get_repo_info():
    """Retorna info del repositorio"""
    return {
        'url': REPO_URL,
        'api': REPO_API,
        'version': VERSION
    }