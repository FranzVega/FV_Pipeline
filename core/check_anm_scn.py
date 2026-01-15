# -*- coding: utf-8 -*-
"""
PKL Pipeline - Animation Scene Checker
Verifica que todos los assets referenciados sean archivos _MASTER
"""
import maya.cmds as cmds
import os
import sys
import re

# Importar helpers
try:
    current_file = os.path.abspath(__file__)
    core_dir = os.path.dirname(current_file)
    parent_dir = os.path.dirname(core_dir)
    utils_dir = os.path.join(parent_dir, 'utils')
    
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    
    import helpers
    get_scene_name = helpers.get_scene_name
    
except ImportError as e:
    print("Warning: Could not import helpers - {}".format(e))
    
    # Fallback
    def get_scene_name():
        return cmds.file(query=True, sceneName=True, shortName=True)


def get_all_references():
    """
    Obtiene todas las referencias en la escena
    
    Returns:
        list: Lista de reference nodes
    """
    references = cmds.ls(type='reference')
    
    # Filtrar referencias validas (excluir sharedReferenceNode, etc)
    valid_refs = []
    for ref in references:
        if ref != 'sharedReferenceNode' and ref != '_UNKNOWN_REF_NODE_':
            valid_refs.append(ref)
    
    return valid_refs


def get_reference_file_path(reference_node):
    """
    Obtiene el path del archivo referenciado
    
    Args:
        reference_node: Nombre del reference node
        
    Returns:
        str: Path completo del archivo referenciado, o None si hay error
    """
    try:
        file_path = cmds.referenceQuery(reference_node, filename=True)
        return file_path
    except:
        return None


