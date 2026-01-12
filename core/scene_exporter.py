# -*- coding: utf-8 -*-
"""
PKL Pipeline - Scene Exporter
Exporta grupos a FBX basado en atributos y skeletons marcados
"""
import maya.cmds as cmds
import maya.mel as mel
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
    has_attribute = helpers.has_attribute
    get_attribute_value = helpers.get_attribute_value
    
except ImportError as e:
    print("Warning: Could not import helpers - {}".format(e))
    
    # Fallback
    def has_attribute(obj, attr_name):
        return cmds.objExists(obj) and cmds.attributeQuery(attr_name, node=obj, exists=True)
    
    def get_attribute_value(obj, attr_name, default=None):
        if has_attribute(obj, attr_name):
            return cmds.getAttr(obj + '.' + attr_name)
        return default


def find_exportable_joint(group):
    """
    Busca un joint con FBX_exportable=True dentro de un grupo
    
    Args:
        group: Nombre del grupo a buscar
        
    Returns:
        str: Nombre del joint encontrado, o None si no existe
    """
    if not cmds.objExists(group):
        return None
    
    # Listar todos los descendientes del tipo joint
    descendants = cmds.listRelatives(group, allDescendents=True, type='joint', fullPath=True) or []
    
    for joint in descendants:
        if has_attribute(joint, 'FBX_exportable'):
            is_exportable = get_attribute_value(joint, 'FBX_exportable', False)
            if is_exportable:
                return joint
    
    return None


def find_exportable_groups():
    """
    Encuentra todos los grupos con atributos de exportacion
    
    Returns:
        list: Lista de dicts con info de cada grupo exportable
              [{group, exported_name, path, exportable}, ...]
    """
    exportable_groups = []
    all_transforms = cmds.ls(type='transform')
    
    for obj in all_transforms:
        # Verificar atributos necesarios
        if (has_attribute(obj, 'ExportedName') and 
            has_attribute(obj, 'Path') and 
            has_attribute(obj, 'Exportable')):
            
            # Verificar que Exportable=True
            is_exportable = get_attribute_value(obj, 'Exportable', False)
            
            if is_exportable:
                exported_name = get_attribute_value(obj, 'ExportedName', '')
                path = get_attribute_value(obj, 'Path', '')
                
                # Validar que tiene valores validos
                if exported_name and path:
                    exportable_groups.append({
                        'group': obj,
                        'exported_name': exported_name,
                        'path': path,
                        'exportable': is_exportable
                    })
    
    return exportable_groups


def resolve_export_path(path_template):
    """
    Resuelve el path de exportacion reemplazando <workspace_root>
    
    Args:
        path_template: String con el path (puede contener <workspace_root>)
        
    Returns:
        str: Path absoluto resuelto
    """
    workspace_root = cmds.workspace(q=True, rootDirectory=True)
    resolved_path = path_template.replace('<workspace_root>', workspace_root)
    resolved_path = resolved_path.replace('\\', '/')
    
    return resolved_path


def configure_fbx_export(start_frame, end_frame):
    """
    Configura opciones de exportacion FBX
    
    Args:
        start_frame: Frame inicial
        end_frame: Frame final
    """
    print("  Configuring FBX export settings...")
    
    mel.eval('FBXResetExport;')
    mel.eval('FBXExportSmoothingGroups -v true;')
    mel.eval('FBXExportSmoothMesh -v true;')
    mel.eval('FBXExportTangents -v true;')
    mel.eval('FBXExportReferencedAssetsContent -v true;')
    mel.eval('FBXExportTriangulate -v false;')
    mel.eval('FBXExportAnimationOnly -v false;')
    mel.eval('FBXExportBakeComplexAnimation -v true;')
    mel.eval('FBXExportBakeComplexStart -v {};'.format(start_frame))
    mel.eval('FBXExportBakeComplexEnd -v {};'.format(end_frame))
    mel.eval('FBXExportBakeComplexStep -v 1;')
    mel.eval('FBXExportQuaternion -v "resample";')
    mel.eval('FBXExportUseSceneName -v false;')
    mel.eval('FBXExportConstraints -v true;')
    mel.eval('FBXExportCameras -v true;')
    mel.eval('FBXExportLights -v true;')
    mel.eval('FBXExportSkins -v true;')
    mel.eval('FBXExportShapes -v true;')
    mel.eval('FBXExportInputConnections -v true;')


