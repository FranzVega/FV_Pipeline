
"""
PKL Pipeline - Camera Exporter
Exporta camaras para Unreal Engine
"""
import maya.cmds as cmds
import maya.mel as mel
import os
import re


def find_unreal_camera():
    """
    Busca la camara con atributo UnrealCamera = True dentro del grupo CAMERA
    
    Returns:
        str: Nombre de la camara encontrada, o None si no existe
    """
    
    if not cmds.objExists('CAMERA'):
        cmds.warning("CAMERA group not found in scene")
        return None
    
    
    children = cmds.listRelatives('CAMERA', allDescendents=True, type='transform') or []
    
    
    for obj in children:
        
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if not shapes or cmds.objectType(shapes[0]) != 'camera':
            continue
        
        
        if cmds.attributeQuery('UnrealCamera', node=obj, exists=True):
            if cmds.getAttr(obj + '.UnrealCamera'):
                return obj
    
    return None


def get_camera_export_info():
    """
    Lee los atributos del grupo CAMERA para obtener info de exportacion
    
    Returns:
        dict: {'exported_name': str, 'path': str, 'exportable': bool}
        None si no existe el grupo o faltan atributos
    """
    if not cmds.objExists('CAMERA'):
        return None
    
    
    exported_name = None
    path = None
    exportable = True
    
    if cmds.attributeQuery('ExportedName', node='CAMERA', exists=True):
        exported_name = cmds.getAttr('CAMERA.ExportedName')
    
    if cmds.attributeQuery('Path', node='CAMERA', exists=True):
        path = cmds.getAttr('CAMERA.Path')
    
    if cmds.attributeQuery('Exportable', node='CAMERA', exists=True):
        exportable = cmds.getAttr('CAMERA.Exportable')
    
    
    if not exported_name or not path:
        return None
    
    return {
        'exported_name': exported_name,
        'path': path,
        'exportable': exportable
    }


