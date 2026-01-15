
"""
PKL Pipeline UI
Drag & Drop installable version
"""
import maya.cmds as cmds
import sys
import os



def setup_paths():
    """Configura los paths necesarios"""
    
    
    
    ui_path = None
    for path in sys.path:
        
        normalized = path.replace('\\', '/').rstrip('/')
        if normalized.endswith('/ui') or normalized.endswith('ui'):
            
            test_file = os.path.join(path, 'pipeline_ui.py')
            if os.path.exists(test_file):
                ui_path = path
                break
    
    if ui_path:
        
        parent_dir = os.path.dirname(ui_path.rstrip('/\\'))
        
        
        core_dir = os.path.join(parent_dir, 'core')
        config_dir = os.path.join(parent_dir, 'config')
        
        print("PKL Pipeline - Setup paths:")
        print("  UI dir:     {}".format(ui_path))
        print("  Parent dir: {}".format(parent_dir))
        print("  Core dir:   {}".format(core_dir))
        print("  Config dir: {}".format(config_dir))
        
        
        if os.path.exists(core_dir):
            print("  [OK] Core directory found")
        else:
            print("  [ERROR] Core directory NOT found!")
            
        if os.path.exists(config_dir):
            print("  [OK] Config directory found")
        else:
            print("  [ERROR] Config directory NOT found!")
        
        
        for p in [parent_dir, core_dir, config_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)
                print("  Added to sys.path: {}".format(p))
        
        return True
    else:
        print("PKL Pipeline ERROR: Could not find UI directory")
        return False


setup_paths()


try:
    import security
    import scene_checker
    import animation_organizer
    import group_creator
    import settings
    import camera_exporter
    import camera_setter
    import model_checker
    import skeleton_marker
    import scene_exporter
    import export_selected_grp
    import check_anm_scn

    
    import sys
    import os
    ui_path_for_helpers = None
    for path in sys.path:
        normalized = path.replace('\\', '/').rstrip('/')
        if normalized.endswith('/ui') or normalized.endswith('ui'):
            test_file = os.path.join(path, 'pipeline_ui.py')
            if os.path.exists(test_file):
                ui_path_for_helpers = path
                break
    
    if ui_path_for_helpers:
        parent_dir_helpers = os.path.dirname(ui_path_for_helpers.rstrip('/\\'))
        utils_dir_helpers = os.path.join(parent_dir_helpers, 'utils')
        if utils_dir_helpers not in sys.path:
            sys.path.insert(0, utils_dir_helpers)
    
    import helpers
    get_scene_type = helpers.get_scene_type
    
    
    check_scene = getattr(scene_checker, 'check_scene', None)
    organize_animation = getattr(animation_organizer, 'organize_animation', None)
    create_main_group_func = getattr(group_creator, 'create_main_group', None)
    ue_cam_exporter = getattr(camera_exporter, "export_ue_camera", None)
    set_camera_func = getattr(camera_setter, 'set_camera_attributes', None)
    check_model_func = getattr(model_checker, 'model_check_cleanup', None)
    set_joint_func = getattr(skeleton_marker, 'mark_skeleton_exportable', None)
    export_all_func = getattr(scene_exporter, 'export_scene', None)
    export_selected_func = getattr(export_selected_grp, 'export_selected', None)
    check_animation_scene = check_anm_scn.check_animation_scene

    
    if check_scene is None:
        print("  Warning: check_scene function not found in scene_checker module")
        def check_scene(): print("Scene Checked (No function found)")
    
    if organize_animation is None:
        print("  Warning: organize_animation function not found in animation_organizer module")
        def organize_animation(): print("Animation Organized (No function found)")
    
    if create_main_group_func is None:
        print("  Warning: create_main_group function not found in group_creator module")
        def create_main_group_func(): print("Create Main Group (No function found)")

    if set_camera_func is None:
        print("  Warning: set_camera_attributes function not found in camera_setter module")
        def set_camera_func(): print("Set Camera (No function found)")
    
    if check_model_func is None:
        print("  Warning: function not found in camera_setter module")
        def check_model_func(): print("(No function found)")
   
    if set_joint_func is None:
        print("  Warning: function not found in module")
        def set_joint_func(): print("(No function found)")
    
    if export_all_func is None:
        print("  Warning: function not found in module")
        def export_all_func(): print("(No function found)")
   
    if export_selected_func is None:
        print("  Warning: export_selected function not found in export_selected module")
        def export_selected_func(): print("Export Selected (No function found)")
   
    VERSION = settings.VERSION
    
    print("PKL Pipeline: Core modules loaded successfully! v{}".format(VERSION))
    
