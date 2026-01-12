import maya.cmds as cmds
import os
import json

def validate_pinkooland_project():

    
    project_path = cmds.workspace(q=True, rootDirectory=True)
    
    
    target_key = "NG9TD3"
    found_project = False

    
    if os.path.exists(project_path):
        files = [f for f in os.listdir(project_path) if f.endswith('.json')]
        
        for file_name in files:
            file_path = os.path.join(project_path, file_name)
            
            try:
                
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    
                    if data.get("project_key") == target_key:
                        found_project = True
                        break 
            except Exception:
                continue

    
    if found_project:
        print("Security Check: Project validation successful.")
        return True
    else:
        cmds.confirmDialog(
            title='Security validation failed', 
            message='You are not working in Pinkooland Project.\nPlease set your project correctly.', 
            button=['OK'], 
            defaultButton='OK',
            icon='critical'
        )
        return False