def check_reference_is_master(reference_node):
    """
    Verifica si un archivo referenciado cumple con los requisitos:
    1. Debe tener prefijo CH_ o PRP_
    2. Debe tener sufijo _MASTER
    
    Args:
        reference_node: Nombre del reference node
        
    Returns:
        dict: {
            'node': reference_node,
            'file_path': path completo,
            'file_name': nombre del archivo,
            'is_valid': True/False,
            'reason': razon si es invalido,
            'prefix': prefijo detectado (CH, PRP, etc),
            'has_master_suffix': True/False
        }
    """
    result = {
        'node': reference_node,
        'file_path': None,
        'file_name': None,
        'is_valid': True,
        'reason': '',
        'prefix': None,
        'has_master_suffix': False
    }
    
    # Obtener path del archivo
    file_path = get_reference_file_path(reference_node)
    
    if not file_path:
        result['is_valid'] = False
        result['reason'] = 'Could not get file path'
        return result
    
    result['file_path'] = file_path
    
    # Obtener nombre del archivo sin extension
    file_name = os.path.basename(file_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    
    result['file_name'] = file_name
    
    # Verificar prefijo CH_ o PRP_
    if file_name_no_ext.startswith('CH_'):
        result['prefix'] = 'CH'
    elif file_name_no_ext.startswith('PRP_'):
        result['prefix'] = 'PRP'
    else:
        # No tiene prefijo CH_ o PRP_, por lo tanto no aplica la validacion
        result['is_valid'] = True
        result['reason'] = 'Not a CH or PRP asset (validation skipped)'
        return result
    
    # Verificar sufijo _MASTER
    if '_MASTER' in file_name_no_ext:
        result['has_master_suffix'] = True
        result['is_valid'] = True
    else:
        result['has_master_suffix'] = False
        result['is_valid'] = False
        result['reason'] = 'Missing _MASTER suffix'
    
    return result


def construct_master_path(current_path):
    """
    Construye el path del archivo _MASTER basado en el path actual
    
    Logica:
    FROM: <workspace>/assets/CH/KASSY/03_rig/versions/CH_KASSY_03_rig_v007.ma
    TO:   <workspace>/assets/CH/KASSY/03_rig/CH_KASSY_03_rig_MASTER.ma
    
    Args:
        current_path: Path actual del archivo referenciado
        
    Returns:
        str: Path del archivo _MASTER, o None si no se puede construir
    """
    if not current_path:
        return None
    
    # Obtener nombre del archivo
    file_name = os.path.basename(current_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    file_ext = os.path.splitext(file_name)[1]
    
    # Verificar que tiene prefijo CH_ o PRP_
    if not (file_name_no_ext.startswith('CH_') or file_name_no_ext.startswith('PRP_')):
        return None
    
    # Construir nombre _MASTER
    # Remover _v### si existe
    master_name = re.sub(r'_v\d+$', '', file_name_no_ext)
    
    # Si no tiene _MASTER, agregarlo
    if not master_name.endswith('_MASTER'):
        master_name += '_MASTER'
    
    master_file = master_name + file_ext
    
    # Construir path
    # Si el path actual contiene /versions/, subir un nivel
    dir_path = os.path.dirname(current_path)
    
    if '/versions/' in current_path or '\\versions\\' in current_path:
        # Subir un nivel (parent de versions)
        master_dir = os.path.dirname(dir_path)
    else:
        # Si no esta en versions, usar el mismo directorio
        master_dir = dir_path
    
    master_path = os.path.join(master_dir, master_file)
    
    # Normalizar path
    master_path = master_path.replace('\\', '/')
    
    return master_path


def fix_reference_to_master(reference_node, current_path):
    """
    Reemplaza una referencia por su archivo _MASTER
    
    Args:
        reference_node: Nombre del reference node
        current_path: Path actual del archivo
        
    Returns:
        dict: {
            'success': True/False,
            'master_path': path del master,
            'error': mensaje de error si falla
        }
    """
    result = {
        'success': False,
        'master_path': None,
        'error': ''
    }
    
    # Construir path del master
    master_path = construct_master_path(current_path)
    
    if not master_path:
        result['error'] = 'Could not construct master path'
        return result
    
    result['master_path'] = master_path
    
    # Verificar que el archivo master existe
    if not os.path.exists(master_path):
        result['error'] = 'Master file does not exist: {}'.format(master_path)
        return result
    
    # Intentar reemplazar la referencia
    try:
        cmds.file(master_path, loadReference=reference_node)
        result['success'] = True
        print("  [FIXED] Reference updated to: {}".format(os.path.basename(master_path)))
        return result
    
    except Exception as e:
        result['error'] = 'Failed to load reference: {}'.format(str(e))
        return result


def auto_fix_invalid_references(invalid_refs):
    """
    Intenta arreglar automaticamente todas las referencias invalidas
    
    Args:
        invalid_refs: Lista de referencias invalidas (del check)
        
    Returns:
        dict: {
            'total': int,
            'fixed': list,
            'failed': list
        }
    """
    print("\n" + "=" * 60)
    print("AUTO-FIXING INVALID REFERENCES")
    print("=" * 60 + "\n")
    
    fixed = []
    failed = []
    
    for ref_data in invalid_refs:
        ref_node = ref_data['node']
        current_path = ref_data['file_path']
        file_name = ref_data['file_name']
        
        print("Fixing: {}".format(file_name))
        
        result = fix_reference_to_master(ref_node, current_path)
        
        if result['success']:
            fixed.append({
                'node': ref_node,
                'old_file': file_name,
                'new_file': os.path.basename(result['master_path']),
                'master_path': result['master_path']
            })
        else:
            failed.append({
                'node': ref_node,
                'file': file_name,
                'error': result['error'],
                'master_path': result.get('master_path')
            })
            print("  [FAILED] {}".format(result['error']))
    
    # Resumen
    print("\n" + "-" * 60)
    print("AUTO-FIX SUMMARY:")
    print("  Total: {}".format(len(invalid_refs)))
    print("  Fixed: {}".format(len(fixed)))
    print("  Failed: {}".format(len(failed)))
    print("-" * 60 + "\n")
    
    if fixed:
        print("FIXED REFERENCES:")
        for item in fixed:
            print("  {} -> {}".format(item['old_file'], item['new_file']))
        print("")
    
    if failed:
        print("FAILED TO FIX:")
        for item in failed:
            print("  {} - {}".format(item['file'], item['error']))
        print("")
    
    return {
        'total': len(invalid_refs),
        'fixed': fixed,
        'failed': failed
    }


def check_animation_scene():
    """
    FUNCION PRINCIPAL - Verifica todos los assets referenciados
    
    Busca assets con prefijo CH_ o PRP_ y valida que tengan sufijo _MASTER
    
    Returns:
        dict: {
            'total_references': int,
            'checked_references': int,
            'valid_references': int,
            'invalid_references': list,
            'skipped_references': list
        }
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - ANIMATION SCENE CHECKER")
    print("=" * 60)
    
    scene_name = get_scene_name()
    print("\nScene: {}".format(scene_name if scene_name else "UNSAVED"))
    
    # Obtener todas las referencias
    all_references = get_all_references()
    
    print("\nTotal references found: {}".format(len(all_references)))
    
    if not all_references:
        print("\n" + "=" * 60)
        print("NO REFERENCES FOUND IN SCENE")
        print("=" * 60 + "\n")
        
        cmds.confirmDialog(
            title='No References',
            message='No references found in the current scene.',
            button=['OK'],
            icon='information'
        )
        
        return {
            'total_references': 0,
            'checked_references': 0,
            'valid_references': 0,
            'invalid_references': [],
            'skipped_references': []
        }
    
    # Verificar cada referencia
    print("\nChecking references...\n")
    
    invalid_refs = []
    skipped_refs = []
    valid_count = 0
    checked_count = 0
    
    for ref in all_references:
        result = check_reference_is_master(ref)
        
        # Si no tiene prefijo CH_ o PRP_, skip
        if result['prefix'] is None:
            skipped_refs.append(result)
            print("  [SKIP] {} - {}".format(
                result['file_name'] if result['file_name'] else ref,
                result['reason']
            ))
            continue
        
        checked_count += 1
        
        if result['is_valid']:
            valid_count += 1
            print("  [OK] {} - Valid _MASTER file".format(result['file_name']))
        else:
            invalid_refs.append(result)
            print("  [ERROR] {} - {}".format(result['file_name'], result['reason']))
    
    # Resumen
    print("\n" + "-" * 60)
    print("SUMMARY:")
    print("  Total references: {}".format(len(all_references)))
    print("  Checked (CH/PRP): {}".format(checked_count))
    print("  Valid: {}".format(valid_count))
    print("  Invalid: {}".format(len(invalid_refs)))
    print("  Skipped (other): {}".format(len(skipped_refs)))
    print("-" * 60)
    
    # Si hay invalidos, mostrar detalles
    if invalid_refs:
        print("\nINVALID REFERENCES (need _MASTER suffix):")
        for ref in invalid_refs:
            print("  - {}".format(ref['file_name']))
            print("    Node: {}".format(ref['node']))
            print("    Path: {}".format(ref['file_path']))
            print("    Reason: {}".format(ref['reason']))
            print("")
        
        print("=" * 60)
        print("VALIDATION FAILED")
        print("Please replace these references with _MASTER files")
        print("=" * 60 + "\n")
        
        # Dialogo de error con opcion de Auto-Fix
        error_message = "Found {} invalid reference(s):\n\n".format(len(invalid_refs))
        
        for i, ref in enumerate(invalid_refs[:5]):  # Mostrar max 5
            error_message += "- {}\n".format(ref['file_name'])
        
        if len(invalid_refs) > 5:
            error_message += "\n... and {} more.\n".format(len(invalid_refs) - 5)
        
        error_message += "\nAll CH_ and PRP_ assets must have _MASTER suffix.\n\n"
        error_message += "Would you like to auto-fix these references?"
        
        response = cmds.confirmDialog(
            title='Validation Failed',
            message=error_message,
            button=['Auto-Fix', 'Cancel'],
            defaultButton='Auto-Fix',
            cancelButton='Cancel',
            icon='warning'
        )
        
        # Si el usuario eligio Auto-Fix
        if response == 'Auto-Fix':
            fix_result = auto_fix_invalid_references(invalid_refs)
            
            # Mostrar resultado del auto-fix
            if fix_result['fixed'] and not fix_result['failed']:
                # Todo se arreglo exitosamente
                success_msg = "All references fixed successfully!\n\n"
                success_msg += "Fixed {} reference(s):\n\n".format(len(fix_result['fixed']))
                
                for item in fix_result['fixed'][:5]:
                    success_msg += "- {}\n".format(item['new_file'])
                
                if len(fix_result['fixed']) > 5:
                    success_msg += "\n... and {} more.".format(len(fix_result['fixed']) - 5)
                
                cmds.confirmDialog(
                    title='Auto-Fix Complete',
                    message=success_msg,
                    button=['OK'],
                    icon='information'
                )
            
            elif fix_result['fixed'] and fix_result['failed']:
                # Algunos se arreglaron, otros no
                partial_msg = "Partial auto-fix completed:\n\n"
                partial_msg += "Fixed: {}\n".format(len(fix_result['fixed']))
                partial_msg += "Failed: {}\n\n".format(len(fix_result['failed']))
                partial_msg += "Failed references:\n\n"
                
                for item in fix_result['failed'][:3]:
                    partial_msg += "- {}\n  {}\n\n".format(item['file'], item['error'])
                
                partial_msg += "Check Script Editor for details."
                
                cmds.confirmDialog(
                    title='Auto-Fix Partial',
                    message=partial_msg,
                    button=['OK'],
                    icon='warning'
                )
            
            else:
                # Nada se pudo arreglar
                fail_msg = "Auto-fix failed for all references.\n\n"
                fail_msg += "Common issues:\n"
                fail_msg += "- Master files do not exist\n"
                fail_msg += "- Incorrect file paths\n\n"
                fail_msg += "Check Script Editor for details."
                
                cmds.confirmDialog(
                    title='Auto-Fix Failed',
                    message=fail_msg,
                    button=['OK'],
                    icon='critical'
                )
        
        return {
            'total_references': len(all_references),
            'checked_references': checked_count,
            'valid_references': valid_count,
            'invalid_references': invalid_refs,
            'skipped_references': skipped_refs
        }
    
    else:
        print("\n" + "=" * 60)
        print("VALIDATION PASSED")
        print("All CH/PRP references are _MASTER files")
        print("=" * 60 + "\n")
        
        # Dialogo de exito
        success_message = "Scene validation passed!\n\n"
        success_message += "Checked {} CH/PRP reference(s)\n".format(checked_count)
        success_message += "All references have _MASTER suffix.\n\n"
        
        if skipped_refs:
            success_message += "Skipped {} other reference(s) (not CH/PRP)".format(len(skipped_refs))
        
        cmds.confirmDialog(
            title='Validation Passed',
            message=success_message,
            button=['OK'],
            icon='information'
        )
        
        return {
            'total_references': len(all_references),
            'checked_references': checked_count,
            'valid_references': valid_count,
            'invalid_references': [],
            'skipped_references': skipped_refs
        }