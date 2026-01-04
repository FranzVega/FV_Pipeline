# -*- coding: utf-8 -*-
"""
PKL Pipeline - Helper Functions
Funciones de utilidad para el pipeline
"""
import sys

def reload_module(module_name):
    """
    Recarga un modulo de forma segura (Python 2/3 compatible)
    """
    if module_name in sys.modules:
        try:
            # Python 2
            reload(sys.modules[module_name])
        except NameError:
            # Python 3
            import importlib
            importlib.reload(sys.modules[module_name])
        return True
    return False

def reload_all_modules():
    """
    Recarga todos los modulos del pipeline
    Util despues de actualizar desde GitHub
    """
    modules_to_reload = [
        'pipeline_ui',
        'core.scene_checker',
        'core.animation_organizer',
        'config.settings'
    ]
    
    reloaded = []
    for mod in modules_to_reload:
        if reload_module(mod):
            reloaded.append(mod)
    
    print("Reloaded modules: {}".format(", ".join(reloaded)))
    return reloaded

def check_for_updates():
    """
    Placeholder para chequear updates desde GitHub
    Lo implementaremos despues si quieres
    """
    print("Checking for updates...")
    print("(Feature coming soon)")
    return None