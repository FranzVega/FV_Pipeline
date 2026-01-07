
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
    import scene_checker
    import animation_organizer
    import group_creator
    import settings
    import camera_exporter
    import camera_setter
    import model_checker
    
    
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
    VERSION = "1.0.0"



def CheckScene(*args): 
    """Llama al script 1 del core"""
    check_model_func()
    
def create_main_group(*args): 
    create_main_group_func()
    
def check_anim_scene(*args): 
    print("Scene ready")
    
def set_camera(*args): 
    
    
    set_camera_func()

    
def orgAnim(*args): 
    """Llama al script 2 del core"""
    organize_animation()
    
    
def Check_errors(*args): 
    print("Errores")
    
def export_all(*args): 
    print("Export all")
    
def export_selected(*args): 
    print("Selected groups exported")
    
def export_camera(*args):
    ue_cam_exporter()
    



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
    
    def check_for_updates(self, *args):
        """
        Verifica si hay actualizaciones disponibles en GitHub
        Si hay update, ofrece instalarlo directamente
        """
        try:
            
            import sys
            import os
            
            
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
                utils_dir = os.path.join(parent_dir, 'utils')
                
                if utils_dir not in sys.path:
                    sys.path.insert(0, utils_dir)
                
                
                import update_checker
                
                result = update_checker.check_updates()
                
                
                if result.get('available'):
                    message = "Update Available!\n\n"
                    message += "Current Version: {}\n".format(result.get('current_version'))
                    message += "Latest Version:  {}\n\n".format(result.get('latest_version'))
                    message += "Would you like to update now?\n\n"
                    message += "(This will download and replace all files)"
                    
                    response = cmds.confirmDialog(
                        title='Update Available',
                        message=message,
                        button=['Update Now', 'Cancel'],
                        defaultButton='Update Now',
                        cancelButton='Cancel',
                        icon='information'
                    )
                    
                    
                    if response == 'Update Now':
                        self.auto_update_pipeline()
                    
                else:
                    
                    message = result.get('message', 'You are up to date!')
                    if 'error' in result:
                        message += "\n\nNote: {}".format(result['error'])
                    
                    cmds.confirmDialog(
                        title='No Updates Available',
                        message=message,
                        button=['OK'],
                        defaultButton='OK'
                    )
            else:
                raise Exception("Could not find pkl_pipeline directory")
        
        except Exception as e:
            error_msg = str(e)
            cmds.confirmDialog(
                title='Error',
                message="Could not check for updates.\n\nError: {}".format(error_msg),
                button=['OK'],
                icon='warning'
            )
            print("Update check error: {}".format(error_msg))
            import traceback
            traceback.print_exc()
    
    def auto_update_pipeline(self, *args):
        """
        Ejecuta auto-update desde GitHub (reemplaza archivos SIN backup)
        Puede ser llamado directamente o desde check_for_updates
        """
        try:
            
            import sys
            import os
            
            
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
                utils_dir = os.path.join(parent_dir, 'utils')
                
                if utils_dir not in sys.path:
                    sys.path.insert(0, utils_dir)
                
                
                if 'auto_updater' in sys.modules:
                    del sys.modules['auto_updater']
                
                import auto_updater
                
                print("\n" + "=" * 60)
                print("STARTING AUTO UPDATE...")
                print("=" * 60 + "\n")
                
                result = auto_updater.auto_update()
                
                if result['success']:
                    message = "Update completed successfully!\n\n"
                    message += "Updated {} files.\n\n".format(len(result['updated']))
                    message += "The tool will now close.\n"
                    message += "Please REOPEN it from the shelf to use the new version."
                    
                    cmds.confirmDialog(
                        title='Update Complete',
                        message=message,
                        button=['OK'],
                        icon='information'
                    )
                    
                    
                    if cmds.window(self.window_id, exists=True):
                        cmds.deleteUI(self.window_id)
                    
                else:
                    message = "Update completed with errors.\n\n"
                    message += "Updated: {}\n".format(len(result.get('updated', [])))
                    message += "Failed: {}\n\n".format(len(result.get('failed', [])))
                    message += "Check Script Editor for details."
                    
                    cmds.confirmDialog(
                        title='Update Incomplete',
                        message=message,
                        button=['OK'],
                        icon='warning'
                    )
            
            else:
                raise Exception("Could not find utils directory")
        
        except Exception as e:
            cmds.confirmDialog(
                title='Update Error',
                message="Could not complete update.\n\nError: {}".format(str(e)),
                button=['OK'],
                icon='critical'
            )
            print("Auto-update error: {}".format(e))
            import traceback
            traceback.print_exc()

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
           
        
        cmds.separator(height=20, style="in")

        
        cmds.frameLayout(
            label="Organize Character and Prop", 
            collapsable=True,
            collapse=True,  
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label="Check Scene", command=CheckScene, 
                   annotation="Ejecuta el Script 1: Scene Checker")
        cmds.button(label="Create main group", command=create_main_group)
        
        cmds.setParent("..")
        cmds.setParent("..")

        
        cmds.frameLayout(
            label="Animation Scene Organization", 
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
        cmds.button(label="Export Selected Groups", command=export_all)
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
            label="CHECK FOR UPDATES", 
            command=self.check_for_updates,
            backgroundColor=[0.2, 0.3, 0.2]
        )
        cmds.setParent("..")
              
        cmds.setParent("..") 
        cmds.setParent("..") 

        cmds.text(label= 'Created by Franz Vega', 
            font="smallObliqueLabelFont",
            align="right",
            )

        cmds.showWindow(self.window)
        



def main():
    """Funcion principal con reload forzado"""
    global pkl_ui
    
    
    modules_to_reload = [
        'pipeline_ui',
        'scene_checker', 
        'animation_organizer',
        'group_creator',
        'camera_exporter',
        'settings',
        'helpers',
        'update_checker',
        'auto_updater'
    ]
    
    for mod_name in modules_to_reload:
        if mod_name in sys.modules:
            try:
                reload(sys.modules[mod_name])
            except NameError:
                import importlib
                importlib.reload(sys.modules[mod_name])
            print("Reloaded: {}".format(mod_name))
    
    
    if cmds.window("pkl_pipeline_ui_window", exists=True):
        cmds.deleteUI("pkl_pipeline_ui_window")
    
    
    pkl_ui = PKLPipelineUI()
    print("PKL Pipeline v{} RELOADED".format(VERSION))

    return pkl_ui
