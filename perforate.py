import adsk.core, adsk.fusion, adsk.cam, traceback, random

DIST_THRSHOLD = 0.3
RADIUS_THRESHOLD = 0.1

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
    except:
        if ui:
           ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    des = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = des.rootComponent
    sketches = rootComp.sketches   
    extrudes = rootComp.features.extrudeFeatures      
    selections = ui.activeSelections
    
    faces = []
    for selection in selections:                
        if selection.entity.objectType == adsk.fusion.BRepFace.classType():
            faces.append(adsk.fusion.BRepFace.cast(selection.entity))
    
    for f in faces:
        face = adsk.fusion.BRepFace.cast(f)
        print("face")
        sketch = sketches.add(face)
        t = sketch.transform
        t.invert()
        
        #bounding box for the face. all holes must fall here 
        minx = 9999
        maxx = -9999
        miny = 9999
        maxy = -9999
        for i in range(0, face.vertices.count):
            v = face.vertices.item(i).geometry.copy()
            v.transformBy(t)
            minx = min(minx, v.asArray()[0])
            miny = min(miny, v.asArray()[1])
            maxx = max(maxx, v.asArray()[0])
            maxy = max(maxy, v.asArray()[1])
        
        
        for i in range(0,4000):
            # center for new hole
            newPointX = random.random() * (maxx - minx) + minx
            newPointY = random.random() * (maxy - miny) + miny
            testPoint = adsk.core.Point3D.create(newPointX, newPointY, 0)
            
            minDist = 9999
            # stay away from edges
            for edgeIndex in range(0, face.edges.count):
                edge = face.edges.item(edgeIndex)
                c = closestPointToEdge(transformPoint(edge.startVertex.geometry, t), transformPoint(edge.endVertex.geometry, t), testPoint)
                minDist = min(c.distanceTo(testPoint), minDist)    
            #stay away from other circles
            for circleIndex in range(0, sketch.sketchCurves.sketchCircles.count):
                circle = sketch.sketchCurves.sketchCircles.item(circleIndex)
                minDist = min(minDist, testPoint.distanceTo(circle.centerSketchPoint.geometry) - circle.radius)
            minDist -= DIST_THRSHOLD
            #actaully create hole on sketch
            if minDist > RADIUS_THRESHOLD:
                sketch.sketchCurves.sketchCircles.addByCenterRadius(testPoint, minDist)
        
        # to extrude, we need profiles.
        profileCollection = adsk.core.ObjectCollection.create()
        for profileIndex in range(1, sketch.profiles.count):
            profileCollection.add(sketch.profiles.item(profileIndex))
        # make the extrusion input
        extInput = extrudes.createInput(profileCollection, adsk.fusion.FeatureOperations.CutFeatureOperation)
        
        # try to extrude in both directions        
        for dir in range (0, 2):
            try:
                extInput.setAllExtent(dir)
                extrudes.add(extInput)
            except:
                print ("nevermind", dir)
        
# not sure that this is necessary, but I think it is
def transformPoint(p, t):
    copyOfP = p.copy()
    copyOfP.transformBy(t)
    return copyOfP
    
# how *do* we find the closest point to the edge?
def closestPointToEdge(startPoint, endPoint, otherPoint):    
    x1 = startPoint.asArray()[0]
    y1 = startPoint.asArray()[1]
    x2 = endPoint.asArray()[0]
    y2 = endPoint.asArray()[1]
    x3 = otherPoint.asArray()[0]
    y3 = otherPoint.asArray()[1]
    
    # edge cases: straight angles
    if x2 == x1:
        newPoint = adsk.core.Point3D.create(x1, y3, 0)
    elif y2 == y1:
        newPoint = adsk.core.Point3D.create(x3, y1, 0)
    else:
        # line equation of the edge
        m1 = (y2 - y1) / (x2 - x1)
        b1 = y1 - (m1 * x1)
        
        # the line connecting the closest point on the edge to our point must be orthogonal to the edge        
        m2 = -1 / m1
        # and must pass through our point
        b2 = y3 - (m2 * x3)
        
        # the closest point sits on the edge and the line. 
        x4 = (b2 - b1) / (m1 - m2)
        y4 = m2 * x4 + b2
        # there you go
        newPoint = adsk.core.Point3D.create(x4, y4, 0)
    return newPoint
    
