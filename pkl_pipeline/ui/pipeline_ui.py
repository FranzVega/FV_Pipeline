# -*- coding: utf-8 -*-
"""
PKL Pipeline UI
Drag & Drop installable version
"""
import maya.cmds as cmds
import re

##-- FUNCIONES DE PROCESO (Logica de los botones superiores)
def CheckScene(*args): 
    print("Scene Checked")
    
def create_main_group(*args): 
    print("Group Created")
    
def check_anim_scene(*args): 
    print("Scene ready")
    
def set_camera(*args): 
    print("Camera Set")
    
def orgAnim(*args): 
    print("Organized Scene")
    
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
        self.window_title = "PKL Pipeline v1.0"
        self.create_ui()
        self.update_scene_info()

    def update_scene_info(self, *args):
        """
        Consulta los datos de la escena y actualiza las etiquetas de la UI.
        """
        # 1. Logica de Scene Type
        if cmds.objExists("ANIMATION"):
            scene_type = "Animation Scene"
            type_color = [0.4, 1.0, 0.4] # Verde suave
        else:
            scene_type = "UNIDENTIFIED"
            type_color = [1.0, 0.4, 0.4] # Rojo suave

        # 2. Logica de Frame Range
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        frame_range = "{0} - {1}".format(int(start), int(end))

        # 3. Aplicar a la UI (usando el flag edit=True)
        cmds.text(self.type_label, edit=True, label=scene_type, backgroundColor=type_color)
        cmds.text(self.range_label, edit=True, label=frame_range)
        
        print("UI Updated: {0} | Range: {1}".format(scene_type, frame_range))

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
        cmds.button(label="Check Scene", command=CheckScene)
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
        cmds.button(label="Organize Scene", command=orgAnim)
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

        # --- Section 4: Scene Info (DINAMICA) ---
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
       
        cmds.separator(height=10, style="in")
                
        # Boton de Update
        cmds.button(
            label="UPDATE SCENE INFO", 
            command=self.update_scene_info, 
            backgroundColor=[0.2, 0.2, 0.2]
        )
              
        cmds.setParent("..") 
        cmds.setParent("..") 

        cmds.showWindow(self.window)


##-- MAIN FUNCTION (REQUERIDA para drag & drop install)
def main():
    """
    Funcion principal que se llama desde el shelf button.
    Intenta reload del modulo para que los cambios se reflejen sin reiniciar Maya.
    """
    global pkl_ui
    
    try:
        # Recargar el modulo si ya esta cargado (util durante desarrollo)
        import sys
        if 'pipeline_ui' in sys.modules:
            # Python 2/3 compatible reload
            try:
                reload(sys.modules['pipeline_ui'])
            except NameError:
                import importlib
                importlib.reload(sys.modules['pipeline_ui'])
    except:
        pass
    
    # Crear/mostrar la UI
    pkl_ui = PKLPipelineUI()
    print("PKL Pipeline UI launched successfully!")
    return pkl_ui


# Si ejecutas el script directamente desde el Script Editor
if __name__ == "__main__":
    main()