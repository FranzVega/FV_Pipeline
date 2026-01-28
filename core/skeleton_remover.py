# -*- coding: utf-8 -*-
"""
PKL Pipeline - Skeleton Remover
Desmarca esqueletos como exportables a FBX
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
    
except ImportError as e:
    print("Warning: Could not import helpers - {}".format(e))


def remove_skeleton_exportable():
    """
    FUNCION PRINCIPAL - Desmarca esqueleto como exportable
    
    Valida:
    - Debe haber seleccion
    - La seleccion debe ser un joint
    - El atributo FBX_exportable debe existir
    
    Desactiva:
    - FBX_exportable: False (bool)
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - SKELETON REMOVER")
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
    # 2. Verificar si tiene el atributo
    # ===============================
    
    if not cmds.attributeQuery('FBX_exportable', node=joint, exists=True):
        cmds.warning("Skeleton was not previously marked as exportable")
        cmds.confirmDialog(
            title='Attribute Not Found',
            message='The skeleton was not previously marked as exportable.\n\nPlease use "Mark Skeleton" first.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    # ===============================
    # 3. Verificar estado actual
    # ===============================
    
    current_value = cmds.getAttr(joint + '.FBX_exportable')
    
    if not current_value:
        # Ya esta desactivado
        print("\n  [INFO] FBX_exportable already disabled")
        
        cmds.confirmDialog(
            title='Already Disabled',
            message='The skeleton wont be exported.\n\nFBX_exportable is already disabled for:\n\n{}'.format(joint),
            button=['OK'],
            icon='information'
        )
        return True
    
    # ===============================
    # 4. Desactivar atributo
    # ===============================
    
    print("\nDisabling attribute...")
    
    cmds.setAttr(joint + '.FBX_exportable', False)
    print("  [OK] FBX_exportable = False")
    
    # ===============================
    # 5. Seleccionar joint final
    # ===============================
    
    cmds.select(joint, replace=True)
    
    print("\n" + "=" * 60)
    print("SKELETON UNMARKED SUCCESSFULLY")
    print("=" * 60 + "\n")
    
    # Mensaje de confirmacion
    cmds.confirmDialog(
        title='Success',
        message='The skeleton wont be exported.\n\nFBX_exportable disabled for:\n\n{}'.format(joint),
        button=['OK'],
        icon='information'
    )
    
    return True