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
            ps = []
            for line in f:
                if line.lstrip() == "":
                    continue
                if line.lstrip()[0] in [";", ":", "M", "G"]:
                    continue

                pntStrArr = list(
                    filter(None, re.split(r"X\s+|\s+[YZ]?\s+", line.strip()))
                )

                p = (
                    round(float(pntStrArr[0]) / 10, 2),
                    round(float(pntStrArr[1]) / 10, 2),
                    round(float(pntStrArr[2]) / 10, 2),
                )

                if len(ps) == 0:
                    ps.append(p)
                elif ps[-1] != p:
                    ps.append(p)

        root = design.rootComponent
        sketch = root.sketches.add(root.xYConstructionPlane)
        points = adsk.core.ObjectCollection.create()
        for p in ps:
            point = adsk.core.Point3D.create(p[0], p[1], p[2])
            points.add(point)

        s = sketch.sketchCurves.sketchFittedSplines.add(points)
        s.isClosed = True

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
