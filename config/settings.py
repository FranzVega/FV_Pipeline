# -*- coding: utf-8 -*-
"""
PKL Pipeline - Settings & Version Control
Configuracion central del pipeline
"""

# Version del pipeline (IMPORTANTE para updates desde GitHub)
VERSION = "1.0.0"

# GitHub Repository
REPO_OWNER = "FranzVega"
REPO_NAME = "FV_Pipeline"
REPO_BRANCH = "main"  # o "master" dependiendo de tu rama principal

# URLs
REPO_URL = "https://github.com/{}/{}".format(REPO_OWNER, REPO_NAME)
REPO_API = "https://api.github.com/repos/{}/{}/contents/pkl_pipeline".format(REPO_OWNER, REPO_NAME)
REPO_RAW = "https://raw.githubusercontent.com/{}/{}/{}/pkl_pipeline".format(REPO_OWNER, REPO_NAME, REPO_BRANCH)

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
        'owner': REPO_OWNER,
        'name': REPO_NAME,
        'branch': REPO_BRANCH,
        'url': REPO_URL,
        'api': REPO_API,
        'raw': REPO_RAW,
        'version': VERSION
    }