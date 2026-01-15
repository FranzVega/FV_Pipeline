# -*- coding: utf-8 -*-
"""
PKL Pipeline - Group Creator
Crea grupos MASTER con atributos desde el nombre del archivo
"""
import maya.cmds as cmds
import maya.mel as mm
import re
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
    set_locked_attribute = helpers.set_locked_attribute
    
except ImportError as e:
    print("Warning: Could not import helpers - {}".format(e))
    
    # Fallback
    def set_locked_attribute(obj, attr_name, value):
        attr_full = obj + '.' + attr_name
        if not cmds.attributeQuery(attr_name, node=obj, exists=True):
            cmds.addAttr(obj, longName=attr_name, dataType='string')
        cmds.setAttr(attr_full, value, type='string')
        cmds.setAttr(attr_full, lock=True)


def create_main_group():
    """
    FUNCION PRINCIPAL - Crea grupo MASTER desde nombre de archivo
    Organiza Assets (CH y PR) creando el MASTER_GRP con atributos.
    SOLO funciona en escenas de MODEL o RIG.
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - GROUP CREATOR")
    print("=" * 60)
    
    # 1. Obtener datos del archivo
    ruta_completa = cmds.file(query=True, sceneName=True)
    
    if not ruta_completa:
        cmds.warning("Please save the scene before running this tool")
        cmds.confirmDialog(
            title='Scene Not Saved',
            message='Please save the scene before running this tool.',
            button=['OK'],
            icon='warning'
        )
        return False

    nombre_archivo = os.path.basename(ruta_completa)
    nombre_base = os.path.splitext(nombre_archivo)[0]
    
    print("\nFile: {}".format(nombre_archivo))

    # 2. VALIDACION: Solo permite model o rig
    id_match = re.search(r"(rig|textures|model)", nombre_base, re.IGNORECASE)
    
    if not id_match:
        cmds.warning("Scene name must contain 'model', 'rig', or 'textures'")
        cmds.confirmDialog(
            title='Invalid Scene Type',
            message='This option only works on MODEL or RIG scenes.\n\n'
                    'Example: CH_hero_model_v01.ma',
            button=['OK'],
            icon='warning'
        )
        return False
    
    found = id_match.group(1).lower()
    id_val = "RIG" if found == "textures" else found.upper()
    
    # Validacion adicional: rechazar escenas de animacion
    if re.search(r"_anim_", nombre_base, re.IGNORECASE):
        cmds.warning("Cannot run on animation scenes")
        cmds.confirmDialog(
            title='Invalid Scene Type',
            message='This option does not work on ANIMATION scenes.\n\n'
                    'Please use this tool only on:\n'
                    '  - MODEL scenes\n'
                    '  - RIG scenes',
            button=['OK'],
            icon='warning'
        )
        return False
    
    print("  Scene Type: {} (valid)".format(id_val))

    # 3. Extraccion de datos con Regex
    
    # Categoria (CH, PR, etc)
    cat_match = re.search(r"^([a-zA-Z]+)_", nombre_base)
    category_val = cat_match.group(1).upper() if cat_match else "UKN"
    print("  Category: {}".format(category_val))

    # Nombre del Asset
    name_match = re.search(r"^[a-zA-Z]+_([a-zA-Z]+)_\d+_", nombre_base)
    if name_match:
        raw_name = name_match.group(1)
        name_val_attr = raw_name.capitalize()
        name_val_group = raw_name.upper()
    else:
        name_val_attr = "Unknown"
        name_val_group = "UNKNOWN"
    
    print("  Name: {}".format(name_val_attr))
    print("  ID: {}".format(id_val))

    # 4. Construccion del Master Group
    nombre_grupo_final = "{}_{}_{}_MASTER_GRP".format(
        category_val, name_val_group, id_val
    )
    
    print("\nProcessing group: {}".format(nombre_grupo_final))

    # 5. Verificar si existe el grupo
    if cmds.objExists(nombre_grupo_final):
        print("  Group already exists. Updating attributes...")
        master_grp = nombre_grupo_final
        
        # Agregar/actualizar atributos usando helpers
        print("  Verifying/updating attributes...")
        set_locked_attribute(master_grp, "Hierarchy", "{Name}_#")
        set_locked_attribute(master_grp, "Category", category_val)
        set_locked_attribute(master_grp, "Name", name_val_attr)
        set_locked_attribute(master_grp, "ID", id_val)
        
        cmds.select(master_grp, replace=True)
        
        print("\n" + "=" * 60)
        print("ATTRIBUTES UPDATED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
        # Actualizar Attribute Editor
        try:
            mm.eval('updateAE ' + master_grp)
        except:
            pass
        
        return True

    # 6. Si no existe, crear el grupo
    cmds.select(all=True)
    seleccion = cmds.ls(selection=True)
    
    # Filtrar objetos que no queremos (camaras, lights, etc)
    to_group = []
    for obj in seleccion:
        obj_type = cmds.objectType(obj)
        if obj_type == 'transform':
            # Verificar que no sea camara o luz
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            if shapes:
                shape_type = cmds.objectType(shapes[0])
                if shape_type in ['camera', 'light']:
                    continue
            to_group.append(obj)
    
    if not to_group:
        cmds.warning("No valid objects to group")
        cmds.confirmDialog(
            title='No Objects Found',
            message='No valid objects found to group.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    print("  Grouping {} objects...".format(len(to_group)))

    cmds.select(to_group, replace=True)
    master_grp = cmds.group(name=nombre_grupo_final)

    # 7. Crear atributos usando helpers
    print("  Adding attributes...")
    set_locked_attribute(master_grp, "Hierarchy", "{Name}_#")
    set_locked_attribute(master_grp, "Category", category_val)
    set_locked_attribute(master_grp, "Name", name_val_attr)
    set_locked_attribute(master_grp, "ID", id_val)

    cmds.select(master_grp, replace=True)
    
    print("\n" + "=" * 60)
    print("GROUP CREATED SUCCESSFULLY")
    print("=" * 60 + "\n")
    
    # Actualizar Attribute Editor
    try:
        mm.eval('updateAE ' + master_grp)
    except:
        pass
    
    return True