# -*- coding: utf-8 -*-
"""
PKL Pipeline - Animation Organizer
Script completo para organizar escenas de animacion
"""
import maya.cmds as cmds
import sys
import os

# Importar helpers
try:
    # Asegurar que utils esta en el path
    current_file = os.path.abspath(__file__)
    core_dir = os.path.dirname(current_file)
    parent_dir = os.path.dirname(core_dir)
    utils_dir = os.path.join(parent_dir, 'utils')
    
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    
    import helpers
    
    # Importar funciones especificas
    get_sq_from_scene = helpers.get_sq_from_scene
    get_sh_from_scene = helpers.get_sh_from_scene
    get_export_path = helpers.get_export_path
    get_scene_data = helpers.get_scene_data
    ensure_attribute_exists = helpers.ensure_attribute_exists
    
except ImportError as e:
    print("Warning: Could not import helpers - {}".format(e))
    # Fallback: definir funciones basicas
    import re
    
    def get_sq_from_scene():
        return 'PKL_SQ01'
    
    def get_sh_from_scene():
        return 'SH010'
    
    def get_export_path():
        return '<workspace_root>/Unreal/animation/PKL_SQ01/SH010'
    
    def get_scene_data():
        return {'sq': 'PKL_SQ01', 'sh': 'SH010', 'export_path': get_export_path()}
    
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


# ====== FUNCIONES ESPECIFICAS DE ORGANIZACION ======

def find_objects_with_hierarchy_attribute(hierarchy_value):
    """Busca objetos con atributo Hierarchy = valor especifico"""
    objects_with_hierarchy = []
    all_transforms = cmds.ls(type='transform')
    
    for obj in all_transforms:
        if cmds.attributeQuery('Hierarchy', node=obj, exists=True):
            current_value = cmds.getAttr(obj + '.Hierarchy')
            if current_value == hierarchy_value:
                objects_with_hierarchy.append(obj)
    
    return objects_with_hierarchy

def get_next_available_number(base_name):
    """Encuentra el siguiente numero disponible para un nombre"""
    number = 1
    while cmds.objExists('{}_{}'.format(base_name, number)):
        number += 1
    return number

def organize_hierarchy_recursive(parent_name):
    """Organiza jerarquia recursivamente"""
    if not cmds.objExists(parent_name):
        return
    
    objects_to_parent = find_objects_with_hierarchy_attribute(parent_name)
    
    for obj in objects_to_parent:
        if obj != parent_name:
            # Condicion especial para camaras: verificar IsInGroup
            if parent_name == 'CAMERA':
                if cmds.attributeQuery('IsInGroup', node=obj, exists=True):
                    is_in_group = cmds.getAttr(obj + '.IsInGroup')
                    if is_in_group:
                        print('  "{}" skipped (IsInGroup = True)'.format(obj))
                        continue
            
            current_parent = cmds.listRelatives(obj, parent=True)
            if not current_parent or current_parent[0] != parent_name:
                cmds.parent(obj, parent_name)
                print('  "{}" parenteado a "{}"'.format(obj, parent_name))
            
            organize_hierarchy_recursive(obj)

def create_child_group(parent, group_name, hierarchy_value='ANIMATION'):
    """Crea un grupo hijo con Hierarchy"""
    if cmds.objExists(group_name):
        current_parent = cmds.listRelatives(group_name, parent=True)
        if not current_parent or current_parent[0] != parent:
            cmds.parent(group_name, parent)
        return group_name
    
    child_group = cmds.group(empty=True, name=group_name)
    ensure_attribute_exists(child_group, 'Hierarchy', 'string', hierarchy_value, lock=True)
    cmds.parent(child_group, parent)
    
    return child_group

