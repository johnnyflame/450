################################################################################
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This is free software; you may redistribute it, and/or modify it,
# under the terms of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License (http://www.gnu.org/licenses/) for more details.
#
# ***** END GPL LICENSE BLOCK *****
'''
Create a "column" at 3D cursor as architectural/decorative object in a scene.
 Column components: plinth, base, shaft, capital, and finale.

'''
# Author(s): Jambay
# Version: 0, 1, 1
#
# @todo: main community complaint is "performance" - too slow...
#  Work on optimizing operations.
# @todo: Add pedestal.
# @todo: Create Ionic and Corinthian style capitals.
#
################################################################################

import bpy
import mathutils
from math import radians, pi, sin, cos
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, BoolProperty, EnumProperty
from add_mesh_building_basics.UtilMats import uMatRGBSet

################################################################################
#
# Set parameters for selected style.
#
#  All styles are based on default settings - they only set differences.
#   User modifications will affect results depending on previous selection
#   or manual adjustment. Use "Default" style to reset.
#
# @todo: Create more styles.
#
def ColumnStyles(sRef,colStyle):

    if colStyle=='0': # set/reset defaults
        sRef.col_plinth=False
#        sRef.plinth_height=0.10
#        sRef.plinth_width=0.6

        sRef.col_base=True
        sRef.base_type=1
        sRef.base_faces=5
        sRef.base_height=0.25
        sRef.base_width=0.4

        sRef.col_cap=True
        sRef.cap_type=1
        sRef.cap_faces=5
        sRef.cap_height=0.25
        sRef.cap_width=0.4

        sRef.col_finale=False
#        sRef.finale_height=0.10
#        sRef.finale_width=0.6

    if colStyle=='1': # Tuscan
        sRef.col_plinth=True
        sRef.plinth_height=0.10
        sRef.plinth_width=0.6

        sRef.col_finale=True
        sRef.finale_height=0.10
        sRef.finale_width=0.6


################################################################################
#
# Generate a series of vertices and edges as an object outline.
#
def makeProfile(orgX, orgZ, endX, itmZ, itmR, itmS=0, mulX=0, mulZ=0, dblZ=True, dblU=True, nxtR=0):
    '''
   Create list of vertexes and edges that outline defined shape (as per parameters).

    Params:
        orgX    Horizontal origin for vertexes; 0 for closed shapes.
        orgZ    Vertical origin.
        endX    Radius end-point for vertexes; 0 for closed shapes.
        itmZ    Vertical offset from orgZ for shape (top).
        itmR    Radius of shape.
        itmS    Number of vertical steps (rows), use 0 for straight.
        mulX    Horizontal multiplier.
        mulZ    Vertical multiplier, used with dblZ.
        dblZ    double mulZ for each row if true.
        dblU    Repeat inverse of shape if true.
        nxtR    Edge list for concatenated shapes.

    Returns:
        list of vertices and edges
    '''
    shapeVerts = []
    shapeEdges = []

    halfH = itmZ/2 # common value, effeciency.
    halfR = itmR/2 # common value, effeciency.

    workX = orgX # origin for segments.
    workR = workX+halfR # "working radius" for item.
    workZ = 0

    rowVariance = 0
    workMulZ = 0

    numRows = nxtR

    if itmS:
        rowVariance = halfR/itmS # number of angles to curve edge
    else:
        dblU = False # override default for square.

    shapeVerts.append([0, workX, orgZ]) # starting point

    for Ivec in range(itmS): # skipped if no rows
        workX = workR+rowVariance*(Ivec*mulX) # set horizontal
        workZ = orgZ+halfH*workMulZ # set vertical

        shapeVerts.append([0, workX, workZ])
        shapeEdges.append([numRows, numRows+1])
        numRows += 1

        if dblZ:
            if Ivec:
                workMulZ *= 2
            else:
                workMulZ = mulZ
        else:
            workMulZ = Ivec * mulZ

    # middle row... outer edge; bottom if no rows.
    workZ = orgZ # set standard origin

    if itmS: # shaped?
        workX = workR+rowVariance*((itmS-1)*mulX)
        workZ += halfH
    else: # square
        workX = workR+halfR

    shapeVerts.append([0, workX, workZ])
    shapeEdges.append([numRows, numRows+1])
    numRows += 1

    # do the middle up part...
    if dblU:
        for Rvec in range(1,itmS): # inverse...

            if dblZ:
                workMulZ /= 2
            else:
                workMulZ = Rvec * mulZ

            workX = workR+rowVariance*((itmS-Rvec)*mulX) # set horizontal
            workZ = orgZ+itmZ-halfH*workMulZ # set vertical

            shapeVerts.append([0, workX, workZ])
            shapeEdges.append([numRows, numRows+1]) 
            numRows += 1

    # finalize...
    workX = orgX+itmR
    workZ = orgZ+itmZ

    if dblU: # match top to bottom for rounded styles
        shapeVerts.append([0, workR, workZ])
    else:
        shapeVerts.append([0, workX, workZ])

    shapeEdges.append([numRows, numRows+1]) # outer edge top
    numRows += 1

    shapeVerts.append([0, endX, workZ])
    shapeEdges.append([numRows, numRows+1]) # last edge....

    return shapeVerts, shapeEdges


