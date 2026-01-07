
"""
PKL Pipeline - Camera Setter
Configura atributos para camaras en escenas de animacion
"""
import maya.cmds as cmds
import re
import os
import sys


try:
    current_file = os.path.abspath(__file__)
    core_dir = os.path.dirname(current_file)
    parent_dir = os.path.dirname(core_dir)
    utils_dir = os.path.join(parent_dir, 'utils')
    
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    
    import helpers
    ensure_attribute_exists = helpers.ensure_attribute_exists
    
except ImportError as e:
    print("Warning: Could not import helpers - {}".format(e))
    
    
    def ensure_attribute_exists(obj, attr_name, attr_type='string', default_value='', lock=False):
        attr_full_name = obj + '.' + attr_name
        if not cmds.attributeQuery(attr_name, node=obj, exists=True):
            if attr_type == 'string':
                cmds.addAttr(obj, longName=attr_name, dataType='string')
                cmds.setAttr(attr_full_name, default_value, type='string')
            elif attr_type == 'bool':
                cmds.addAttr(obj, longName=attr_name, attributeType='bool', defaultValue=default_value)
        if lock:
            cmds.setAttr(attr_full_name, lock=True)


def check_camtools_pattern(camera_name):
    """
    Verifica si la camara cumple con el patron CamTools: _FR_
    Ejemplos validos: camera_FR_001_100, shot_FR_50_150_v01
    
    Returns:
        bool: True si cumple el patron, False si no
    """
    pattern = re.compile(r'_FR_\d+_\d+')
    return bool(pattern.search(camera_name))


def check_is_in_group(camera):
    """
    Verifica si la camara esta dentro de una jerarquia (tiene parent)
    
    Returns:
        bool: True si tiene parent, False si esta en root
    """
    if not camera or not cmds.objExists(camera):
        return False
    
    parent = cmds.listRelatives(camera, parent=True)
    return parent is not None


def set_camera_attributes():
    """
    FUNCION PRINCIPAL - Configura atributos de camara
    
    Crea/actualiza:
    - Hierarchy: "CAMERA" (string, locked)
    - Unreal Camera: True (bool, unlocked)
    - CamTools Logic: Auto-detectado (bool, unlocked)
    - Is in Group: Auto-detectado (bool, unlocked)
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - CAMERA SETTER")
    print("=" * 60)
    
    
    
    
    
    selection = cmds.ls(selection=True, type="transform")
    
    if not selection:
        cmds.warning("No camera selected")
        cmds.confirmDialog(
            title='No Selection',
            message='Please select a camera first.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    camera = selection[0]
    
    
    shapes = cmds.listRelatives(camera, shapes=True, fullPath=True) or []
    if not shapes or cmds.objectType(shapes[0]) != 'camera':
        cmds.warning("Selected object is not a camera")
        cmds.confirmDialog(
            title='Invalid Selection',
            message='Selected object is not a camera.\nPlease select a camera transform.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    print("\nCamera: {}".format(camera))
    
    
    
    
    
    camtools_logic = check_camtools_pattern(camera)
    is_in_group = check_is_in_group(camera)
    
    print("  CamTools Pattern: {}".format(camtools_logic))
    print("  Is in Group: {}".format(is_in_group))
    
    
    
    
    
    print("\nSetting attributes...")
    
    
    ensure_attribute_exists(camera, 'Hierarchy', 'string', 'CAMERA', lock=True)
    print("  [OK] Hierarchy = 'CAMERA' (locked)")
    
    
    ensure_attribute_exists(camera, 'UnrealCamera', 'bool', True, lock=False)
    print("  [OK] Unreal Camera = True")
    
    
    ensure_attribute_exists(camera, 'CamToolsLogic', 'bool', camtools_logic, lock=False)
    print("  [OK] CamTools Logic = {}".format(camtools_logic))
    
    
    ensure_attribute_exists(camera, 'IsInGroup', 'bool', is_in_group, lock=False)
    print("  [OK] Is in Group = {}".format(is_in_group))
    
    
    
    
    
    cmds.select(camera, replace=True)
    
    print("\n" + "=" * 60)
    print("CAMERA SET SUCCESSFULLY")
    print("=" * 60 + "\n")
    
    
    cmds.confirmDialog(
        title='Success',
        message='The following camera will be treated as the main camera for render: \n\nCamera: {}'.format(camera),
        button=['OK'],
        icon='information'
    )
    

    return True