def setup_camera_group(scene_data):
    """
    Configura el grupo CAMERA con sus atributos especiales
    Incluye ExportedName y Path con frame range
    """
    if not cmds.objExists('CAMERA'):
        return False
    
    # Obtener frame range del timeline
    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)
    
    # Construir ExportedName: CAM_PKL_S1_SH010_001_100
    exported_name = "CAM_{}_{}_{}_{}" .format(
        scene_data['sq'], 
        scene_data['sh'],
        int(start),
        int(end)
    )
    
    # Construir Path: <workspace_root>/Unreal/animation/PKL_S1/SH010/Camera
    # Extraer el base path sin el ultimo segmento
    base_export_path = scene_data['export_path']
    path_value = '{}/Camera'.format(base_export_path)
    
    # FORZAR actualizacion de atributos (unlock -> set -> lock)
    
    # ExportedName
    if cmds.attributeQuery('ExportedName', node='CAMERA', exists=True):
        cmds.setAttr('CAMERA.ExportedName', lock=False)
        cmds.setAttr('CAMERA.ExportedName', exported_name, type='string')
        cmds.setAttr('CAMERA.ExportedName', lock=True)
    else:
        cmds.addAttr('CAMERA', longName='ExportedName', dataType='string')
        cmds.setAttr('CAMERA.ExportedName', exported_name, type='string')
        cmds.setAttr('CAMERA.ExportedName', lock=True)
    
    # Path
    if cmds.attributeQuery('Path', node='CAMERA', exists=True):
        cmds.setAttr('CAMERA.Path', lock=False)
        cmds.setAttr('CAMERA.Path', path_value, type='string')
        cmds.setAttr('CAMERA.Path', lock=True)
    else:
        cmds.addAttr('CAMERA', longName='Path', dataType='string')
        cmds.setAttr('CAMERA.Path', path_value, type='string')
        cmds.setAttr('CAMERA.Path', lock=True)
    
    # Exportable
    if cmds.attributeQuery('Exportable', node='CAMERA', exists=True):
        cmds.setAttr('CAMERA.Exportable', lock=False)
        cmds.setAttr('CAMERA.Exportable', True)
    else:
        cmds.addAttr('CAMERA', longName='Exportable', attributeType='bool', defaultValue=True)
        cmds.setAttr('CAMERA.Exportable', True)
    
    print('  CAMERA group configured:')
    print('    ExportedName: {}'.format(exported_name))
    print('    Path: {}'.format(path_value))
    
    return True

def update_dynamic_groups():
    """Actualiza grupos dinamicos existentes"""
    scene_data = get_scene_data()
    all_transforms = cmds.ls(type='transform')
    
    for obj in all_transforms:
        # Saltar el grupo CAMERA - tiene su propia logica
        if obj == 'CAMERA':
            continue
            
        if cmds.attributeQuery('ExportedName', node=obj, exists=True):
            if cmds.attributeQuery('Hierarchy', node=obj, exists=True):
                category = cmds.getAttr(obj + '.Hierarchy')
                
                exported_name = '{}_{}_{}_{}' .format(
                    category, obj, 
                    scene_data['sq'], scene_data['sh']
                )
                ensure_attribute_exists(obj, 'ExportedName', 'string', exported_name, lock=True)
                
                path_value = '{}/{}'.format(scene_data['export_path'], category)
                ensure_attribute_exists(obj, 'Path', 'string', path_value, lock=True)
                
                ensure_attribute_exists(obj, 'Exportable', 'bool', True, lock=False)

def process_template_groups():
    """Procesa grupos template y crea grupos dinamicos"""
    scene_data = get_scene_data()
    all_transforms = cmds.ls(type='transform')
    processed = []
    
    for obj in all_transforms:
        has_category = cmds.attributeQuery('Category', node=obj, exists=True)
        has_hierarchy = cmds.attributeQuery('Hierarchy', node=obj, exists=True)
        has_name = cmds.attributeQuery('Name', node=obj, exists=True)
        
        if has_category and has_hierarchy and has_name:
            category = cmds.getAttr(obj + '.Category')
            hierarchy_pattern = cmds.getAttr(obj + '.Hierarchy')
            name_value = cmds.getAttr(obj + '.Name')
            
            if '{Name}_#' in hierarchy_pattern:
                current_parent = cmds.listRelatives(obj, parent=True)
                
                skip = False
                if current_parent:
                    parent_name = current_parent[0]
                    if parent_name.startswith(name_value + '_'):
                        suffix = parent_name.replace(name_value + '_', '')
                        if suffix.isdigit():
                            if cmds.attributeQuery('Hierarchy', node=parent_name, exists=True):
                                parent_hierarchy = cmds.getAttr(parent_name + '.Hierarchy')
                                if parent_hierarchy == category:
                                    skip = True
                
                if not skip:
                    next_number = get_next_available_number(name_value)
                    new_group_name = '{}_{}'.format(name_value, next_number)
                    new_group = cmds.group(empty=True, name=new_group_name)
                    
                    ensure_attribute_exists(new_group, 'Hierarchy', 'string', category, lock=True)
                    
                    exported_name = '{}_{}_{}_{}' .format(
                        category, new_group_name, 
                        scene_data['sq'], scene_data['sh']
                    )
                    ensure_attribute_exists(new_group, 'ExportedName', 'string', exported_name, lock=True)
                    
                    path_value = '{}/{}'.format(scene_data['export_path'], category)
                    ensure_attribute_exists(new_group, 'Path', 'string', path_value, lock=True)
                    ensure_attribute_exists(new_group, 'Exportable', 'bool', True, lock=False)
                    
                    cmds.parent(obj, new_group)
                    processed.append(new_group_name)
                    
                    print('  Grupo "{}" creado desde template "{}"'.format(new_group_name, obj))
    
    return processed


