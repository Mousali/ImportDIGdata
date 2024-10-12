import io
import re
import traceback
from copy import copy

import adsk.core
import adsk.fusion


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        # Get all components in the active design.
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        title = "Import Centroid Spline dig data"
        if not design:
            ui.messageBox(
                "The DESIGN workspace must be active when running this script.", title
            )
            return

        dlg = ui.createFileDialog()
        dlg.title = "Open DIG File"
        dlg.filter = "dig data (*.dig);;All Files (*.*)"
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        filename = dlg.filename
        with io.open(filename, "r", encoding="utf-8-sig") as f:
            first_spline = True
            points = []
            splines = []
            for line in f:
                if line.lstrip() == "":
                    continue
                if line.lstrip()[0] in [";", ":", "M", "G"]:
                    continue

                pntStrArr = line.split(" ")

                if pntStrArr[1][0] == "Y":
                    if first_spline:
                        first_spline = False
                    else:
                        splines.append(copy(points))
                        points.clear()

                    current_y = round(float(pntStrArr[1][1:]) / 10, 2)

                    p = (
                        round(float(pntStrArr[0][1:]) / 10, 2),
                        current_y,
                        round(float(pntStrArr[2][1:]) / 10, 2),
                    )
                else:
                    p = (
                        round(float(pntStrArr[0][1:]) / 10, 2),
                        current_y,
                        round(float(pntStrArr[1][1:]) / 10, 2),
                    )

                if len(points) == 0:
                    points.append(p)
                elif points[-1] == p:
                    continue
                else:
                    points.append(p)

            splines.append(copy(points))

        root = design.rootComponent
        sketch = root.sketches.add(root.xYConstructionPlane)
        points = adsk.core.ObjectCollection.create()
        for splin_points in splines:
            for p in splin_points:
                point = adsk.core.Point3D.create(p[0], p[1], p[2])
                points.add(point)

            s = sketch.sketchCurves.sketchFittedSplines.add(copy(points))
            # s.isClosed = True
            points.clear()

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
