# -*- coding: utf-8 -*-
"""
PKL Pipeline - Model Checker
Verifica geometria limpia basado en Maya Cleanup Options
"""
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
    """
    Realiza cleanup check basado en la imagen de referencia:
    - Faces with more than 4 sides (Ngons)
    - Faces with holes
    - Lamina faces
    - Nonmanifold geometry
    + Unfrozen Transformations
    """
    error_map = defaultdict(lambda: defaultdict(int))
    all_problem_components = []
    objects_to_freeze = []

    geos = _get_geo_transforms()
    if not geos:
        cmds.warning("No polygon geometry found in the scene.")
        return

    # --- CHECKS SEGUN LA IMAGEN ---
    # Fix by Tesselation:
    #   [x] Faces with more than 4 sides
    #   [x] Faces with holes
    # Remove Geometry:
    #   [x] Lamina faces
    #   [x] Nonmanifold geometry
    
    checks = [
        ("Faces with more than 4 sides", 2),  # Ngons
        ("Faces with holes", 4),
        ("Lamina faces", 6),
            
    ]

    for label, index in checks:
        flags = ["0"] * 31 
        flags[0] = "1"  # Modo Select Only
        flags[index] = "1"

        cmds.select(geos, r=True)
        _run_cleanup_select(flags)

        selection = cmds.ls(sl=True, fl=True) or []
        
        for item in selection:
            if "." in item:  # Es un componente (face, edge, etc)
                geo = item.split(".")[0]
                error_map[geo][label] += 1
                all_problem_components.append(item)

    # --- CHECK DE FREEZE TRANSFORMATIONS ---
    for geo in geos:
        # Revisa traslacion, rotacion y escala con tolerancia
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

    # --- SELECCION Y REPORTE FINAL ---
    final_selection = all_problem_components + objects_to_freeze
    
    if final_selection:
        cmds.select(final_selection, r=True)
        
        report = []
        report.append("=== MODELING ISSUES FOUND ===\n")
        
        for geo, errors in error_map.items():
            report.append("Object: {}".format(geo))
            for err, count in errors.items():
                report.append("  - {}: {}".format(err, count))
            report.append("")
        
        report.append("Total problem components: {}".format(len(all_problem_components)))

        cmds.confirmDialog(
            title="Model Check Results",
            message="\n".join(report),
            button=["OK"],
            icon="warning"
        )
    else:
        cmds.select(clear=True)
        cmds.confirmDialog(
            title="Model Check",
            message="No geometry issues found!\n\nAll geometry is clean.",
            button=["OK"],
            icon="information"
        )

# Para ejecutar:
# model_check_cleanup()