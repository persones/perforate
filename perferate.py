#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, random

DIST_THRSHOLD = 0.3
RADIUS_THRESHOLD = 0.3

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
    print ("starting")
    
    #print (faces)   
    for f in faces:
        face = adsk.fusion.BRepFace.cast(f)
        print("face")
        sketch = sketches.add(face)
        t = sketch.transform
        #t1 = t.copy()
        t.invert()
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
            
            
                
        
        for i in range(0,2000):
            newPointX = random.random() * (maxx - minx) + minx
            newPointY = random.random() * (maxy - miny) + miny
            testPoint = adsk.core.Point3D.create(newPointX, newPointY, 0)
            
            minDist = 9999
            for edgeIndex in range(0, face.edges.count):
                edge = face.edges.item(edgeIndex)
                c = closestPointToEdge(transformPoint(edge.startVertex.geometry, t), transformPoint(edge.endVertex.geometry, t), testPoint)
                minDist = min(c.distanceTo(testPoint), minDist)    
            for circleIndex in range(0, sketch.sketchCurves.sketchCircles.count):
                circle = sketch.sketchCurves.sketchCircles.item(circleIndex)
                minDist = min(minDist, testPoint.distanceTo(circle.centerSketchPoint.geometry) - circle.radius)
            minDist -= DIST_THRSHOLD
            if minDist > RADIUS_THRESHOLD:
                sketch.sketchCurves.sketchCircles.addByCenterRadius(testPoint, minDist)
        profileCollection = adsk.core.ObjectCollection.create()
        for profileIndex in range(1, sketch.profiles.count):
            profileCollection.add(sketch.profiles.item(profileIndex))
        extInput = extrudes.createInput(profileCollection, adsk.fusion.FeatureOperations.CutFeatureOperation)
        for dir in range (0, 2):
            try:
                extInput.setAllExtent(dir)
                extrudes.add(extInput)
            except:
                print ("nevermind", dir)
        
def transformPoint(p, t):
    copyOfP = p.copy()
    copyOfP.transformBy(t)
    return copyOfP
    
    
def closestPointToEdge(startPoint, endPoint, otherPoint):    
    x1 = startPoint.asArray()[0]
    y1 = startPoint.asArray()[1]
    x2 = endPoint.asArray()[0]
    y2 = endPoint.asArray()[1]
    x3 = otherPoint.asArray()[0]
    y3 = otherPoint.asArray()[1]
    if x2 == x1:
        newPoint = adsk.core.Point3D.create(x1, y3, 0)
    elif y2 == y1:
        newPoint = adsk.core.Point3D.create(x3, y1, 0)
    else:
        m1 = (y2 - y1) / (x2 - x1)
        b1 = y1 - (m1 * x1)
        m2 = -1 / m1
        b2 = y3 - (m2 * x3)    
        x4 = (b2 - b1) / (m1 - m2)
        y4 = m2 * x4 + b2
        newPoint = adsk.core.Point3D.create(x4, y4, 0)
#    print (("otherPoint" ,otherPoint.asArray()))
#    print (("startPoint" ,startPoint.asArray()))
#    print (("endPoint" ,endPoint.asArray()))
#    print (("newPoint" ,newPoint.asArray()))
    return newPoint
    
#def pointToEdgeDistance(startPoint, endPoint, otherPoint):    
#    x1 = startPoint.asArray()[0]
#    y1 = startPoint.asArray()[1]
#    x2 = endPoint.asArray()[0]
#    y2 = endPoint.asArray()[1]
#    x3 = otherPoint.asArray()[0]
#    y3 = otherPoint.asArray()[1]
#    if x2 == x1:
#        newPoint = adsk.core.Point3D.create(x1, y3, 0)
#    elif y2 == y1:
#        newPoint = adsk.core.Point3D.create(x3, y1, 0)
#    else:
#        m1 = (y2 - y1) / (x2 - x1)
#        b1 = y1 - (m1 * x1)
#        m2 = -1 / m1
#        b2 = y3 - (m2 * x3)    
#        x4 = (b2 - b1) / (m1 - m2)
#        y4 = m2 * x4 + b2
#        newPoint = adsk.core.Point3D.create(x4, y4, 0)
#    print (("otherPoint" ,otherPoint.asArray()))
#    print (("startPoint" ,startPoint.asArray()))
#    print (("endPoint" ,endPoint.asArray()))
#    print (("newPoint" ,newPoint.asArray()))
#    return newPoint.distanceTo(otherPoint)


        
    