################################################################################
#
# Create standard "Stackable" shapes using makeProfile.
#
def makeSeg(segTy, segCt, segXo, segZo, segXe, segZe, segRw, seg2=True, segI=True, segL=0):
    '''
   Create list of vertexes and edges for shape.

    Params:
        segTy   Type of segment to generate.
        segCt   Segment rows.
        segXo   Radius origin for vertexes; 0 for closed shapes.
        segZo   Vertical origin.
        segXe   Radius end-point for vertexes; 0 for closed shapes.
        segZe   Vertical offset from segZo for shape top.
        segRw   Radius (width) of shape.
        seg2    doubler for each facet if true.
        segI    Repeat inverse of shape if true.
        segL    Edge list for concatenated shapes.

    Returns:
        list of vertices and edges from makeProfile.
    '''
    if segTy == 0: # ...
        return makeProfile(segXo, segZo, segXe, segZe, segRw, segCt, 0, 0, seg2, segI, segL)

    if segTy == 1: # ...
        return makeProfile(segXo, segZo, segXe, segZe, segRw, segCt, 1, 1, seg2, segI, segL)

    if segTy == 2: # ...
        return makeProfile(segXo, segZo, segXe, segZe, segRw, segCt, 1.2, 0.05, seg2, segI, segL)

    if segTy == 3: # ...
        return makeProfile(segXo, segZo, segXe, segZe, segRw, segCt, 1.3, 0.05, seg2, segI, segL)

    if segTy == 4: # ...
        return makeProfile(segXo, segZo, segXe, segZe, segRw, segCt, -0.75, 0.05, seg2, segI, segL)

    if segTy == 5: # ...
        return makeProfile(segXo, segZo, segXe, segZe, segRw, segCt, 1, 0.15, seg2, segI, segL)


############################################################
#
#    Rotate shape... finish 360 as a handler sub-routine
#
def obj_360(objName, objVert, objEdge, objScene, objSteps=1):
    objMesh = bpy.data.meshes.new(objName)
    objMesh.from_pydata(objVert, objEdge, [])
    objMesh.update()

    # generate object
    ob_new = bpy.data.objects.new(objName, objMesh)
    objScene.objects.link(ob_new)
    objScene.objects.active = ob_new
    ob_new.select = True

    # add faces/steps
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.spin(steps=objSteps, dupli=False, center=(0,0,0), axis=(0,0,1))
    bpy.ops.mesh.spin(steps=objSteps, dupli=False, center=(0,0,0), axis=(0,0,1))
    bpy.ops.mesh.spin(steps=objSteps, dupli=False, center=(0,0,0), axis=(0,0,1))
    bpy.ops.mesh.spin(steps=objSteps, dupli=False, center=(0,0,0), axis=(0,0,1))
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.editmode_toggle()


