# -*- coding: utf-8 -*-
"""
PKL Pipeline UI
Drag & Drop installable version
"""
import maya.cmds as cmds
import sys
import os

# Setup paths - Para estructura: pkl_pipeline/ui/, pkl_pipeline/core/, pkl_pipeline/config/
def setup_paths():
    """Configura los paths necesarios"""
    # El install.mel agrega pkl_pipeline/ui/ a sys.path
    # Necesitamos encontrar pkl_pipeline/ (el parent)
    
    ui_path = None
    for path in sys.path:
        # Buscar un path que termine en 'ui' o 'ui/'
        normalized = path.replace('\\', '/').rstrip('/')
        if normalized.endswith('/ui') or normalized.endswith('ui'):
            # Verificar que pipeline_ui.py existe ahi
            test_file = os.path.join(path, 'pipeline_ui.py')
            if os.path.exists(test_file):
                ui_path = path
                break
    
    if ui_path:
        # Parent es pkl_pipeline/
        parent_dir = os.path.dirname(ui_path.rstrip('/\\'))
        
        # core y config estan al mismo nivel que ui
        core_dir = os.path.join(parent_dir, 'core')
        config_dir = os.path.join(parent_dir, 'config')
        
        print("PKL Pipeline - Setup paths:")
        print("  UI dir:     {}".format(ui_path))
        print("  Parent dir: {}".format(parent_dir))
        print("  Core dir:   {}".format(core_dir))
        print("  Config dir: {}".format(config_dir))
        
        # Verificar que existen
        if os.path.exists(core_dir):
            print("  [OK] Core directory found")
        else:
            print("  [ERROR] Core directory NOT found!")
            
        if os.path.exists(config_dir):
            print("  [OK] Config directory found")
        else:
            print("  [ERROR] Config directory NOT found!")
        
        # Agregar al path
        for p in [parent_dir, core_dir, config_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)
                print("  Added to sys.path: {}".format(p))
        
        return True
    else:
        print("PKL Pipeline ERROR: Could not find UI directory")
        return False

# Setup paths
setup_paths()

# Importar modulos core
try:
    import scene_checker
    import animation_organizer
    import settings
    
    # Importar funciones con fallback
    check_scene = getattr(scene_checker, 'check_scene', None)
    organize_animation = getattr(animation_organizer, 'organize_animation', None)
    
    # Si no existen las funciones, crear fallbacks
    if check_scene is None:
        print("  Warning: check_scene function not found in scene_checker module")
        def check_scene(): print("Scene Checked (No function found)")
    
    if organize_animation is None:
        print("  Warning: organize_animation function not found in animation_organizer module")
        def organize_animation(): print("Animation Organized (No function found)")
    
    VERSION = settings.VERSION
    
    print("PKL Pipeline: Core modules loaded successfully! v{}".format(VERSION))
    
except ImportError as e:
    print("PKL Pipeline Warning: Could not import core modules")
    print("Error: {}".format(e))
    import traceback
    traceback.print_exc()
    # Fallback a funciones dummy
    def check_scene(): print("Scene Checked (Fallback)")
    def organize_animation(): print("Animation Organized (Fallback)")
    VERSION = "1.0.0"


##-- FUNCIONES DE PROCESO (Conectadas con Core)
def CheckScene(*args): 
    """Llama al script 1 del core"""
    check_scene()
    
def create_main_group(*args): 
    print("Group Created")
    
def check_anim_scene(*args): 
    print("Scene ready")
    
def set_camera(*args): 
    print("Camera Set")
    
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
    print("Camera exported")


