
import maya.cmds as cmds
import maya.mel as mel
from collections import defaultdict

def _get_geo_transforms():
    """Retorna los transforms de las mallas poligonales."""
    return [
        t for t in cmds.ls(type="transform", long=True)
        if cmds.listRelatives(t, shapes=True, type="mesh")
    ]

def _run_cleanup_select(flags_list):
    """
    Ejecuta el cleanup de Maya en modo seleccion.
    Convierte la lista de flags a un array de strings para MEL.
    """
    quoted_flags = ['"{}"'.format(f) for f in flags_list]
    arg_string = ",".join(quoted_flags)
    mel_cmd = 'polyCleanupArgList 3 {{{}}};'.format(arg_string)
    mel.eval(mel_cmd)

def model_check_cleanup():
    error_map = defaultdict(lambda: defaultdict(int))
    all_problem_components = []
    objects_to_freeze = []

    geos = _get_geo_transforms()
    if not geos:
        cmds.warning("No polygon geometry found in the scene.")
        return

    
    
    checks = [
        ("Ngons (more than 4 sides)", 2),
        ("Faces with holes", 4),
        ("Non-planar faces", 5),
        ("Lamina faces", 6),
        ("Non-manifold geometry", 7),
        ("Zero length edges", 9),
    ]

    for label, index in checks:
        flags = ["0"] * 31 
        flags[0] = "1" 
        flags[index] = "1"

        cmds.select(geos, r=True)
        _run_cleanup_select(flags)

        faces = cmds.ls(sl=True, fl=True) or []
        for f in faces:
            if "." in f:
                geo = f.split(".")[0]
                error_map[geo][label] += 1
                all_problem_components.append(f)

    
    for geo in geos:
        
        t = cmds.getAttr(geo + ".t")[0]
        r = cmds.getAttr(geo + ".r")[0]
        s = cmds.getAttr(geo + ".s")[0]
        
        needs_freeze = False
        if any(abs(v) > 0.001 for v in t): needs_freeze = True
        if any(abs(v) > 0.001 for v in r): needs_freeze = True
        if any(abs(1.0 - v) > 0.001 for v in s): needs_freeze = True
        
        if needs_freeze:
            error_map[geo]["Unfrozen Transformations"] = 1
            objects_to_freeze.append(geo)

    
    final_selection = all_problem_components + objects_to_freeze
    
    if final_selection:
        cmds.select(final_selection, r=True)
        
        report = []
        for geo, errors in error_map.items():
            report.append(" Object: {}".format(geo))
            for err, count in errors.items():
                if err == "Unfrozen Transformations":
                    report.append("    - [!] Unfrozen Transformations")
                else:
                    report.append("    - {} ({})".format(err, count))
            report.append("-" * 30)

        cmds.confirmDialog(
            title="Modeling Report",
            message="\n".join(report),
            button=["OK"],
            icon="warning"
        )
    else:
        cmds.select(clear=True)
        cmds.confirmDialog(
            title="Model Check",
            message="No geometry issues found!",
            button=["OK"],
            icon="information"
        )