################################################################################
#
# A very simple "bridge" tool.
#
def createFaces(vertIdx1, vertIdx2, vertLoop=True, flipped=False):
    '''
   Connects two vertex list rows with faces.

    Parameters:
        vertIdx1  First vertex list (list of vertex indices) == 1 for fan/star.
        vertIdx2  Second vertex list - minimum 2.
        vertLoop  Creates a loop (first & last are closed). # True for now...
        flipped   Invert the normals for faces. # False for now....

    Returns:
        itmFaces  a list of faces (list of  lists); "None" for invalid options.
    '''
    # ensure there are lists to work with.
    if not vertIdx1 or not vertIdx2:
        return None

    # check minimum second list verts.
    if len(vertIdx2) < 2:
        return None

    itmFaces = []
    workFace = []
    fanFaces = False

    # vert lists must match if not fan/star effect.
    if len(vertIdx1) != len(vertIdx2):
        if len(vertIdx1) == 1:
            fanFaces = True
        else:
            return None

    total = len(vertIdx2)

    # Bridge the start with the end.
    if vertLoop:
        if flipped:
            workFace = [
                vertIdx1[0],
                vertIdx2[0],
                vertIdx2[total - 1]]

            if not fanFaces:
                workFace.append(vertIdx1[total - 1])

            itmFaces.append(workFace)
        else:
            workFace = [vertIdx2[0], vertIdx1[0]]
            if not fanFaces:
                workFace.append(vertIdx1[total - 1])

            workFace.append(vertIdx2[total - 1])

            itmFaces.append(workFace)

    # Bridge the rest of the faces.
    for num in range(total - 1):
        if flipped:
            if fanFaces:
                workFace = [vertIdx2[num], vertIdx1[0], vertIdx2[num + 1]]
            else:
                workFace = [vertIdx2[num], vertIdx1[num],
                    vertIdx1[num + 1], vertIdx2[num + 1]]

            itmFaces.append(face)
        else:
            if fanFaces:
                workFace = [vertIdx1[0], vertIdx2[num], vertIdx2[num + 1]]
            else:
                workFace = [vertIdx1[num], vertIdx2[num],
                    vertIdx2[num + 1], vertIdx1[num + 1]]

            itmFaces.append(workFace)

    return itmFaces