except ImportError as e:
    print("PKL Pipeline Warning: Could not import core modules")
    print("Error: {}".format(e))
    import traceback
    traceback.print_exc()
    
    def check_scene(): print("Scene Checked (Fallback)")
    def organize_animation(): print("Animation Organized (Fallback)")
    def create_main_group_func(): print("Create Main Group (Fallback)")
    def get_scene_type(): return ("UNIDENTIFIED", [1.0, 0.4, 0.4])
    VERSION = "PRUEBA"



def CheckScene(*args): 
    
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    
    check_model_func()

def SetJoints(*args):
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return 
    set_joint_func()
    
def create_main_group(*args): 
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    create_main_group_func()
    
def check_anim_scene(*args):
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    print("Scene ready")
    check_animation_scene()
    
def set_camera(*args): 
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    set_camera_func()
    
def orgAnim(*args): 
    """Llama al script 2 del core"""
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    organize_animation()
    
def Check_errors(*args): 
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    print("Errores")
    check_animation_scene()
    
def export_all(*args): 
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    export_all_func()
    ue_cam_exporter()
    
def export_selected(*args):
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    export_selected_func()
    
    
def export_camera(*args):
    if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return
    ue_cam_exporter()




def silent_check_update_on_startup():
    """
    Ejecuta check_update.bat en background al abrir la UI
    El bat verifica versiones y crea .update_available si hay update
    """
    import subprocess
    
    try:
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        utils_dir = os.path.join(parent_dir, 'utils')
        check_bat = os.path.join(utils_dir, 'check_update.bat')
        
        if not os.path.exists(check_bat):
            print("Warning: check_update.bat not found at {}".format(check_bat))
            return False
        
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  
        
        subprocess.Popen(
            [check_bat],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print("PKL Pipeline: Checking for updates in background...")
        return True
        
    except Exception as e:
        print("Update check error: {}".format(e))
        return False


def check_for_update_signal():
    """
    Lee el archivo señal .update_available
    Returns: (has_update, remote_version)
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        signal_file = os.path.join(parent_dir, '.update_available')
        
        if os.path.exists(signal_file):
            
            with open(signal_file, 'r') as f:
                remote_version = f.read().strip()
            
            print("PKL Pipeline: Update available - Remote version: {}".format(remote_version))
            return (True, remote_version)
        else:
            return (False, None)
            
    except Exception as e:
        print("Signal check error: {}".format(e))
        return (False, None)



class PKLPipelineUI(object):
    def __init__(self):
        self.window_id = "pkl_pipeline_ui_window"
        self.window_title = "PKL Pipeline v{}".format(VERSION)
        self.create_ui()
        self.update_scene_info()

    def update_scene_info(self, *args):
        """
        Consulta los datos de la escena y actualiza las etiquetas de la UI.
        Ahora usa el helper get_scene_type() para deteccion inteligente
        """
        
        scene_type, type_color = get_scene_type()

        
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        frame_range = "{0} - {1}".format(int(start), int(end))

        
        cmds.text(self.type_label, edit=True, label=scene_type, backgroundColor=type_color)
        cmds.text(self.range_label, edit=True, label=frame_range)
        
        print("UI Updated: {0} | Range: {1}".format(scene_type, frame_range))
    
    def launch_external_updater(self, *args):
        """
        Lanza el updater completo (update.bat)
        Este SI descarga y actualiza archivos
        """
        import subprocess

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        updater_bat = os.path.join(parent_dir, "update.bat")
        updater_bat = os.path.abspath(updater_bat)

        if not os.path.exists(updater_bat):
            cmds.confirmDialog(
                title="Updater Error",
                message="Updater not found.\n\n{}".format(updater_bat),
                button=["OK"],
                icon="critical"
            )
            return

        if cmds.confirmDialog(
            title="Update Pipeline",
            message="This will check and update PKL Tool.\n\nMaya must be restarted after update.",
            button=["Update", "Cancel"],
            defaultButton="Update",
            cancelButton="Cancel",
            dismissString="Cancel"
        ) != "Update":
            return

        
        subprocess.Popen(
            ['cmd.exe', '/c', updater_bat],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        
        if cmds.window(self.window_id, exists=True):
            cmds.deleteUI(self.window_id)

    def create_ui(self):
        if cmds.window(self.window_id, exists=True):
            cmds.deleteUI(self.window_id)

        self.window = cmds.window(
            self.window_id,
            title=self.window_title,
            widthHeight=(300, 500),
            sizeable=True
        )

        main_scroll = cmds.scrollLayout(childResizable=True)
        main_col = cmds.columnLayout(adjustableColumn=True, parent=main_scroll)

        
        cmds.separator(height=20, style="out")
        
        
        
        
        has_update, remote_version = check_for_update_signal()
        
        if has_update:
            cmds.frameLayout(
                label="",
                borderStyle="etchedIn",
                backgroundColor=[0.3, 0.5, 0.2],
                marginWidth=5,
                marginHeight=3,
                parent=main_col
            )
            cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
            
            cmds.text(
                label="NEW UPDATE AVAILABLE!",
                font="boldLabelFont",
                backgroundColor=[0.4, 0.6, 0.3],
                height=20
            )
            
            if remote_version:
                cmds.text(
                    label="Version {} is ready to install".format(remote_version),
                    font="smallPlainLabelFont",
                    align="center"
                )
            
            cmds.button(
                label="UPDATE NOW",
                height=25,
                backgroundColor=[0.2, 0.4, 0.2],
                command=self.launch_external_updater
            )
            
            cmds.setParent("..")
            cmds.setParent("..")
        
        cmds.separator(height=20, style="in")

        
        cmds.frameLayout(
            label="Character and Prop Organizer", 
            collapsable=True,
            collapse=True,  
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label="Check Scene", command=CheckScene, 
                   annotation="Look for possible errors")
        cmds.button(label="Create main group", command=create_main_group)
        cmds.button(label="Set Joints", command=SetJoints, annotation="Set the Skeleton to be exported")
        cmds.setParent("..")
        cmds.setParent("..")

        
        cmds.frameLayout(
            label="Animation Scene Organizer", 
            collapsable=True,
            collapse=True, 
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label="Check Animation Scene", command=check_anim_scene)
        cmds.button(label="Set Selected Camera", command=set_camera)
        cmds.button(label="Organize Scene", command=orgAnim)
        cmds.setParent("..")
        cmds.setParent("..")

        
        cmds.frameLayout(
            label="Export to Unreal", 
            collapsable=True, 
            collapse=True, 
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label="Check for Errors", command=Check_errors)
        cmds.button(label="Export all", command=export_all)
        cmds.button(label="Export Selected Groups", command=export_selected)
        cmds.button(label="Export Camera", command=export_camera)
        cmds.setParent("..")
        cmds.setParent("..")

        
        cmds.frameLayout(
            label="Scene Info", 
            collapsable=True, 
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5) 
        
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[85, 100])
        cmds.text(label="Scene Type:", align="left", font="boldLabelFont")
        self.type_label = cmds.text(label="Detecting...", align="center")
        cmds.setParent("..")
        
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[85, 100])
        cmds.text(label="Frame Range:", align="left", font="boldLabelFont")
        self.range_label = cmds.text(label="0 - 0", align="center")
        cmds.setParent("..")
        
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[85, 100])
        cmds.text(label="Version:", align="left", font="boldLabelFont")
        cmds.text(label=VERSION, align="center", backgroundColor=[0.2, 0.2, 0.3])
        cmds.setParent("..")
       
        cmds.separator(height=10, style="in")
        
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=[150, 150], columnAttach=[(1,'both',2), (2,'both',2)])
        cmds.button(
            label="UPDATE SCENE INFO", 
            command=self.update_scene_info, 
            backgroundColor=[0.2, 0.2, 0.2]
        )
        cmds.button(
            label="UPDATE PKL TOOL", 
            command=self.launch_external_updater,
            backgroundColor=[0.2, 0.3, 0.2]
        )
        cmds.setParent("..")
              
        cmds.setParent("..") 
        cmds.setParent("..") 

        cmds.text(label='Created by Franz Vega', 
            font="smallObliqueLabelFont",
            align="right",
        )

        cmds.showWindow(self.window)



def main():
    """Main function with security check and UI launch"""
    global pkl_ui
    
    
    
    try:
        import security
        if not security.validate_pinkooland_project():
            print("Access Denied: Incorrect Project.")
            return 
    except ImportError:
        print("Security Error: Could not find security module. Access denied.")
        return

    
    silent_check_update_on_startup()
    
    
    modules_to_reload = [
        'security',
        'pipeline_ui',
        'scene_checker', 
        'animation_organizer',
        'group_creator',
        'camera_exporter',
        'camera_setter',
        'settings',
        'helpers'
    ]
    
    for mod_name in modules_to_reload:
        if mod_name in sys.modules:
            try:
                import importlib
                importlib.reload(sys.modules[mod_name])
            except:
                pass
    
    
    if cmds.window("pkl_pipeline_ui_window", exists=True):
        cmds.deleteUI("pkl_pipeline_ui_window")
    
    
    pkl_ui = PKLPipelineUI()
    print("=" * 60)
    print("PKL Pipeline v{} LOADED SUCCESSFULLY".format(VERSION))
    print("=" * 60)
    return pkl_ui

if __name__ == "__main__":
    main()