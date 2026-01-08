# -*- coding: utf-8 -*-
"""
PKL Pipeline - Skeleton Marker
Marca esqueletos como exportables a FBX
"""
import maya.cmds as cmds
import sys
import os

# Importar helpers
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
    
    # Fallback
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


def mark_skeleton_exportable():
    """
    FUNCION PRINCIPAL - Marca esqueleto como exportable
    
    Valida:
    - Debe haber seleccion
    - La seleccion debe ser un joint
    
    Crea:
    - FBX_exportable: True (bool, unlocked)
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - SKELETON MARKER")
    print("=" * 60)
    
    # ===============================
    # 1. Validar seleccion
    # ===============================
    
    selection = cmds.ls(selection=True, type="joint")
    
    if not selection:
        cmds.warning("No joint selected")
        cmds.confirmDialog(
            title='Invalid Selection',
            message='Please select a joint (skeleton root).',
            button=['OK'],
            icon='warning'
        )
        return False
    
    joint = selection[0]
    
    print("\nJoint selected: {}".format(joint))
    
    # ===============================
    # 2. Crear atributo
    # ===============================
    
    print("\nSetting attribute...")
    
    ensure_attribute_exists(joint, 'FBX_exportable', 'bool', True, lock=False)
    print("  [OK] FBX_exportable = True")
    
    # ===============================
    # 3. Seleccionar joint final
    # ===============================
    
    cmds.select(joint, replace=True)
    
    print("\n" + "=" * 60)
    print("SKELETON MARKED SUCCESSFULLY")
    print("=" * 60 + "\n")
    
    # Mensaje de confirmacion
    cmds.confirmDialog(
        title='Success',
        message='Skeleton marked as exportable:\n\n{}'.format(joint),
        button=['OK'],
        icon='information'
    )
    
    return True