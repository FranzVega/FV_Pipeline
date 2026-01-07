# -*- coding: utf-8 -*-
"""
PKL Pipeline - Helper Functions
Funciones compartidas que se usan en multiples modulos
"""
import maya.cmds as cmds
import re
import sys

# ====== CONFIGURACION ======
PROJECT_PREFIX = 'PKL'

# ====== SCENE INFO ======

def get_scene_name():
    """Obtiene el nombre de la escena actual"""
    return cmds.file(query=True, sceneName=True, shortName=True)

def get_scene_type():
    """
    Detecta el tipo de escena basandose en patrones del nombre
    
    Returns:
        tuple: (scene_type_name, scene_type_color)
        
    Tipos posibles:
        - Animation Scene: Contiene '_anim_' o existe grupo ANIMATION
        - Modeling Scene: Contiene '_model_'
        - Rig Scene: Contiene '_rig_'
        - Texturing Scene: Contiene '_texture_' o '_textures_'
        - Layout Scene: Contiene '_layout_'
        - UNIDENTIFIED: No cumple ningun patron
    """
    scene_name = get_scene_name()
    
    # Si no hay escena guardada
    if not scene_name:
        return ("UNSAVED SCENE", [1.0, 0.6, 0.4])  # Naranja
    
    # Convertir a lowercase para busqueda
    scene_lower = scene_name.lower()
    
    # Patrones en orden de prioridad
    patterns = [
        ('_anim_', "Animation Scene", [0.4, 1.0, 0.4]),      # Verde
        ('_model_', "Modeling Scene", [0.4, 0.7, 1.0]),      # Azul
        ('_rig_', "Rig Scene", [1.0, 0.8, 0.4]),             # Amarillo
        ('_texture_', "Texturing Scene", [1.0, 0.5, 0.8]),   # Rosa
        ('_textures_', "Texturing Scene", [1.0, 0.5, 0.8]),  # Rosa
        ('_layout_', "Layout Scene", [0.7, 0.5, 1.0]),       # Purpura
    ]
    
    # Buscar patrones en el nombre
    for pattern, scene_type, color in patterns:
        if pattern in scene_lower:
            return (scene_type, color)
    
    # Verificacion adicional: si existe grupo ANIMATION -> Animation Scene
    if cmds.objExists('ANIMATION'):
        return ("Animation Scene", [0.4, 1.0, 0.4])
    
    # Si no cumple ningun patron
    return ("UNIDENTIFIED", [1.0, 0.4, 0.4])  # Rojo

def get_sq_from_scene():
    """Extrae SQ del nombre de la escena (_S01_ -> S01)"""
    scene_name = get_scene_name()
    if not scene_name:
        return 'S01'
    
    pattern = re.compile(r'_S(\d+)_')
    match = pattern.search(scene_name)
    
    if match:
        sq_number = match.group(1)
        return 'S{}'.format(sq_number)
    else:
        return 'S01'

def get_sh_from_scene():
    """Extrae SH del nombre de la escena (_SH010_ -> SH010)"""
    scene_name = get_scene_name()
    if not scene_name:
        return 'SH010'
    
    pattern = re.compile(r'_SH(\d+)_')
    match = pattern.search(scene_name)
    
    if match:
        sh_number = match.group(1)
        return 'SH{}'.format(sh_number)
    else:
        return 'SH010'

def get_export_path():
    """Construye el path de exportacion basado en SQ y SH"""
    sq = get_sq_from_scene()
    sh = get_sh_from_scene()
    return '<workspace_root>/Unreal/animation/{}_{}/{}'.format(PROJECT_PREFIX, sq, sh)

def get_scene_data():
    """
    Obtiene toda la info de la escena en un dict
    Returns: dict con 'sq', 'sh', 'export_path', 'scene_name'
    """
    return {
        'sq': get_sq_from_scene(),
        'sh': get_sh_from_scene(),
        'export_path': get_export_path(),
        'scene_name': get_scene_name()
    }

# ====== ATTRIBUTE MANAGEMENT ======

def ensure_attribute_exists(obj, attr_name, attr_type='string', default_value='', lock=False):
    """
    Crea o actualiza un atributo en un objeto
    
    Args:
        obj: Nombre del objeto
        attr_name: Nombre del atributo
        attr_type: 'string' o 'bool'
        default_value: Valor por defecto
        lock: Si True, bloquea el atributo
    """
    attr_full_name = obj + '.' + attr_name
    
    if not cmds.attributeQuery(attr_name, node=obj, exists=True):
        # Crear atributo
        if attr_type == 'string':
            cmds.addAttr(obj, longName=attr_name, dataType='string')
            cmds.setAttr(attr_full_name, default_value, type='string')
        elif attr_type == 'bool':
            cmds.addAttr(obj, longName=attr_name, attributeType='bool', defaultValue=default_value)
            cmds.setAttr(attr_full_name, default_value)
    else:
        # Actualizar atributo existente
        is_locked = cmds.getAttr(attr_full_name, lock=True)
        if is_locked:
            cmds.setAttr(attr_full_name, lock=False)
        
        if attr_type == 'string':
            current_value = cmds.getAttr(attr_full_name)
            if current_value != default_value:
                cmds.setAttr(attr_full_name, default_value, type='string')
        elif attr_type == 'bool':
            current_value = cmds.getAttr(attr_full_name)
            if current_value != default_value:
                cmds.setAttr(attr_full_name, default_value)
    
    if lock:
        cmds.setAttr(attr_full_name, lock=True)

def set_locked_attribute(obj, attr_name, value):
    """
    Crea un atributo string y lo bloquea inmediatamente
    (Alias conveniente para ensure_attribute_exists con lock=True)
    
    Args:
        obj: Nombre del objeto
        attr_name: Nombre del atributo
        value: Valor del atributo
    """
    ensure_attribute_exists(obj, attr_name, 'string', value, lock=True)

def get_attribute_value(obj, attr_name, default=None):
    """Obtiene el valor de un atributo de forma segura"""
    if cmds.objExists(obj) and cmds.attributeQuery(attr_name, node=obj, exists=True):
        return cmds.getAttr(obj + '.' + attr_name)
    return default

def has_attribute(obj, attr_name):
    """Verifica si un objeto tiene un atributo"""
    return cmds.objExists(obj) and cmds.attributeQuery(attr_name, node=obj, exists=True)

# ====== MODULE RELOAD ======

def reload_module(module_name):
    """Recarga un modulo de forma segura (Python 2/3 compatible)"""
    if module_name in sys.modules:
        try:
            reload(sys.modules[module_name])
        except NameError:
            import importlib
            importlib.reload(sys.modules[module_name])
        return True
    return False

def reload_all_modules():
    """Recarga todos los modulos del pipeline"""
    modules_to_reload = [
        'pipeline_ui',
        'scene_checker',
        'animation_organizer',
        'settings',
        'update_checker',
        'helpers'
    ]
    
    reloaded = []
    for mod in modules_to_reload:
        if reload_module(mod):
            reloaded.append(mod)
    
    if reloaded:
        print("=" * 60)
        print("PKL Pipeline - Modules Reloaded:")
        for mod in reloaded:
            print("  - {}".format(mod))
        print("=" * 60)
    
    return reloaded