def export_ue_camera():
    """
    FUNCION PRINCIPAL - Exporta camara a UE
    1. Busca camara con UnrealCamera=True en grupo CAMERA
    2. Lee atributos del grupo CAMERA
    3. Crea camara UE_ duplicada
    4. Bake animation
    5. Exporta FBX
    """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - CAMERA EXPORTER")
    print("=" * 60)
    
    
    
    
    
    print("\nSearching for Unreal Camera...")
    camera = find_unreal_camera()
    
    if not camera:
        cmds.warning("No camera found in CAMERA group")
        cmds.confirmDialog(
            title='No Camera Found',
            message='No Unreal Camera was found inside the CAMERA group.\n\nPlease use Camera Setter first.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    print("  Camera found: {}".format(camera))
    
    
    
    
    
    print("\nReading CAMERA group attributes...")
    export_info = get_camera_export_info()
    
    if not export_info:
        cmds.warning("CAMERA group missing")
        cmds.confirmDialog(
            title='Missing Group',
            message='CAMERA group is missing required attributes.\n\nPlease organize the animation scene first.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    if not export_info['exportable']:
        cmds.warning("CAMERA group has Exportable set to False")
        cmds.confirmDialog(
            title='Export Disabled',
            message='CAMERA group has Exportable attribute set to False.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    exported_name = export_info['exported_name']
    export_path = export_info['path']
    
    print("  Exported Name: {}".format(exported_name))
    print("  Export Path: {}".format(export_path))
    
    
    
    
    
    
    range_match = re.search(r'_FR_(\d+)_(\d+)', camera)
    
    if range_match:
        start_frame = int(range_match.group(1))
        end_frame = int(range_match.group(2))
        print("  Frame range from camera name: {} - {}".format(start_frame, end_frame))
    else:
        
        start_frame = int(cmds.playbackOptions(query=True, minTime=True))
        end_frame = int(cmds.playbackOptions(query=True, maxTime=True))
        print("  Frame range from timeline: {} - {}".format(start_frame, end_frame))
    
    
    cmds.playbackOptions(min=start_frame, max=end_frame)
    cmds.playbackOptions(animationStartTime=start_frame, animationEndTime=end_frame)
    
    
    
    
    
    print("\nCreating UE camera...")
    
    world_matrix = cmds.xform(camera, q=True, m=True, ws=True)
    
    new_cam = cmds.camera()
    new_cam_transform = new_cam[0]
    new_cam_shape = new_cam[1]
    
    
    new_cam_transform = cmds.rename(new_cam_transform, exported_name)
    new_cam_shape = cmds.listRelatives(new_cam_transform, shapes=True)[0]
    
    cmds.xform(new_cam_transform, m=world_matrix, ws=True)
    
    print("  UE camera created: {}".format(new_cam_transform))
    
    
    
    
    
    print("  Copying focal length...")
    
    src_attr = camera + ".focalLength"
    dst_attr = new_cam_shape + ".focalLength"
    
    if cmds.objExists(src_attr) and cmds.objExists(dst_attr):
        keys = cmds.keyframe(src_attr, q=True, timeChange=True)
        if keys:
            for t in keys:
                value = cmds.getAttr(src_attr, time=t)
                cmds.setKeyframe(dst_attr, time=t, value=value)
        else:
            value = cmds.getAttr(src_attr)
            cmds.setAttr(dst_attr, value)
    
    
    
    
    
    print("  Baking animation...")
    
    constraint = cmds.parentConstraint(camera, new_cam_transform, mo=True)[0]
    
    cmds.bakeResults(
        new_cam_transform,
        simulation=True,
        t=(start_frame, end_frame),
        at=["translate", "rotate"],
        preserveOutsideKeys=True
    )
    
    cmds.delete(constraint)
    
    
    
    
    
    print("\nResolving export path...")
    
    
    workspace_root = cmds.workspace(q=True, rootDirectory=True)
    
    
    full_export_path = export_path.replace('<workspace_root>', workspace_root)
    
    
    try:
        if not os.path.exists(full_export_path):
            os.makedirs(full_export_path)
            print("  Created directory: {}".format(full_export_path))
    except Exception as e:
        cmds.warning("Could not create export directory: {}".format(e))
    
    
    fbx_path = os.path.join(full_export_path, "{}.fbx".format(exported_name)).replace("\\", "/")
    
    print("  Export path: {}".format(fbx_path))
    
    
    
    
    
    print("\nConfiguring FBX export...")
    
    mel.eval("FBXResetExport;")
    mel.eval("FBXExportCameras -v true;")
    mel.eval("FBXExportLights -v false;")
    mel.eval("FBXExportSkins -v false;")
    mel.eval("FBXExportShapes -v true;")
    mel.eval("FBXExportBakeComplexAnimation -v true;")
    mel.eval("FBXExportBakeComplexStart -v {};".format(start_frame))
    mel.eval("FBXExportBakeComplexEnd -v {};".format(end_frame))
    mel.eval("FBXExportBakeComplexStep -v 1;")
    mel.eval("FBXExportBakeResampleAnimation -v true;")
    mel.eval('FBXExportQuaternion -v "resample";')
    
    
    
    
    
    print("  Exporting FBX...")
    
    cmds.select(new_cam_transform, r=True)
    mel.eval('FBXExport -f "{}" -s;'.format(fbx_path))
    
    
    
    
    
    if os.path.exists(fbx_path):
        cmds.delete(new_cam_transform)
        
        print("\n" + "=" * 60)
        print("CAMERA EXPORTED SUCCESSFULLY")
        print("  Name: {}".format(exported_name))
        print("  Path: {}".format(fbx_path))
        print("=" * 60 + "\n")
        
        cmds.confirmDialog(
            title='Export Complete',
            message="Camera exported successfully!\n\n{}".format(fbx_path),
            button=['OK'],
            icon='information'
        )
        
        return True
    else:
        cmds.warning("FBX not created, UE camera kept for review")
        cmds.confirmDialog(
            title='Export Failed',
            message='FBX file was not created.\nUE camera kept in scene for review.',
            button=['OK'],
            icon='warning'
        )

        return False