##-- UI CLASS
class PKLPipelineUI(object):
    def __init__(self):
        self.window_id = "pkl_pipeline_ui_window"
        self.window_title = "PKL Pipeline v{}".format(VERSION)
        self.create_ui()
        self.update_scene_info()

    def update_scene_info(self, *args):
        """
        Consulta los datos de la escena y actualiza las etiquetas de la UI.
        """
        # 1. Logica de Scene Type
        if cmds.objExists("ANIMATION"):
            scene_type = "Animation Scene"
            type_color = [0.4, 1.0, 0.4]
        else:
            scene_type = "UNIDENTIFIED"
            type_color = [1.0, 0.4, 0.4]

        # 2. Logica de Frame Range
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        frame_range = "{0} - {1}".format(int(start), int(end))

        # 3. Aplicar a la UI
        cmds.text(self.type_label, edit=True, label=scene_type, backgroundColor=type_color)
        cmds.text(self.range_label, edit=True, label=frame_range)
        
        print("UI Updated: {0} | Range: {1}".format(scene_type, frame_range))
    
    def check_for_updates(self, *args):
        """
        Verifica si hay actualizaciones disponibles en GitHub
        """
        try:
            # Importar update checker con manejo robusto de paths
            import sys
            import os
            
            # Encontrar el directorio pkl_pipeline
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
                
                print("Checking for update_checker in: {}".format(utils_dir))
                
                # Verificar que existe
                update_checker_file = os.path.join(utils_dir, 'update_checker.py')
                if not os.path.exists(update_checker_file):
                    raise Exception("update_checker.py not found at: {}".format(update_checker_file))
                
                # Agregar al path
                if utils_dir not in sys.path:
                    sys.path.insert(0, utils_dir)
                    print("Added to sys.path: {}".format(utils_dir))
                
                # Intentar importar
                import update_checker
                print("update_checker imported successfully!")
                
                result = update_checker.check_updates()
                
                # Mostrar resultado en dialogo
                if result.get('available'):
                    message = "Update Available!\n\n"
                    message += "Current: {}\n".format(result.get('current_version'))
                    message += "Latest:  {}\n\n".format(result.get('latest_version'))
                    message += "Check the Script Editor for update instructions."
                    
                    response = cmds.confirmDialog(
                        title='Update Available',
                        message=message,
                        button=['Show Instructions', 'Close'],
                        defaultButton='Show Instructions',
                        cancelButton='Close',
                        icon='information'
                    )
                    
                    if response == 'Show Instructions':
                        update_checker.show_update_instructions()
                    
                else:
                    message = result.get('message', 'You are up to date!')
                    if 'error' in result:
                        message += "\n\nError: {}".format(result['error'])
                    
                    cmds.confirmDialog(
                        title='No Updates',
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
        """
        # Confirmar con el usuario
        response = cmds.confirmDialog(
            title='Auto Update',
            message='This will REPLACE all your files.\n\n'                    
                    'You will need to restart the tool after updating.\n\n'
                    'Continue?',
            button=['Yes, Update', 'Cancel'],
            defaultButton='Cancel',
            cancelButton='Cancel',
            icon='warning'
        )
        
        if response != 'Yes, Update':
            return
        
        try:
            # Importar auto_updater
            import sys
            import os
            
            # Encontrar utils directory
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
                
                # Recargar si ya existe
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
                    message += "Please CLOSE and REOPEN the tool to use the new version."
                    
                    cmds.confirmDialog(
                        title='Update Complete',
                        message=message,
                        button=['OK'],
                        icon='information'
                    )
                    
                    # Cerrar la UI automaticamente
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
            widthHeight=(300, 600),
            sizeable=True
        )

        main_scroll = cmds.scrollLayout(childResizable=True)
        main_col = cmds.columnLayout(adjustableColumn=True, parent=main_scroll)

        # --- Section 1: Character & Prop ---
        cmds.frameLayout(
            label="Organize Character and Prop", 
            collapsable=True, 
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label="Check Scene", command=CheckScene, 
                   annotation="Ejecuta el Script 1: Scene Checker")
        cmds.button(label="Create main group", command=create_main_group)
        cmds.checkBox(label="AdvancedSkeleton Logic")
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Section 2: Animation Organization ---
        cmds.frameLayout(
            label="Animation Scene Organization", 
            collapsable=True, 
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label="Check Animation Scene", command=check_anim_scene)
        cmds.button(label="Set Selected Camera", command=set_camera)
        cmds.button(label="Organize Scene", command=orgAnim,
                   annotation="Ejecuta el Script 2: Animation Organizer")
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Section 3: Export to Unreal ---
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
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Section 4: Scene Info ---
        cmds.frameLayout(
            label="Scene Info", 
            collapsable=True, 
            marginWidth=5, 
            marginHeight=5, 
            parent=main_col
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5) 
        
        # Fila 1: Tipo de Escena
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[85, 100])
        cmds.text(label="Scene Type:", align="left", font="boldLabelFont")
        self.type_label = cmds.text(label="Detecting...", align="center")
        cmds.setParent("..")
        
        # Fila 2: Rango de Frames
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[85, 100])
        cmds.text(label="Frame Range:", align="left", font="boldLabelFont")
        self.range_label = cmds.text(label="0 - 0", align="center")
        cmds.setParent("..")
        
        # Fila 3: Version
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[85, 100])
        cmds.text(label="Version:", align="left", font="boldLabelFont")
        cmds.text(label=VERSION, align="center", backgroundColor=[0.2, 0.2, 0.3])
        cmds.setParent("..")
       
        cmds.separator(height=10, style="in")
        
        # Botones de accion
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
        
        cmds.separator(height=5, style="none")
        
        # Boton de auto-update (mas prominente)
        cmds.button(
            label="AUTO UPDATE FROM GITHUB", 
            command=self.auto_update_pipeline,
            backgroundColor=[0.3, 0.5, 0.3],
            annotation="Downloads and replaces all files from GitHub (NO backup)"
        )
              
        cmds.setParent("..") 
        cmds.setParent("..") 

        cmds.showWindow(self.window)


##-- MAIN FUNCTION
def main():
    """
    Funcion principal que se llama desde el shelf button.
    """
    global pkl_ui
    
    try:
        # Recargar modulos
        import sys
        if 'pipeline_ui' in sys.modules:
            try:
                reload(sys.modules['pipeline_ui'])
            except NameError:
                import importlib
                importlib.reload(sys.modules['pipeline_ui'])
        
        for mod in ['scene_checker', 'animation_organizer', 'settings']:
            if mod in sys.modules:
                try:
                    reload(sys.modules[mod])
                except NameError:
                    import importlib
                    importlib.reload(sys.modules[mod])
    except Exception as e:
        print("Reload warning: {}".format(e))
    
    # Crear/mostrar la UI
    pkl_ui = PKLPipelineUI()
    print("=" * 60)
    print("PKL Pipeline v{} launched successfully!".format(VERSION))
    print("=" * 60)
    return pkl_ui


if __name__ == "__main__":

    main()

