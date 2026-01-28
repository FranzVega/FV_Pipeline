# -*- coding: utf-8 -*-
"""
PKL Pipeline - Camera Cleaner
Desactiva el atributo Unreal Camera de camaras en el grupo CAMERA
"""
import maya.cmds as cmds
import os
import sys

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


def find_cameras_in_group():
    """
    Busca camaras dentro del grupo CAMERA
    
    Returns:
        list: Lista de transforms de camaras encontradas
    """
    cameras = []
    
    if not cmds.objExists('CAMERA'):
        return cameras
    
    # Obtener todos los hijos del grupo CAMERA
    children = cmds.listRelatives('CAMERA', allDescendents=True, type='transform') or []
    
    for child in children:
        # Verificar si es una camara
        shapes = cmds.listRelatives(child, shapes=True, fullPath=True) or []
        if shapes and cmds.objectType(shapes[0]) == 'camera':
            cameras.append(child)
    
    return cameras


def clean_camera():
    """
    FUNCION PRINCIPAL - Desactiva Unreal Camera en camaras del grupo CAMERA
    
    Busca camaras en el grupo CAMERA y desactiva el atributo UnrealCamera
    Si no existe el atributo, muestra warning
    Si ya esta desactivado, muestra confirmacion
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - CAMERA CLEANER")
    print("=" * 60)
    
    # ===============================
    # 1. Verificar que existe grupo CAMERA
    # ===============================
    
    if not cmds.objExists('CAMERA'):
        cmds.warning("CAMERA group does not exist")
        cmds.confirmDialog(
            title='Group Not Found',
            message='CAMERA group does not exist in the scene.\nPlease organize the scene first.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    # ===============================
    # 2. Buscar camaras en el grupo
    # ===============================
    
    cameras = find_cameras_in_group()
    
    if not cameras:
        cmds.warning("No cameras found in CAMERA group")
        cmds.confirmDialog(
            title='No Cameras Found',
            message='No cameras found inside CAMERA group.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    print("\nCameras found: {}".format(len(cameras)))
    for cam in cameras:
        print("  - {}".format(cam))
    
    # ===============================
    # 3. Procesar cada camara
    # ===============================
    
    cameras_cleaned = []
    cameras_already_disabled = []
    cameras_without_attribute = []
    
    for camera in cameras:
        # Verificar si tiene el atributo UnrealCamera
        if not cmds.attributeQuery('UnrealCamera', node=camera, exists=True):
            cameras_without_attribute.append(camera)
            print("\n  [WARNING] {}: UnrealCamera attribute does not exist".format(camera))
            continue
        
        # Obtener valor actual
        current_value = cmds.getAttr(camera + '.UnrealCamera')
        
        if not current_value:
            # Ya esta desactivado
            cameras_already_disabled.append(camera)
            print("\n  [INFO] {}: Already disabled".format(camera))
        else:
            # Desactivar
            cmds.setAttr(camera + '.UnrealCamera', False)
            cameras_cleaned.append(camera)
            print("\n  [OK] {}: UnrealCamera disabled".format(camera))
    
    # ===============================
    # 4. Mensajes finales
    # ===============================
    
    # Si alguna camara no tenia el atributo
    if cameras_without_attribute:
        cmds.warning("Some cameras were not previously set as exportable")
        message = "The following cameras were not previously selected as exportable cameras:\n\n"
        for cam in cameras_without_attribute:
            message += "- {}\n".format(cam)
        message += "\nPlease use 'Set Selected Camera' first."
        
        cmds.confirmDialog(
            title='Camera Not Set',
            message=message,
            button=['OK'],
            icon='warning'
        )
        return False
    
    # Si todas ya estaban desactivadas
    if cameras_already_disabled and not cameras_cleaned:
        message = "The camera wont be exported.\n\n"
        message += "UnrealCamera attribute is already disabled for:\n\n"
        for cam in cameras_already_disabled:
            message += "- {}\n".format(cam)
        
        cmds.confirmDialog(
            title='Already Disabled',
            message=message,
            button=['OK'],
            icon='information'
        )
        return True
    
    # Si se desactivaron camaras exitosamente
    if cameras_cleaned:
        print("\n" + "=" * 60)
        print("CAMERAS CLEANED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
        message = "The camera wont be exported.\n\n"
        message += "UnrealCamera disabled for:\n\n"
        for cam in cameras_cleaned:
            message += "- {}\n".format(cam)
        
        if cameras_already_disabled:
            message += "\nAlready disabled:\n\n"
            for cam in cameras_already_disabled:
                message += "- {}\n".format(cam)
        
        cmds.confirmDialog(
            title='Success',
            message=message,
            button=['OK'],
            icon='information'
        )
        
        return True
    
    return False