################################################################################
#
# Create a decorative/stylized base of column.
#
def add_extent_base(startX, endX, shapeZ, shapeR, startZ, matchR, shapeT=1):
    '''
   Create geometry for column base.

    Params:
	startX   origin for vertexes.
	endX     end for vertexes.
	shapeZ   vertical area of item.
	shapeR   radius of item.
	startZ   vertical origin.
	matchR   column radius,including extruded flutes.
	shapeT   type of item to generate.

    Returns:
	list of vertices and edges (mostly) generated by makeSeg.
    '''
    verts = []
    edges = []

    workR = matchR
    workX = startX
    workZ = startZ
    workH = shapeZ

    if shapeT == 1: # attempt to create Tuscan style base...

        workR = shapeR
        stepModW = workR/10 # set segement width step modifier

        workH = shapeZ/8
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR -= stepModW
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workX = startX+workR/2 # mod x origin for inverted shape
        workR -= stepModW
        workZ += workH
        workH = shapeZ/2
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(4, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workX = startX # restore x origin
        workR = matchR # width to match column.
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # connector edge...
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        return verts, edges

    if shapeT == 2:
        return makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))

    if shapeT == 3:
        return makeSeg(1, 1, workX, workZ, endX, workH, workR, False, False, len(edges))

    if shapeT == 4:
        return makeSeg(2, 6, workX, workZ, endX, workH, workR, segI=False, segL=len(edges))

    if shapeT == 5:
        return makeSeg(1, 2, workX, workZ, endX, workH, workR, False, False, len(edges))

    if shapeT == 6:
        return makeSeg(5, 6, workX, workZ, endX, workH, workR, False, segL=len(edges))

    if shapeT == 7:

        workR = shapeR
        workH = shapeZ/8
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        workH = shapeZ/4
        edges.append([len(edges), len(edges)+1])
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        workH = shapeZ/8
        edges.append([len(edges), len(edges)+1])
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        workH = shapeZ/4
        edges.append([len(edges), len(edges)+1])
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = matchR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1])
        verts1, edges1 = makeSeg(1, 2, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        return verts, edges

# nice example to use modulo for steps (loop+1 to finish); 5 steps...
    if shapeT == 8:

        workR = shapeR
        workH = shapeZ/8
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR/2
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # connector edge...
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR/4
        workZ += workH
        edges.append([len(edges), len(edges)+1])
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR/2
        workZ += workH
        workH = shapeZ/4
        edges.append([len(edges), len(edges)+1])
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = matchR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(3, 6, workX, workZ, endX, workH, workR, False, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        return verts, edges

    if shapeT == 10:

        workR = shapeR/4
        workH = shapeZ/4
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        edges.append([len(edges), len(edges)+1]) # connector edge...
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = matchR # width to match column.
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(1, 2, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        return verts, edges

    if shapeT == 11: # attempt to create Tuscan style base... round 2

        workR = shapeR
        stepModW = workR/10 # segement width modifier

        workH = shapeZ/8
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR -= stepModW
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR -= stepModW
        workZ += workH
        workH = shapeZ/2
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = matchR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        return verts, edges

##########
# default: shapeT not recognized - straight side, full height.
    return makeSeg(0, 0, workX, workZ, endX, workH, workR)


################################################################################
#
# Create captial, a decorative/stylized top of column.
#
def add_extent_capital(startX, endX, shapeZ, shapeR, startZ, matchR, shapeT=1):
    '''
   Create column "capital".

    Params:
	startX   origin for vertexes.
	endX     end for vertexes.
	shapeZ   vertical area of item.
	shapeR   horizontal area of item, tapered for column.
	startZ   vertical origin.
	matchR   column radius, with flutes and taper, used for match/proportion.
	shapeT   type of item to generate.

    Returns:
	list of vertices and edges.
    '''
    verts = []
    edges = []

    workX = startX # start for most segments.
    workZ = startZ # vertical origin.
    workR = matchR # set radius to match column.
    workH = shapeZ # set full/default segment height.

    if shapeT == 1: # attempt to create Tuscan style capital.

        workH = shapeZ/4
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workX = startX+workR/2 # mod x origin for inverted shape
        workZ += workH
        workH = shapeZ/2
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(4, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workX = startX # restore x origin
        workZ += workH
        workH = shapeZ/8
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

    elif shapeT == 2:
        verts, edges = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))

    elif shapeT == 3:
        verts, edges = makeSeg(1, 1, workX, workZ, endX, workH, workR, False, False, len(edges))

    elif shapeT == 4:
        verts, edges = makeSeg(2, 6, workX, workZ, endX, workH, workR, segI=False, segL=len(edges))

    elif shapeT == 5:
        verts, edges = makeSeg(1, 2, workX, workZ, endX, workH, workR, False, False, len(edges))

    elif shapeT == 6:
        verts, edges = makeSeg(5, 6, workX, workZ, endX, workH, workR, False, segL=len(edges))

    elif shapeT == 7:

        workH = shapeZ/2
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

    elif shapeT == 8:

        workH = shapeZ/4
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR/2
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(1, 2, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

    elif shapeT == 9:

        workH = shapeZ/8
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        workH = shapeZ/4
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        workH = shapeZ/8
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # connector edge.
        verts1, edges1 = makeSeg(1, 2, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

    elif shapeT == 10:

        workH = shapeZ/8
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR/2
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(0, 0, workX, workZ, endX, workH, workR, False, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR/2
        workZ += workH
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        workH = (startZ+shapeZ)-workZ # remaining height.
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(3, 6, workX, workZ, endX, workH, workR, True, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

    elif shapeT == 11:

        workH = shapeZ/8
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workR = shapeR
        workZ += workH
        workH = shapeZ/4
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(4, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH
        workH = shapeZ/8
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(2, 6, workX, workZ, endX, workH, workR, segL=len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

        workZ += workH # next segment veritcal origin.
        workH = (startZ+shapeZ)-workZ # set final height to fill allocated space.
        edges.append([len(edges), len(edges)+1]) # add connector edge...
        verts1, edges1 = makeSeg(3, 6, workX, workZ, endX, workH, workR, True, False, len(edges))
        verts.extend(verts1)
        edges.extend(edges1)

    else: # default: shapeT not recognized - straight side, full height.
        verts, edges = makeSeg(0, 0, workX, workZ, endX, workH, workR)

    return verts,edges


################################################################################
#
# @todo: Round top and bottom of flutes.
# @todo: handle odd number of sides (flat in middle).
#
def add_col_flute(fAngle, fTarg, fBase, fXorg, fluteAd, fSides=2):
    '''
   Create "flutes" for column.

    Parameters:
        fAngle  starting point of flute on column face.
        fTarg   angle offset of flute end point for column face.
        fBase   vertical position for vertices.
        fXorg   column face radius, negative for flute extrusions.
        fluteAd flute "depth" offset from radius
        fSides  number of faces for flute

    Returns:
        newpoints - a list of coordinates for flute points (list of tuples), [[x,y,z],[x,y,z],...n]
    '''
    newpoints = []

    if fSides < 2: fSides = 2 # min number of sides.

    halfSides = fSides/2 # common value efficiency variable.

    stepD = fluteAd/halfSides # in and out depth variation per side.

    divSides = 0
    curStep = 1

    while curStep <= halfSides:
        divSides += curStep*curStep
        curStep+=1

    stepCurve = fTarg/(divSides*2) # logorithmic delta along radius for sides.

    curStep = 0
    tAngle = fAngle

    # curvature in
    while curStep < halfSides:
        tAngle = tAngle + (curStep*curStep*stepCurve)
        x1 = (fXorg - (stepD * (curStep+1))) * cos(tAngle)
        y1 = (fXorg - (stepD * (curStep+1))) * sin(tAngle)
        newpoints.append([x1, y1, fBase])
        curStep+=1

    # curvature out - includes mid-point, and end-point...
    while curStep:
        tAngle = tAngle + (curStep*curStep*stepCurve)
        x1 = (fXorg - (stepD * curStep)) * cos(tAngle)
        y1 = (fXorg - (stepD * curStep)) * sin(tAngle)
        newpoints.append([x1, y1, fBase])
        curStep-=1

    return newpoints


################################################################################
#
def add_column(colBase, colWide, taper, c_faces, colRows, colRowH, fluteCt, fluteAd, fluteFs, colSkew):
    '''
    Create column geometry.

    Params:
	colBase   starting zPos for column (put on top of base and plinth).
	colWide   width of the column, negative for flute extrusions.
	taper     width reduction per row to taper column.
	c_faces   surfaces (faces) on column per quadrant, 1 = square, increase to smooth, max 360.
	colRows   number of rows/vertical blocks for column. Use +1 to complete row (2 is working min).
	colRowH   height of column row.
	fluteCt   flute count, make curfs, gouges, gear like indents.
	fluteAd   Addendum, extent of flute from column face/radius.
        fluteFs   number of "sides" (faces) for flute.
	colSkew   twist column, negative for "clock-wise" twist.

    Returns:
	list of vertices and faces
    '''
    if fluteCt: # set working faces and modulo/flag for doing flutes...
        c_faces -= c_faces % fluteCt
        fluteFaces = c_faces / fluteCt
    else:
        fluteFaces = 0

    tFaces = 2 * pi / c_faces # c_faces == 1 makes a square

    verts = []
    faces = []

    edgeloop_prev = []

    for curRow in range(colRows):
        edgeloop = []

        for faceCnt in range(c_faces):
            fAngle = faceCnt * tFaces

            rSkew = curRow * colSkew
            curZ = colBase + (curRow*colRowH)

            if fluteFaces and not faceCnt % fluteFaces: # making "flutes", and due a flute?
                verts1 = add_col_flute(fAngle + rSkew, tFaces, curZ, colWide, fluteAd, fluteFs)

            else: # column surface for section...
                targStep = tFaces/4
                vAngle = fAngle + rSkew

                # create list of coordinates for column face points (list of four tuples), [[x,y,z],[x,y,z],...4]
                verts1 = [(colWide * cos(vAngle+(targStep*I)), colWide * sin(vAngle+(targStep*I)), curZ) for I in range(4)]

# track down list(range(listStart,listEnd))...
            edgeloop.extend(list(range(len(verts), len(verts) + len(verts1))))
            verts.extend(verts1)

        # Create faces between rings/rows.
        if edgeloop_prev:
            faces.extend(createFaces(edgeloop, edgeloop_prev))
        edgeloop_prev = edgeloop # Track ring/row vertices for next iteration.

        # apply taper to rows.
        if colWide > 0: 
            colWide -= taper # decrease radius
        else:
            colWide += taper # will decrease neg radius

    return verts, faces


################################################################################
#
def create_columnObj(self,context):
    # validate UI setting limits, individual and relative to other parameters.

    # Radius can't be 0.00
    if self.properties.col_radius == 0:
        self.properties.col_radius = 0.01 # Reset UI if input out of bounds...

    # Flutes can't exceed faces
    if self.properties.col_flutes > self.properties.col_faces:
        self.properties.col_flutes = self.properties.col_faces # Reset UI if input out of bounds...

    colWidth = self.properties.col_radius
    colTubeH = self.row_height * self.col_blocks
    checkFlutes = 0

    if colWidth < 0:
        checkRadius = -colWidth

        if self.col_flutes:
            checkFlutes = self.addendum # negative adjustment for extrusions.
    else:
        checkRadius = colWidth

    # Taper can't exceed radius
    if self.properties.col_taper > checkRadius:
        self.properties.col_taper = checkRadius # Reset UI if input out of bounds...

    plinthH = 0.00
    vertsPlinth = []
    edgesPlinth = []

    baseH = 0.00
    vertsBase = []
    edgesBase = []

    capH = 0.00
    vertsCap = []
    edgesCap = []

    finaleH = 0.00
    vertsFinale = []
    edgesFinale = []

    # Start at bottom...

    if self.col_plinth: # making a sub-base/platform.
        plinthH = self.plinth_height

        # Create simple platform
        vertsPlinth, edgesPlinth = makeSeg(0, 0, 0, 0, 0, plinthH, self.plinth_width, False, False)

    if self.col_base: # making a base.
        baseH = self.base_height
        baseM = checkRadius + checkFlutes # match column with extruded flutes.

        # Create column base, type used to modify "style".
        vertsBase, edgesBase = add_extent_base(
            0.0,
            0.0,
            baseH,
            self.base_width,
            plinthH,
            baseM,
            self.base_type
            )

    if self.col_cap: # making a capital
        capH = self.cap_height
# need to check for "zero" and set minimum width? naw, blame it on the user...
        capM = checkRadius + checkFlutes - self.properties.col_taper # same as base with taper.

        # Create column capital, type used to modify "style".
        vertsCap, edgesCap = add_extent_capital(
            0.0,
            0.0,
            capH,
            self.cap_width - self.properties.col_taper, # size to top of column
            baseH + plinthH + colTubeH,
            capM,
            self.cap_type,
            )

    if self.col_finale: # making top/cover of column.
        finaleH = self.finale_height # needed to calculate accumulative column height.

        # Create simple cover
        vertsFinale, edgesFinale = makeSeg(0, 0, 0, baseH + plinthH + capH + colTubeH, 0,
            finaleH, self.finale_width - self.properties.col_taper)

    # finish top.

    # Stage all operators....

    verts, faces = add_column(
        baseH + plinthH,
        colWidth,
        self.col_taper/self.col_blocks, # taper column per number of rows.
        self.col_faces, # "faces" on column, per quadrant, 1 = square.
        self.col_blocks + 1, # need extra to complete row.
        self.row_height,
        self.col_flutes,
        self.addendum,
        self.flute_sides,
        radians(self.skew)
        )

    scene = context.scene

    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')

    if self.col_plinth: # platform (sub-base).
        obj_360("Plinth", vertsPlinth, edgesPlinth, scene)

    if self.col_base: # decorative base.
        obj_360("Base", vertsBase, edgesBase, scene, self.base_faces*4)

    if self.col_cap: # decorative top.
        obj_360("Capital", vertsCap, edgesCap, scene, self.cap_faces*4)

    if self.col_finale: # structural "cover".
        obj_360("Finale", vertsFinale, edgesFinale, scene)

    # this is where the rubber meets the road... ;)

    mesh = bpy.data.meshes.new("Column")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(uMatRGBSet('Col_mat',self.cMatRGB,matMod=True))

    mesh.update()

    ob_new = bpy.data.objects.new("Column", mesh)
    scene.objects.link(ob_new)
    scene.objects.active = ob_new
    ob_new.select = True

    if self.col_base or self.col_cap or self.col_plinth or self.col_finale:
        bpy.ops.object.join()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.editmode_toggle()

    ob_new.location = tuple(context.scene.cursor_location)


################################################################################
#
# Add a column object.
#
#    UI functions and object creation.
#
class AddColumn(bpy.types.Operator):

    bl_idname = "mesh.add_column"
    bl_label = "Add Column"
    bl_options = {'REGISTER', 'UNDO'}

    Style = EnumProperty(items=(
        ('0',"Default",""),
        ("1","Tuscan","")
        ),
        name="Style",description="Column style.")

    curStyle=Style

    cMatRGB=FloatVectorProperty(min=0,max=1,default=(0.5,0.5,0.5),subtype='COLOR',size=3)


    col_radius = FloatProperty(name="Radius",
        description="Radius of the column; use negative to extrude flutes.",
        min=-100.0,
        max=100.0,
        default=0.4)
    col_taper = FloatProperty(name="Taper",
        description="Radius reduction for taper - cannot exceed radius.",
        min=0.00,
        max=10.0,
        default=0.10)
    col_faces = IntProperty(name="Faces",
        description="Number of faces per quadrant, 1 = square.",
        min=1,
        max=360,
        default=20)
    col_blocks = IntProperty(name="Rows",
        description="Number of blocks in the column",
        min=1,
        max=100,
        default=4)
    row_height = FloatProperty(name="Row Height",
        description="Height of each block row",
        min=0.10,
        max=100.0,
        default=0.25)
    skew = FloatProperty(name="Skew",
        description="Twist the column (degrees) - neg for right twist.",
        min=-180,
        max=180,
        default=0.00)


    col_flutes = IntProperty(name="Flutes",
        description="Channels on column",
        min=0,
        max=100,
        default=0)
    addendum = FloatProperty(name="Addendum",
        description="flute (depth) offset from radius.",
        min=0.01,
        max=100.0,
        default=0.1)
    flute_sides = IntProperty(name="Sides",
        description="facets for flute",
        min=2,
        max=100,
        default=12)


    col_plinth = BoolProperty(name="Plinth",
        description="sub-base of column.",
         default = False)
    plinth_height = FloatProperty(name="Height",
        description="Height of sub-base",
        min=0.10,
        max=10.0,
        default=0.10)
    plinth_width = FloatProperty(name="Width",
        description="Width of sub-base/platform (radius)",
        min=0.10,
        max=10.0,
        default=0.6)


    col_base = BoolProperty(name="Base",
         description="Column base",
         default = True)
    base_type = IntProperty(name="Type",
        description="Type of base to generate.",
        min=1,
        max=20,
        default=1)
    base_faces = IntProperty(name="Faces",
        description="Number of faces per quadrant; 1 = square.",
        min=1,
        max=360,
        default=5)
    base_height = FloatProperty(name="Height",
        description="Height of base",
        min=0.10,
        max=10.0,
        default=0.25)
    base_width = FloatProperty(name="Width",
        description="Width of base (radius)",
        min=0.10,
        max=10.0,
        default=0.4)


    col_cap = BoolProperty(name="Capital",
         description="Column capital",
         default = True)
    cap_type = IntProperty(name="Type",
        description="Type of capital to generate.",
        min=1,
        max=20,
        default=1)
    cap_faces = IntProperty(name="Faces",
        description="Number of faces per quadrant, 1 = square.",
        min=1,
        max=360,
        default=5)
    cap_height = FloatProperty(name="Height",
        description="Height of capital",
        min=0.10,
        max=10.0,
        default=0.25)
    cap_width = FloatProperty(name="Width",
        description="Width of capital (radius)",
        min=0.10,
        max=10.0,
        default=0.4)


    col_finale = BoolProperty(name="Finale",
        description="cover of column.",
         default = False)
    finale_height = FloatProperty(name="Height",
        description="Height of column cover",
        min=0.10,
        max=10.0,
        default=0.10)
    finale_width = FloatProperty(name="Width",
        description="Width of cover (radius)",
        min=0.10,
        max=10.0,
        default=0.6)


    def draw(self, context):
        layout = self.layout

        layout.prop(self,'Style')

        box=layout.box()
        box.prop(self,'cMatRGB',text='Color')

#        box = layout.box()
#        box.label(text='Column Sizing')
        box.prop(self, 'col_radius')
        box.prop(self, 'col_taper')
        box.prop(self, 'col_faces')
        box.prop(self, 'col_blocks')
        box.prop(self, 'row_height')
        box.prop(self, 'skew')

	#modifier to primary
        box = layout.box()
        box.prop(self, 'col_flutes')
        if self.properties.col_flutes:
            box.prop(self, 'addendum')
            box.prop(self, 'flute_sides')

	#sub-base object - works as simple base too.
        box = layout.box()
        box.prop(self, 'col_plinth')
	# add faces/steps for plinth
        if self.properties.col_plinth:
            box.prop(self, 'plinth_height')
            box.prop(self, 'plinth_width')

	#base object
        box = layout.box()
        box.prop(self, 'col_base')
        if self.properties.col_base:
            box.prop(self, 'base_type')
            box.prop(self, 'base_faces')
            box.prop(self, 'base_height')
            box.prop(self, 'base_width')

	#top object
        box = layout.box()
        box.prop(self, 'col_cap')
        if self.properties.col_cap:
            box.prop(self, 'cap_type')
            box.prop(self, 'cap_faces')
            box.prop(self, 'cap_height')
            box.prop(self, 'cap_width')

	#cover object
        box = layout.box()
        box.prop(self, 'col_finale')
	# add faces/steps for finale
        if self.properties.col_finale:
            box.prop(self, 'finale_height')
            box.prop(self, 'finale_width')

    ##########-##########-##########-##########

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            # set style, "new" or first use.
            if self.curStyle!=self.Style:
                ColumnStyles(self,self.Style)
                self.curStyle=self.Style

            create_columnObj(self,context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'},"Option only valid in Object mode")
            return {'CANCELLED'}