def export_group_to_fbx(group_data, start_frame, end_frame):
    """
    Exporta un grupo individual a FBX
    
    Args:
        group_data: Dict con info del grupo {group, exported_name, path, exportable}
        start_frame: Frame inicial
        end_frame: Frame final
        
    Returns:
        dict: Resultado de la exportacion {success, message, fbx_path}
    """
    group = group_data['group']
    exported_name = group_data['exported_name']
    path_template = group_data['path']
    
    print("\n" + "-" * 50)
    print("Processing group: {}".format(group))
    print("  Exported Name: {}".format(exported_name))
    print("  Path Template: {}".format(path_template))
    
    # 1. Buscar skeleton
    skeleton = find_exportable_joint(group)
    
    if not skeleton:
        print("  [SKIP] No exportable skeleton found in group")
        return {
            'success': False,
            'message': 'No exportable skeleton found',
            'fbx_path': None
        }
    
    print("  [OK] Skeleton found: {}".format(skeleton))
    
    # 2. Resolver path
    export_dir = resolve_export_path(path_template)
    
    # Crear directorio si no existe
    try:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            print("  [OK] Directory created: {}".format(export_dir))
    except Exception as e:
        print("  [ERROR] Could not create directory: {}".format(e))
        return {
            'success': False,
            'message': 'Could not create directory: {}'.format(e),
            'fbx_path': None
        }
    
    # 3. Construir path completo del FBX
    fbx_filename = "{}.fbx".format(exported_name)
    fbx_path = os.path.join(export_dir, fbx_filename).replace('\\', '/')
    
    print("  Export Path: {}".format(fbx_path))
    
    # 4. Configurar FBX
    configure_fbx_export(start_frame, end_frame)
    
    # 5. Seleccionar skeleton (root joint)
    try:
        cmds.select(skeleton, replace=True)
        print("  [OK] Skeleton selected for export")
    except Exception as e:
        print("  [ERROR] Could not select skeleton: {}".format(e))
        return {
            'success': False,
            'message': 'Could not select skeleton: {}'.format(e),
            'fbx_path': None
        }
    
    # 6. Exportar FBX
    try:
        mel.eval('FBXExport -f "{}" -s;'.format(fbx_path))
        
        # Verificar que se creo el archivo
        if os.path.exists(fbx_path):
            print("  [SUCCESS] FBX exported successfully")
            return {
                'success': True,
                'message': 'Exported successfully',
                'fbx_path': fbx_path
            }
        else:
            print("  [ERROR] FBX file not created")
            return {
                'success': False,
                'message': 'FBX file not created',
                'fbx_path': None
            }
    
    except Exception as e:
        print("  [ERROR] FBX export failed: {}".format(e))
        return {
            'success': False,
            'message': 'Export failed: {}'.format(e),
            'fbx_path': None
        }


def export_scene():
    """
    FUNCION PRINCIPAL - Exporta toda la escena
    
    Busca todos los grupos exportables, valida skeletons y exporta FBX
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - SCENE EXPORTER")
    print("=" * 60)
    
    # 1. Obtener frame range
    start_frame = int(cmds.playbackOptions(query=True, minTime=True))
    end_frame = int(cmds.playbackOptions(query=True, maxTime=True))
    
    print("\nFrame Range: {} - {}".format(start_frame, end_frame))
    
    # 2. Buscar grupos exportables
    print("\nSearching for exportable groups...")
    exportable_groups = find_exportable_groups()
    
    if not exportable_groups:
        cmds.warning("No exportable groups found in scene")
        cmds.confirmDialog(
            title='No Groups Found',
            message='No exportable groups found.\n\nMake sure groups have:\n- ExportedName attribute\n- Path attribute\n- Exportable = True',
            button=['OK'],
            icon='warning'
        )
        return False
    
    print("  Found {} exportable groups".format(len(exportable_groups)))
    
    # 3. Exportar cada grupo
    print("\n" + "=" * 60)
    print("STARTING EXPORT PROCESS")
    print("=" * 60)
    
    results = {
        'success': [],
        'skipped': [],
        'failed': []
    }
    
    for group_data in exportable_groups:
        result = export_group_to_fbx(group_data, start_frame, end_frame)
        
        if result['success']:
            results['success'].append({
                'group': group_data['group'],
                'path': result['fbx_path']
            })
        elif result['message'] == 'No exportable skeleton found':
            results['skipped'].append({
                'group': group_data['group'],
                'reason': result['message']
            })
        else:
            results['failed'].append({
                'group': group_data['group'],
                'reason': result['message']
            })
    
    # 4. Mostrar resumen
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE - SUMMARY")
    print("=" * 60)
    print("\nSuccessful Exports: {}".format(len(results['success'])))
    for item in results['success']:
        print("  [OK] {}".format(item['group']))
        print("       {}".format(item['path']))
    
    print("\nSkipped (No Skeleton): {}".format(len(results['skipped'])))
    for item in results['skipped']:
        print("  [SKIP] {}".format(item['group']))
    
    print("\nFailed: {}".format(len(results['failed'])))
    for item in results['failed']:
        print("  [FAIL] {}".format(item['group']))
        print("         {}".format(item['reason']))
    
    print("\n" + "=" * 60 + "\n")
    
    # 5. Dialogo de resultado
    if results['success']:
        message = "Export completed!\n\n"
        message += "Successful: {}\n".format(len(results['success']))
        message += "Skipped: {}\n".format(len(results['skipped']))
        message += "Failed: {}\n\n".format(len(results['failed']))
        message += "Check Script Editor for details."
        
        cmds.confirmDialog(
            title='Export Complete',
            message=message,
            button=['OK'],
            icon='information'
        )
    else:
        message = "No groups were exported.\n\n"
        message += "Skipped: {}\n".format(len(results['skipped']))
        message += "Failed: {}\n\n".format(len(results['failed']))
        message += "Check Script Editor for details."
        
        cmds.confirmDialog(
            title='Export Failed',
            message=message,
            button=['OK'],
            icon='warning'
        )
    
    return len(results['success']) > 0