# ====== FUNCION PRINCIPAL ======

def organize_animation():
    """
    FUNCION PRINCIPAL - Organiza toda la escena de animacion
    Esta es la funcion que llama la UI
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - ANIMATION ORGANIZER")
    print("=" * 60)
    
    # Validar que estamos en una escena de animacion
    scene_name = cmds.file(query=True, sceneName=True, shortName=True)
    
    if not scene_name:
        cmds.warning("Scene must be saved before organizing")
        cmds.confirmDialog(
            title='Scene Not Saved',
            message='Please save the scene before organizing.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    if '_anim_' not in scene_name.lower():
        cmds.warning("This is not an animation scene")
        cmds.confirmDialog(
            title='Not an Animation Scene',
            message='Currently this is not an Animation Scene \n or is not in the pipeline workflow.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    # Obtener datos de la escena (usando helpers)
    scene_data = get_scene_data()
    
    print("\nDatos de la escena:")
    print("  SQ: {}".format(scene_data['sq']))
    print("  SH: {}".format(scene_data['sh']))
    print("  Export Path: {}".format(scene_data['export_path']))
    
    # Crear o actualizar grupo ANIMATION
    print("\n1. Configurando grupo ANIMATION...")
    if cmds.objExists('ANIMATION'):
        print("  Grupo ANIMATION ya existe, actualizando...")
        animation_group = 'ANIMATION'
    else:
        animation_group = cmds.group(empty=True, name='ANIMATION')
        print("  Grupo ANIMATION creado")
    
    ensure_attribute_exists(animation_group, 'ExportedPath', 'string', scene_data['export_path'], lock=True)
    ensure_attribute_exists(animation_group, 'SQ', 'string', scene_data['sq'], lock=True)
    ensure_attribute_exists(animation_group, 'SH', 'string', scene_data['sh'], lock=True)
    
    # Crear grupos hijos
    print("\n2. Creando grupos hijos...")
    create_child_group(animation_group, 'CH', 'CH')
    create_child_group(animation_group, 'PR', 'PR')
    create_child_group(animation_group, 'CAMERA', 'CAMERA')
    print("  Grupos CH, PR y CAMERA verificados")
    
    # Configurar grupo CAMERA con sus atributos especiales
    print("\n3. Configurando atributos de CAMERA...")
    setup_camera_group(scene_data)
    
    # Actualizar grupos dinamicos
    print("\n4. Actualizando grupos dinamicos...")
    update_dynamic_groups()
    
    # Procesar templates
    print("\n5. Procesando grupos template...")
    templates = process_template_groups()
    if templates:
        print("  {} grupos dinamicos creados".format(len(templates)))
    
    # Organizar jerarquia
    print("\n6. Organizando jerarquia...")
    organize_hierarchy_recursive('ANIMATION')
    organize_hierarchy_recursive('CH')
    organize_hierarchy_recursive('PR')
    organize_hierarchy_recursive('CAMERA')
    
    print("\n" + "=" * 60)
    print("ORGANIZACION COMPLETADA CON EXITO")
    print("=" * 60 + "\n")
    
    return True