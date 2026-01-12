# -*- coding: utf-8 -*-
"""
PKL Pipeline - Export Selected Groups
Only exports groups selected by the user (or their children if a parent container is selected).
"""
import maya.cmds as cmds
import maya.mel as mel
import os
import sys

# --- ATTRIBUTE HELPERS ---

def has_attribute(obj, attr_name):
    """ Checks if an attribute exists on the object """
    return cmds.objExists(obj) and cmds.attributeQuery(attr_name, node=obj, exists=True)

def get_attribute_value(obj, attr_name, default=None):
    """ Gets the value of a specific attribute safely """
    if has_attribute(obj, attr_name):
        return cmds.getAttr(obj + '.' + attr_name)
    return default


def find_exportable_joint(group):
    """
    Searches for a joint with FBX_exportable=True inside a group
    """
    if not cmds.objExists(group):
        return None
    
    # List all descendants of type joint
    descendants = cmds.listRelatives(group, allDescendents=True, type='joint', fullPath=True) or []
    
    for joint in descendants:
        if has_attribute(joint, 'FBX_exportable'):
            is_exportable = get_attribute_value(joint, 'FBX_exportable', False)
            if is_exportable:
                return joint
    
    return None


def is_exportable_group(obj):
    """
    Checks if an object is an exportable group (has name, path, and Exportable=True)
    """
    if not cmds.objExists(obj):
        return False
    
    # Check for required attributes
    if not (has_attribute(obj, 'ExportedName') and 
            has_attribute(obj, 'Path') and 
            has_attribute(obj, 'Exportable')):
        return False
    
    # Check if Exportable is set to True
    is_exportable = get_attribute_value(obj, 'Exportable', False)
    if not is_exportable:
        return False
    
    # Check if it has valid string values
    exported_name = get_attribute_value(obj, 'ExportedName', '')
    path = get_attribute_value(obj, 'Path', '')
    
    return bool(exported_name and path)


def get_exportable_children(parent):
    """
    Gets all direct exportable children of a parent group (e.g., 'CH', 'PR')
    """
    if not cmds.objExists(parent):
        return []
    
    # Get direct children transforms
    children = cmds.listRelatives(parent, children=True, type='transform', fullPath=True) or []
    
    exportable_children = []
    for child in children:
        if is_exportable_group(child):
            exportable_children.append(child)
    
    return exportable_children


def get_groups_to_export_from_selection():
    """
    Logic:
    1. If selection is a parent (CH/PR/CAMERA) and NOT exportable itself -> export its children.
    2. If selection is an individual exportable group -> export only that group.
    """
    selection = cmds.ls(selection=True, type='transform', long=True)
    
    if not selection:
        return []
    
    groups_to_export = []
    processed = set()
    
    for obj in selection:
        is_exportable = is_exportable_group(obj)
        hierarchy = get_attribute_value(obj, 'Hierarchy', '')

        # CASE 1: Selecting a parent container (not exportable itself)
        if hierarchy in ['CH', 'PR', 'CAMERA'] and not is_exportable:
            print("  Detected parent container: {} - Searching children...".format(obj))
            children = get_exportable_children(obj)
            
            for child in children:
                if child not in processed:
                    groups_to_export.append(child)
                    processed.add(child)
        
        # CASE 2: Selecting an individual exportable sub-group
        elif is_exportable:
            if obj not in processed:
                groups_to_export.append(obj)
                processed.add(obj)
                print("  Detected exportable sub-group: {}".format(obj))
        
        else:
            print("  [SKIP] Object is not an exportable group or container: {}".format(obj))
    
    return groups_to_export


def resolve_export_path(path_template):
    """ Resolves absolute path replacing <workspace_root> """
    workspace_root = cmds.workspace(q=True, rootDirectory=True)
    resolved_path = path_template.replace('<workspace_root>', workspace_root)
    resolved_path = resolved_path.replace('\\', '/')
    return resolved_path


def configure_fbx_export(start_frame, end_frame):
    """ Sets FBX Export options """
    print("  Configuring FBX export settings...")
    mel.eval('FBXResetExport;')
    mel.eval('FBXExportSmoothingGroups -v true;')
    mel.eval('FBXExportSmoothMesh -v true;')
    mel.eval('FBXExportTangents -v true;')
    mel.eval('FBXExportAnimationOnly -v false;')
    mel.eval('FBXExportBakeComplexAnimation -v true;')
    mel.eval('FBXExportBakeComplexStart -v {};'.format(start_frame))
    mel.eval('FBXExportBakeComplexEnd -v {};'.format(end_frame))
    mel.eval('FBXExportSkins -v true;')
    mel.eval('FBXExportShapes -v true;')
    mel.eval('FBXExportInputConnections -v true;')


def export_group_to_fbx(node, start_frame, end_frame):
    """
    Exports a single node to FBX
    """
    exported_name = get_attribute_value(node, 'ExportedName')
    path_template = get_attribute_value(node, 'Path')
    
    # 1. Resolve path and create directory
    export_dir = resolve_export_path(path_template)
    if not os.path.exists(export_dir):
        try:
            os.makedirs(export_dir)
        except Exception as e:
            return {'success': False, 'message': 'Could not create directory: {}'.format(e)}

    # 2. Find skeleton
    skeleton = find_exportable_joint(node)
    if not skeleton:
        return {'success': False, 'message': 'No exportable skeleton found'}
    
    fbx_path = os.path.join(export_dir, "{}.fbx".format(exported_name)).replace('\\', '/')
    
    # 3. Export
    try:
        configure_fbx_export(start_frame, end_frame)
        cmds.select(skeleton, replace=True)
        mel.eval('FBXExport -f "{}" -s;'.format(fbx_path))
        
        if os.path.exists(fbx_path):
            return {'success': True, 'path': fbx_path}
        return {'success': False, 'message': 'File was not created'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def export_selected_func():
    """ Main logic for the export process """
    print("\n" + "=" * 60)
    print("PKL PIPELINE - EXPORT SELECTED")
    print("=" * 60)
    
    # 1. Check selection
    nodes_to_export = get_groups_to_export_from_selection()
    
    if not nodes_to_export:
        cmds.warning("Nothing valid selected for export")
        cmds.confirmDialog(
            title='Selection Error',
            message='Please select a parent container (CH/PR) or specific exportable sub-groups.',
            button=['OK'],
            icon='warning'
        )
        return False
    
    # 2. Get frame range
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))
    
    # 3. Process export
    success_list = []
    fail_list = []

    for node in nodes_to_export:
        result = export_group_to_fbx(node, start, end)
        if result['success']:
            success_list.append(node)
        else:
            fail_list.append((node, result['message']))
            
    # 4. Summary Dialog
    msg = "Export Process Finished\n\nSuccessful: {}\nFailed: {}".format(len(success_list), len(fail_list))
    if fail_list:
        msg += "\n\nCheck Script Editor for error details."
    
    cmds.confirmDialog(title='Export Results', message=msg, button=['OK'])
    return True


def export_selected(*args): 
    """ Wrapper for UI calls """
    export_selected_func()