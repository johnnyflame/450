################################################################################
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License.
# See http://www.gnu.org/licenses/ for more details.
#
# ***** END GPL LICENSE BLOCK *****
'''
Generate a "block wall", suitable for many uses, typically a "castle style".
'''
# @todo: perform color change without rebuild.
# @todo: prevent opening overlap.
# @todo: "Merge" more blocks.
# @todo: review defaults and limits for all UI entries.
# @todo: Add "reset" button to restore defaults - see "style" for other scripts.
# @todo: replace globals with parameters
#
# Wish list:
#  Block styles: "Rocks" (add_mesh_rocks), "Balls" (add_mesh_clusters), hexagon.
#  Stair Builder, Balcony, Door, and other script/object integration.
#
################################################################################

import bpy
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty
from add_mesh_building_basics.UtilMats import uMatRGBSet
from random import random

import math
from math import pi, fmod, sqrt, sin, cos, atan


################################################################################

# constants
BLOCK_MIN=0.10 # Minimum block sizing; also used for openings.
ROW_H_WEIGHT=0.5 # Use 0.5, else create parameter: 0=no effect, 1=1:1 relationship, negative values allowed

# gap 0 makes solid wall but affects other options (like openings), not in a good way.
# Negative gap creates "phantom blocks" inside the edges.
GAP_MIN=0.01 # minimum space between blocks.


# globals - need review and revision... preferably removal.

# General wall Settings
settings = {'w': 1.2, 'wv': 0.3, 'h': .6, 'hv': 0.3, 'd': 0.3, 'dv': 0.1,
            'g': 0.1, 'sdv': 0.1,
            'hm':BLOCK_MIN, 'eoff':0.3,
            'Round':False, 'Curve':False }
# 'w':width 'wv':widthVariation
# 'h':height 'hv':heightVariation
# 'd':depth 'dv':depthVariation
# 'g':grout
# 'sdv':subdivision(distance or angle)
# 'hm':height minimum
#no width min? 'wm':width minimum
# 'eoff':edge offset
# 'Round': round/radial wall shape
# 'Curve': curve (slope) wall, makes dome if "Round"

# dims = area of wall (centered/splitX from 3D cursor); modified for radial.
dims = {'s':-10, 'e':10, 't':15}
#dims = {'s':0, 'e':pi*3/2, 't':12.3} # radial
# 's' start, 'e' end, 't' top

# Holes in wall for various apertures.
#openingSpecs = []
openingSpecs = [{'w':0.5, 'h':0.5, 'x':0.8, 'z':2.7, 'rp':1, 'bvl':0.0,
                 'v':0, 'vl':0, 't':0, 'tl':0}]
# 'w': opening width, 'h': opening height,
# 'x': horizontal position, 'z': vertical position,
# 'rp': repeat opening with a spacing of x,
# 'bvl': bevel the inside of the opening,
# 'v': height of the top arch, 'vl':height of the bottom arch,
# 't': thickness of the top arch, 'tl': thickness of the bottom arch

############################
#
# Psuedo macros:
#
# random values (in specific range).
    # random value +-0.5
def rndc(): return (random() - 0.5)

    # random value +-1
def rndd(): return rndc()*2

# line/circle intercepts
# offs = distance perpendicular to the line to the center
# r=radius
# return the distance paralell to the line to the center of the circle at the intercept.
def circ(offs=0,r=1):
    absOffs = abs(offs)
    if absOffs > r: return None
    elif absOffs == r: return 0.
    else: return sqrt(r**2 - absOffs**2)

# bevel blocks.
# pointsToAffect are: left=(4,6), right=(0,2)
def bevelBlockOffsets(offsets,bevel,pointsToAffect):
    for num in pointsToAffect:
        offsets[num] = offsets[num][:]
        offsets[num][0] += bevel

################################################################################


################################################################################
#
#  UI functions and object creation.
#
class add_Blockwall(bpy.types.Operator):
    bl_idname="mesh.add_wall"
    bl_label="Block wall"
    bl_description="Block wall"
    bl_options = {'REGISTER', 'UNDO'}

    wallRGB=FloatVectorProperty(min=0,max=1,default=(0.5,0.5,0.5),subtype='COLOR',size=3)


# @todo: Add "flat" selection for disk, else radial makes a tower (normal).
    # make the wall circular - if not curved it's a flat disc
    # Radiating from one point - round/disc; instead of square
    wallCirc=BoolProperty(default=False,description="Make wall circular")
    # curve the wall - if radial creates dome.
    # Warp/slope; curved over like a vaulted tunnel
    wallCurve=BoolProperty(default=False,description="Curve wall")

    # wall area/size
    wallX=FloatProperty(name="Width",min=1,max=100,default=20)
    wallZ=FloatProperty(name="Height",min=1,max=100,default=15)
    EdgeOffset=FloatProperty(name="Edging",min=0.0,max=100,default=0.6,description="stagger wall sides")

    # block sizing
    blockX=FloatProperty(name="Width",min=BLOCK_MIN,max=100.0,default=1.5)
    WidthVar=FloatProperty(name="Variance",min=0.0,max=100.0,default=0.5,description="Randomize")
# no width minimum?
    blockZ=FloatProperty(name="Height",min=BLOCK_MIN,max=100.0,default=0.7)
    HeightVar=FloatProperty(name="Variance",min=0.0,max=100.0,default=0.3,description="Randomize")
    HeightMin=FloatProperty(name="Minimum",min=BLOCK_MIN,max=100.0,default=0.25,description="Minimum block Height with variance")
    Depth=FloatProperty(name="Depth",min=BLOCK_MIN,max=100.0,default=1)
# allow 0 for test cases...
#    Depth=FloatProperty(name="Depth",min=0,max=100.0,default=1)
    DepthVar=FloatProperty(name="Variance",min=0.0,max=100.0,default=0,description="Randomize")
    DepthMinimum = FloatProperty(name="Minimum",min=BLOCK_MIN,max=100.0,default=1.0,description="minimum block Depth with variance")
    MergeBlock = BoolProperty(name="Merge",default=False,description="merge closely adjoining blocks")

    # block spacing
    Grout=FloatProperty(name="Gap",min=GAP_MIN,max=10,default=0.1,description="Block separation")

    # portals, windows or doors, holes/openings in wall... affects block row size.
    wallPort=BoolProperty(name="Portal",default=True,description="Door/window opening")
    portW=FloatProperty(name="Width",min=BLOCK_MIN,max=100,default=2.5)
    portH=FloatProperty(name="Height",min=BLOCK_MIN,max=100,default=3.5)
    portL=FloatProperty(name="Indent",min=0,max=100,default=5,description="The x position")
# fix opening base so 0 can be default...
    portB=FloatProperty(name="Bottom",min=0,max=100,default=1,description="opening base location")
    portBevel=FloatProperty(name="Bevel",min=-10,max=10,default=0.25,description="Angle block face")
    portRpt=BoolProperty(default=False,description="make multiple openings")
    portArchT=BoolProperty(name="Arch Top",default=True)
    portArchTC=FloatProperty(name="Curve",min=0.01,max=100,default=2.5,description="Arch curve height")
    portArchTT=FloatProperty(name="Thickness",min=0.001,max=100,default=0.75)
    portArchB=BoolProperty(name="Arch Base",default=False)
    portArchBC=FloatProperty(name="Curve",min=0.01,max=100,default=2.5,description="Arch curve height")
    portArchBT=FloatProperty(name="Thickness",min=0.01,max=100,default=0.75)

    # narrow openings in wall - classical arrow/rifle ports.
#need to prevent overlap with arch openings - though inversion is an interesting effect.
    SlotV=BoolProperty(name="Vertical",default=True)
    SlotVW=FloatProperty(name="Width",min=BLOCK_MIN,max=100.0,default=0.5)
    SlotVH=FloatProperty(name="Height",min=BLOCK_MIN,max=100.0,default=3.5)
    SlotVL=FloatProperty(name="Indent",min=-100,max=100.0,default=0,description="The x position or spacing")
    SlotVZ=FloatProperty(name="Bottom",min=-100,max=100.0,default=4.00)
    slotVArchT=BoolProperty(name="Top",default=True)
    slotVArchB=BoolProperty(name="Bottom",default=True)
    SlotVRpt = BoolProperty(name="Repeat",default=False)

    SlotH=BoolProperty(name="Horizontal",default=True)
    SlotHW=FloatProperty(name="Width",min=BLOCK_MIN,max=100.0,default=2.5)
    SlotHH=FloatProperty(name="Height",min=BLOCK_MIN,max=100.0,default=3.5)
    SlotHL=FloatProperty(name="Indent",min=-100,max=100.0,default=-7.0,description="The x position or spacing")
    SlotHZ=FloatProperty(name="Bottom",min=-100,max=100.0,default=5.50)
    SlotHBvl=FloatProperty(name="Bevel",min=-10,max=10,default=0.25,description="Angle block face")
    slotHArchT=BoolProperty(name="Top",default=False)
    slotHArchB=BoolProperty(name="Bottom",default=False)
    SlotHRpt = BoolProperty(name="Repeat",default=False)

    # "gaps" on top of wall.
    CrenelTog=BoolProperty(name="Crenels",default=True,description="Make openings along top of wall")
# review and determine min for % - should allow less...
    CrenelXP=FloatProperty(name="Width %",min=0.10,max=1.0,default=0.15)
    CrenelZP=FloatProperty(name="Height %",min=0.10,max=1.0,default=0.10)


    # shelf location and size.
# see "balcony" options for improved capabilities.
    wallShelf=BoolProperty(name="Shelf",default=True)
# should limit x and z to wall boundaries
    ShelfX=FloatProperty(name="Left",min=-100,max=100.0,default=0,description="x origin")
    ShelfZ=FloatProperty(name="Base",min=-100,max=100.0,default=12.0,description="z origin")
    ShelfW=FloatProperty(name="Width",min=BLOCK_MIN,max=100.0,default=10,description="The Width of shelf area")
# height seems to be double, check usage
    ShelfH=FloatProperty(name="Height",min=BLOCK_MIN,max=100.0,default=0.5,description="The Height of Shelf area")
    ShelfD = FloatProperty(name="Depth",min=BLOCK_MIN,max=100.0,default=2,description="Depth of shelf")
    ShelfBack=BoolProperty(name="Back",default=False)

    # steps
    wallSteps=BoolProperty(name="Steps",default=True)
    StepX=FloatProperty(name="Left",min=-100,max=100,default=-10,description="x origin")
    StepZ=FloatProperty(name="Base",min=-100,max=100,default=0,description="z origin")
    StepW=FloatProperty(name="Width",min=BLOCK_MIN,max=100.0,default=15,description="Width of step area")
    StepH=FloatProperty(name="Height",min=BLOCK_MIN,max=100.0,default=15,description="Height of step area")
    StepD=FloatProperty(name="Depth",min=BLOCK_MIN,max=100.0,default=3,description="Depth of steps")
    StepV=FloatProperty(name="Riser",min=BLOCK_MIN,max=100.0,default=0.70,description="Height of steps")
    StepT=FloatProperty(name="Tread",min=BLOCK_MIN,max=100.0,default=1.0,description="Width of steps")
    StepLeft=BoolProperty(name="Left",default=False,description="Up to left.")
    StepBlocks=BoolProperty(name="Blocks",default=False,description="Supporting blocks")
    StepBack=BoolProperty(name="Back",default=False,description="Backside of wall")

##
##
#####
# Show the UI - present properties to user.
#####
##
##
    # Display the toolbox options
    def draw(self, context):

        layout = self.layout

        box=layout.box()
        box.prop(self,'wallRGB',text='Color')

        # Wall area (size/position)
#        box.label(text='Wall Size (area)')
        box.prop(self,'wallX')
        box.prop(self,'wallZ')
        box.prop(self,'EdgeOffset')

        # Wall shape modifiers
        row=box.row()
        row.prop(self,'wallCirc',text='Round')
        row.prop(self,'wallCurve',text='Curve')

        # Wall block sizing
        row=box.row()
        row.label(text='Blocks')
        row.prop(self,'MergeBlock')
        box.prop(self,'Grout')
#add checkbox for "fixed" sizing (ignore variance) a.k.a. bricks.
        box.prop(self,'blockX')
        box.prop(self, 'WidthVar')
        box.prop(self,'blockZ')
        box.prop(self, 'HeightVar')
        box.prop(self, 'HeightMin')
        box.prop(self, 'Depth')
        box.prop(self, 'DepthVar')
        box.prop(self, 'DepthMinimum')

        # Openings (doors, windows; arched)
        box = layout.box()
        row=box.row()
        row.prop(self,'wallPort')
        if self.properties.wallPort:
            row.prop(self,'portRpt',text='Dupe')
            box.prop(self, 'portW')
            box.prop(self, 'portH')
            box.prop(self, 'portL')
            box.prop(self, 'portB')
            box.prop(self, 'portBevel')

            box.prop(self,'portArchT')
            if self.portArchT:
                box.prop(self, 'portArchTC')
                box.prop(self, 'portArchTT')

            box.prop(self,'portArchB')
            if self.portArchB:
                box.prop(self, 'portArchBC')
                box.prop(self, 'portArchBT')

        box = layout.box()
        row=box.row()
        row.prop(self,'SlotV',text='Slot')
        if self.properties.SlotV:
            row.prop(self,'SlotVRpt',text='Dupe')
            box.prop(self,'SlotVL')
            box.prop(self,'SlotVW')
            box.prop(self,'SlotVH')
            box.prop(self,'SlotVZ')
            box.label(text='Arch')
            row=box.row()
            row.prop(self,'slotVArchT')
            row.prop(self,'slotVArchB')

        box = layout.box()
        row=box.row()
        row.prop(self,'SlotH',text='Window')
        if self.properties.SlotH:
            row.prop(self,'SlotHRpt',text='Dupe')
            box.prop(self,'SlotHW')
            box.prop(self,'SlotHH')
            box.prop(self,'SlotHL')
            box.prop(self,'SlotHZ')
            box.prop(self,'SlotHBvl')
            box.label(text='Arch')
            row=box.row()
            row.prop(self,'slotHArchT')
            row.prop(self,'slotHArchB')

        # Crenels, gaps in top of wall
        box = layout.box()
        box.prop(self, 'CrenelTog')
        if self.properties.CrenelTog:
            box.prop(self, 'CrenelXP')
            box.prop(self, 'CrenelZP')

        # Shelfing
        box = layout.box()
        row=box.row()
        row.prop(self,'wallShelf')
        if self.properties.wallShelf:
            row.prop(self,'ShelfBack')
            box.prop(self,'ShelfX')
            box.prop(self,'ShelfZ')
            box.prop(self,'ShelfW')
            box.prop(self,'ShelfH')
            box.prop(self,'ShelfD')

        # Steps
        box = layout.box()
        row=box.row()
        row.prop(self,'wallSteps')
        if self.properties.wallSteps:
            row.prop(self,'StepLeft')

            row=box.row()
            row.prop(self,'StepBlocks')
            row.prop(self,'StepBack')

            box.prop(self, 'StepX')
            box.prop(self, 'StepZ')
            box.prop(self, 'StepW')
            box.prop(self, 'StepH')
            box.prop(self, 'StepD')
            box.prop(self, 'StepV')
            box.prop(self, 'StepT')
##
#####
# Respond to UI - process the properties set by user.
    # Check and process UI settings to generate wall.
#####
##
    def execute(self, context):

        global openingSpecs

        # set a few working variables
        halfWallW=self.properties.wallX/2
        blockHeight=self.properties.blockZ

        # Limit UI settings relative to other parameters.

        # min height cannot exceed block height
        if self.properties.HeightMin > blockHeight:
            self.properties.HeightMin=blockHeight

        blockHmin=self.properties.HeightMin

        # gap cannot reduce block below minimum - does not account for variance.
# may want to use /2 here... but, who's going to notice?
        if blockHeight-self.properties.Grout < blockHmin:
            self.properties.Grout=blockHeight-blockHmin

        # needed for rowprocessing() to center wall...
        dims['s'] = -halfWallW
        dims['e'] = halfWallW

        dims['t'] = self.properties.wallZ

        settings['eoff'] = self.properties.EdgeOffset

        # block sizing
        settings['w'] = self.properties.blockX
        settings['wv'] = self.properties.WidthVar

        if self.properties.wallCirc:
# eliminate to allow user control for start/completion by width setting.
            dims['s'] = 0.0 # complete radial
            if dims['e'] > pi*2: dims['e'] = pi*2 # max end for circle
            settings['sdv'] = 0.12
        else:
            settings['sdv'] = settings['w'] 

        settings['h']=blockHeight
        settings['hm']=blockHmin

        settings['d'] = self.properties.Depth
        settings['dv'] = self.properties.DepthVar

        settings['g'] = self.properties.Grout

        settings['Round']=self.properties.wallCirc
        settings['Curve']=self.properties.wallCurve

#when openings overlap they create inverse stonework - interesting but not the desired effect
#if opening width == indent*2 the edge blocks fail (row of blocks cross opening) - bug.
        openingSpecs = []
        openingIdx = 0 # track opening array references for multiple uses

        if self.properties.wallPort: # Door/window opening
            # set defaults...
            openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.8, 'z':2.7, 'rp':1, 'bvl':0, 'v':0, 'vl':0, 't':0, 'tl':0}]

            openingSpecs[openingIdx]['w'] = self.properties.portW
            openingSpecs[openingIdx]['h'] = self.properties.portH
            openingSpecs[openingIdx]['x'] = self.properties.portL
            openingSpecs[openingIdx]['z'] = self.properties.portB
            openingSpecs[openingIdx]['rp'] = self.properties.portRpt

            if self.properties.portArchT:
                openingSpecs[openingIdx]['v'] = self.properties.portArchTC
                openingSpecs[openingIdx]['t'] = self.properties.portArchTT

            if self.properties.portArchB:
                openingSpecs[openingIdx]['vl'] = self.properties.portArchBC
                openingSpecs[openingIdx]['tl'] = self.properties.portArchBT
            
            openingSpecs[openingIdx]['bvl'] = self.properties.portBevel

            openingIdx += 1 # count window/door/arch opening

        if self.properties.SlotV: # vertical slots
            # create with defaults...
            openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.0, 'z':2.7, 'rp':0, 'bvl':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]

            # set opening using input parameters
            openingSpecs[openingIdx]['w'] = self.properties.SlotVW
            openingSpecs[openingIdx]['h'] = self.properties.SlotVH
            openingSpecs[openingIdx]['x'] = self.properties.SlotVL
            openingSpecs[openingIdx]['z'] = self.properties.SlotVZ
            openingSpecs[openingIdx]['rp'] = self.properties.SlotVRpt

            if self.properties.slotVArchT:
                openingSpecs[openingIdx]['v'] = self.properties.SlotVW
                openingSpecs[openingIdx]['t'] = self.properties.SlotVW/2
            if self.properties.slotVArchB:
                openingSpecs[openingIdx]['vl'] = self.properties.SlotVW
                openingSpecs[openingIdx]['tl'] = self.properties.SlotVW/2

            openingIdx += 1 # count vertical slot opening

        if self.properties.SlotH: # Horizontal slots
            # create with defaults...
            openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.0, 'z':2.7, 'rp':0, 'bvl':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]

            # set opening using input parameters
            openingSpecs[openingIdx]['w'] = self.properties.SlotHW
            openingSpecs[openingIdx]['h'] = self.properties.SlotHH
            openingSpecs[openingIdx]['x'] = self.properties.SlotHL
            openingSpecs[openingIdx]['z'] = self.properties.SlotHZ
#horizontal repeat isn't same spacing as vertical...
            openingSpecs[openingIdx]['rp'] = self.properties.SlotHRpt

# want arc to go sideways too... maybe wedge will be sufficient and can skip horiz arcs.
            openingSpecs[openingIdx]['bvl'] = self.properties.SlotHBvl

            if self.properties.slotHArchT:
                openingSpecs[openingIdx]['v'] = self.properties.SlotHW/2
                openingSpecs[openingIdx]['t'] = self.properties.SlotHW/4
            if self.properties.slotHArchB:
                openingSpecs[openingIdx]['vl'] = self.properties.SlotHW/2
                openingSpecs[openingIdx]['tl'] = self.properties.SlotHW/4

            openingIdx += 1 # count horizontal slot opening

        # Crenellations (top row openings)
        if self.properties.CrenelTog:
# add bottom arch option?
# if crenel opening overlaps with arch opening it fills with blocks...

            # set defaults...
            openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.0, 'z':2.7, 'rp':1, 'bvl':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]

            wallw=self.properties.wallX
            crenelW = wallw*self.properties.CrenelXP # Width % opening.

            crenelH = self.properties.wallZ*self.properties.CrenelZP # % proportional height.

            openingSpecs[openingIdx]['w'] = crenelW
            openingSpecs[openingIdx]['h'] = crenelH
            openingSpecs[openingIdx]['x'] = crenelW*2-1 # assume standard spacing

            if not self.properties.wallCirc: # normal wall?
                # set indent 0 (center) if opening is 50% or more of wall width, no repeat.
                if crenelW*2 >= wallw:
                    openingSpecs[openingIdx]['x'] = 0
                    openingSpecs[openingIdx]['rp'] = 0

            openingSpecs[openingIdx]['z'] = self.properties.wallZ - (crenelH/2) # set bottom of opening

            openingIdx += 1 # count crenel openings

#########################################
        #
        # Process the user settings to generate a wall
        #
#########################################

        holeList=openList()
        wallVs,wallFs = wallBuild(self,wallPlan(self,holeList),holeList)

        wallMesh=bpy.data.meshes.new("Wall")
        wallMesh.from_pydata(wallVs,[],wallFs)

        scene = context.scene

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        wallMesh.update()

        ob_new = bpy.data.objects.new("Wall",wallMesh)
        scene.objects.link(ob_new)
        scene.objects.active = ob_new
        ob_new.select = True

        ob_new.data.materials.append(uMatRGBSet("Wall_mat",self.wallRGB,matMod=True))

        ob_new.location = tuple(context.scene.cursor_location)
        ob_new.rotation_quaternion = [1.0,0.0,0.0,0.0]

        return {'FINISHED'}


################
##
#################
##
######################## Blocks module/script inclusion - to be reduced significantly.
##
#######################
##

##
#
# Module notes:
#
# consider removing wedge crit for small "c" and "cl" values
# wrap around for openings on radial stonework?
# repeat for opening doesn't distribute evenly when radialized
#  - see wrap around note above.
# if opening width == indent*2 the edge blocks fail (row of blocks cross opening).
# if block width variance is 0, and edging is on, right edge blocks create a "vertical seam".
#
##


################################################################################
#
# create a list of openings from the general specifications.
#
def openList():
    boundlist = []

    # initialize variables
#overkill? no, first step to eliminating "globals", and, hope to improve performance.
    areaStart=dims['s']
    areaEnd=dims['e']

    SetWid = settings['w']
    wallCirc=settings['Round']

    for x in openingSpecs:
        # hope this is faster... at least for repeat.
        xOpenW=x['w']
        xOpenX=x['x']
        xOpenZ=x['z']

        if x['rp']:
            if wallCirc: r1 = xOpenZ
            else: r1 = 1

            if xOpenX > (xOpenW + SetWid): spacing = xOpenX/r1
            else: spacing = (xOpenW + SetWid)/r1

            minspacing = (xOpenW + SetWid)/r1

            divs = fill(areaStart,areaEnd,spacing,minspacing,center=1)

            for posidx in range(len(divs)-2):
                boundlist.append(opening(divs[posidx+1],xOpenZ,xOpenW,x['h'],x['v'],x['t'],x['vl'],x['tl'],x['bvl']))

        else: boundlist.append(opening(xOpenX,xOpenZ,xOpenW,x['h'],x['v'],x['t'],x['vl'],x['tl'],x['bvl']))
        #check for overlaping edges?

    return boundlist


################################################################################
#
# Build the wall, based on rows, "holeList", and parameters;
#     geometry for the blocks, arches, steps, platforms...
#
# Return: verts and faces for wall object.
#
# @todo: replace "settings['var']" with "sRef.properties.var" (eliminate globals).
#
def wallBuild(sRef,rows,holeList):

    wallVs=[]
    wallFs=[]

    AllBlocks = []

    # create local references for anything that's used more than once...

    wallTop=dims['t']
    wallTop2=wallTop*2

    wallSlope=sRef.properties.wallCurve
    wallDisc=sRef.properties.wallCirc

    blockWidth=sRef.properties.blockX

    blockGap=sRef.properties.Grout
    halfGrout = blockGap/2 # half grout for block size modifier

    wallDhalf=settings['d']/2 # offset by half wall depth to match UI setting

    for rowidx in range(len(rows)): # add blocks for each row.
        rows[rowidx].FillBlocks()

    if sRef.properties.MergeBlock: # merge (vertical) blocks in close proximity...
        for rowidx in range(len(rows)-1):
            if wallDisc:
                if wallSlope: r1 = wallTop*sin(abs(rows[rowidx].z)*pi/wallTop2)
                else: r1 = abs(rows[rowidx].z)
            else: r1 = 1

            Tollerance = blockGap/r1
            idxThis = len(rows[rowidx].BlocksNorm[:]) - 1
            idxThat = len(rows[rowidx+1].BlocksNorm[:]) - 1

            while True:
                # end loop when either array idx wraps
                if idxThis < 0 or idxThat < 0: break

                blockThis = rows[rowidx].BlocksNorm[idxThis]
                blockThat = rows[rowidx+1].BlocksNorm[idxThat]

                cx, cz, cw, ch, cd = blockThis[:5]
                ox, oz, ow, oh, od = blockThat[:5]

                if (abs(cw - ow) < Tollerance) and (abs(cx - ox) < Tollerance) :
                    if cw > ow: BlockW = ow
                    else: BlockW = cw

                    AllBlocks.append([(cx+ox)/2,(cz+oz+(oh-ch)/2)/2,BlockW,abs(cz-oz)+(ch+oh)/2,(cd+od)/2,None])

                    rows[rowidx].BlocksNorm.pop(idxThis)
                    rows[rowidx+1].BlocksNorm.pop(idxThat)
                    idxThis -= 1
                    idxThat -= 1

                elif cx > ox: idxThis -= 1
                else: idxThat -= 1


    if sRef.properties.wallShelf: # Add blocks to create a "shelf/platform".
# Does not account for openings (crosses gaps - which is a good thing)

        # Use wall block settings for shelf
        shelfBW=blockWidth
        shelfBWVar=settings['wv']
        shelfBH=sRef.properties.blockZ

        ShelfLft = sRef.properties.ShelfX
        ShelfBtm = sRef.properties.ShelfZ
        ShelfEnd = ShelfLft + sRef.properties.ShelfW
        ShelfTop = ShelfBtm + sRef.properties.ShelfH
        ShelfThk = sRef.properties.ShelfD
        ShelfThk2= ShelfThk*2 # double-depth to position at cursor.

        if sRef.properties.ShelfBack: # place blocks on backside of wall
            ShelfOffsets = [[0,ShelfThk,0],[0,wallDhalf,0],[0,ShelfThk,0],[0,wallDhalf,0],[0,ShelfThk,0],[0,wallDhalf,0],[0,ShelfThk,0],[0,wallDhalf,0]]
        else:
            ShelfOffsets = [[0,-wallDhalf,0],[0,-ShelfThk,0],[0,-wallDhalf,0],[0,-ShelfThk,0],[0,-wallDhalf,0],[0,-ShelfThk,0],[0,-wallDhalf,0],[0,-ShelfThk,0]]

        while ShelfBtm < ShelfTop: # Add blocks for each "shelf row" in area
            divs = fill(ShelfLft, ShelfEnd, shelfBW, shelfBW, shelfBWVar)

            for i in range(len(divs)-1): # add blocks for row divisions
                ThisBlockx = (divs[i]+divs[i+1])/2
                ThisBlockw = divs[i+1]-divs[i]-halfGrout
                AllBlocks.append([ThisBlockx, ShelfBtm, ThisBlockw, shelfBH, ShelfThk2, ShelfOffsets])

            ShelfBtm += shelfBH + halfGrout # moving up to next row...

# Set shelf material/color... on wish list.


    if sRef.properties.wallSteps: # Add blocks to create "steps".
# Does not account for openings (crosses gaps - which is a good thing)

        stepsFill=sRef.properties.StepBlocks
        steps2Left=sRef.properties.StepLeft

        # step block "filler" by wall block settings.
        stepFW=blockWidth
        StepFWVar=settings['wv']

        StepXMod = sRef.properties.StepT # step tread, also sets basic block size.
        StepZMod = sRef.properties.StepV

        StepLft = sRef.properties.StepX
        StepWide = sRef.properties.StepW
        StepRt = StepLft + StepWide
        StepBtm = sRef.properties.StepZ + StepZMod/2 # Start offset for centered blocks
        StepTop = StepBtm + sRef.properties.StepH

        StepThk = sRef.properties.StepD
        StepThk2=StepThk*2 # use double-depth due to offsets to position at cursor.

        # Use "corners" to adjust steps so not centered on depth.
        # steps at cursor so no gaps between steps and wall face due to wall block depth.
        if sRef.properties.StepBack: # place blocks on backside of wall
            StepOffsets = [[0,StepThk,0],[0,wallDhalf,0],[0,StepThk,0],[0,wallDhalf,0],[0,StepThk,0],[0,wallDhalf,0],[0,StepThk,0],[0,wallDhalf,0]]
        else:
            StepOffsets = [[0,-wallDhalf,0],[0,-StepThk,0],[0,-wallDhalf,0],[0,-StepThk,0],[0,-wallDhalf,0],[0,-StepThk,0],[0,-wallDhalf,0],[0,-StepThk,0]]

        # Add steps for each "step row" in area (neg width is interesting but prevented)
        while StepBtm < StepTop and StepWide > 0:

            # Make blocks for each step row - based on rowOb::fillblocks
            if stepsFill:
                divs = fill(StepLft, StepRt, StepXMod, stepFW, StepFWVar)

                #loop through the row divisions, adding blocks for each one
                for i in range(len(divs)-1):
                    ThisBlockx = (divs[i]+divs[i+1])/2
                    ThisBlockw = divs[i+1]-divs[i]-halfGrout

                    AllBlocks.append([ThisBlockx, StepBtm, ThisBlockw, StepZMod, StepThk2, StepOffsets])
            else: # "cantilevered steps"
                if steps2Left:
                    stepStart=StepRt-StepXMod
                else:
                    stepStart=StepLft

                AllBlocks.append([stepStart, StepBtm, StepXMod, StepZMod, StepThk2, StepOffsets])

            StepBtm += StepZMod + halfGrout # moving up to next row...
            StepWide -= StepXMod # reduce step width

            # adjust side limit depending on direction of steps
            if steps2Left:
                StepRt-=StepXMod # move from right
            else:
                StepLft+=StepXMod # move from left

    for row in rows: # Copy all the blocks out of the rows
        AllBlocks+=row.BlocksEdge
        AllBlocks+=row.BlocksNorm

    # make individual blocks for each block specified in the plan

    subDivision=settings['sdv']

    for block in AllBlocks:
        x,z,w,h,d,corners = block
        holeW2=w/2

        if wallDisc:
            if wallSlope: r1 = wallTop*sin(z*pi/wallTop2)
            else: r1 = z
        else: r1 = 1

        geom = MakeABlock([x-holeW2, x+holeW2, z-h/2, z+h/2, -d/2, d/2], subDivision, len(wallVs), corners)
        wallVs += geom[0]
        wallFs += geom[1]

    # make Arches for every opening specified in the plan.

    blockHMin=settings['hm']+blockGap

    for hole in holeList:
        # lower arch stones
        if hole.vl > 0 and hole.rtl > blockHMin:
            archGeneration(hole, wallVs, wallFs, -1)

        # top arch stones
        if hole.v > 0 and hole.rt > blockHMin:
            archGeneration(hole, wallVs, wallFs, 1)

    if wallSlope: # Curve wall, dome shape if "radialized".
        for i,vert in enumerate(wallVs):
            wallVs[i] = [vert[0],(wallTop+vert[1])*cos(vert[2]*pi/wallTop2),(wallTop+vert[1])*sin(vert[2]*pi/wallTop2)]

    if wallDisc: # Make wall circular, dome if sloped, else disc (flat round).
        for i,vert in enumerate(wallVs):
            wallVs[i] = [vert[2]*cos(vert[0]),vert[2]*sin(vert[0]),vert[1]]

    return wallVs,wallFs


################################################################################
#
# fill a linear space with divisions
#
#    objXO: x origin
#    objXL: x limit
#    avedst: the average distance between points
#    mindst: the minimum distance between points
#    dev: the maximum random deviation from avedst
#    center: flag to center the elements in the range, 0 == disabled
#
# returns an ordered list of points, including the end points.
#
def fill(objXO,objXL,avedst,mindst=0.0,dev=0.0,center=0):

    curpos = objXO
    poslist = [curpos]

    # Set offset by average spacing, then add blocks (fall through);
    # if not at edge.
    if center:
        curpos += ((objXL-objXO-mindst*2)%avedst)/2+mindst
        if curpos-poslist[-1]<mindst: curpos = poslist[-1]+mindst+random()*dev/2

        # clip to right edge.
        if (objXL-curpos<mindst) or (objXL-curpos< mindst):
            poslist.append(objXL)
            return poslist
        else: poslist.append(curpos)

    # make block edges
    while True:
        curpos += avedst+rndd()*dev
        if curpos-poslist[-1]<mindst:
            curpos = poslist[-1]+mindst+random()*dev/2

        if (objXL-curpos<mindst) or (objXL-curpos< mindst):
            poslist.append(objXL) # close off edges at limit
            return poslist
        else: poslist.append(curpos)


#######################################################################
#
# MakeABlock: Generate block geometry
#  to be made into a square cornered block, subdivided along the length.
#
#  bounds: a list of boundary positions:
#      0:left, 1:right, 2:bottom, 3:top, 4:back, 5:front
#  segsize: the maximum size before lengthwise subdivision occurs
#  vll: the number of vertexes already in the mesh. len(mesh.verts) should
#          give this number.
#  Offsets: list of coordinate delta values.
#      Offsets are lists, [x,y,z] in
#          [
#          0:left_bottom_back,
#          1:left_bottom_front,
#          2:left_top_back,
#          3:left_top_front,
#          4:right_bottom_back,
#          5:right_bottom_front,
#          6:right_top_back,
#          7:right_top_front,
#          ]
#  FaceExclude: list of faces to exclude from the faces list; see bounds above for indices
#  xBevScl: how much to divide the end (+- x axis) bevel dimensions.
#   Set to current average radius to compensate for angular distortion on curved blocks
#
#  return lists of points and faces.
#
def MakeABlock(bounds, segsize, vll=0, Offsets=None, FaceExclude=[], bevel=0, xBevScl=1):

    slices = fill(bounds[0], bounds[1], segsize, segsize, center=1)
    points = []
    faces = []

    if Offsets == None:
        points.append([slices[0],bounds[4],bounds[2]])
        points.append([slices[0],bounds[5],bounds[2]])
        points.append([slices[0],bounds[5],bounds[3]])
        points.append([slices[0],bounds[4],bounds[3]])

        for x in slices[1:-1]:
            points.append([x,bounds[4],bounds[2]])
            points.append([x,bounds[5],bounds[2]])
            points.append([x,bounds[5],bounds[3]])
            points.append([x,bounds[4],bounds[3]])

        points.append([slices[-1],bounds[4],bounds[2]])
        points.append([slices[-1],bounds[5],bounds[2]])
        points.append([slices[-1],bounds[5],bounds[3]])
        points.append([slices[-1],bounds[4],bounds[3]])

    else:
        points.append([slices[0]+Offsets[0][0],bounds[4]+Offsets[0][1],bounds[2]+Offsets[0][2]])
        points.append([slices[0]+Offsets[1][0],bounds[5]+Offsets[1][1],bounds[2]+Offsets[1][2]])
        points.append([slices[0]+Offsets[3][0],bounds[5]+Offsets[3][1],bounds[3]+Offsets[3][2]])
        points.append([slices[0]+Offsets[2][0],bounds[4]+Offsets[2][1],bounds[3]+Offsets[2][2]])

        for x in slices[1:-1]:
            xwt = (x-bounds[0])/(bounds[1]-bounds[0])
            points.append([x+Offsets[0][0]*(1-xwt)+Offsets[4][0]*xwt,bounds[4]+Offsets[0][1]*(1-xwt)+Offsets[4][1]*xwt,bounds[2]+Offsets[0][2]*(1-xwt)+Offsets[4][2]*xwt])
            points.append([x+Offsets[1][0]*(1-xwt)+Offsets[5][0]*xwt,bounds[5]+Offsets[1][1]*(1-xwt)+Offsets[5][1]*xwt,bounds[2]+Offsets[1][2]*(1-xwt)+Offsets[5][2]*xwt])
            points.append([x+Offsets[3][0]*(1-xwt)+Offsets[7][0]*xwt,bounds[5]+Offsets[3][1]*(1-xwt)+Offsets[7][1]*xwt,bounds[3]+Offsets[3][2]*(1-xwt)+Offsets[7][2]*xwt])
            points.append([x+Offsets[2][0]*(1-xwt)+Offsets[6][0]*xwt,bounds[4]+Offsets[2][1]*(1-xwt)+Offsets[6][1]*xwt,bounds[3]+Offsets[2][2]*(1-xwt)+Offsets[6][2]*xwt])

        points.append([slices[-1]+Offsets[4][0],bounds[4]+Offsets[4][1],bounds[2]+Offsets[4][2]])
        points.append([slices[-1]+Offsets[5][0],bounds[5]+Offsets[5][1],bounds[2]+Offsets[5][2]])
        points.append([slices[-1]+Offsets[7][0],bounds[5]+Offsets[7][1],bounds[3]+Offsets[7][2]])
        points.append([slices[-1]+Offsets[6][0],bounds[4]+Offsets[6][1],bounds[3]+Offsets[6][2]])

    faces.append([vll,vll+3,vll+2,vll+1])

    for x in range(len(slices)-1):
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll-3,vll+1,vll+4])
        vll+=1

    faces.append([vll,vll+1,vll+2,vll+3])

    return points, faces


#
#For generating Keystone Geometry
def MakeAKeystone(xpos, width, zpos, ztop, zbtm, thick, bevel, vll=0, FaceExclude=[], xBevScl=1):
    __doc__ = """\
    MakeAKeystone returns lists of points and faces to be made into a square cornered keystone, with optional bevels.
    xpos: x position of the centerline
    width: x width of the keystone at the widest point (discounting bevels)
    zpos: z position of the widest point
    ztop: distance from zpos to the top
    zbtm: distance from zpos to the bottom
    thick: thickness
    bevel: the amount to raise the back vertex to account for arch beveling
    vll: the number of vertexes already in the mesh. len(mesh.verts) should give this number
    faceExclude: list of faces to exclude from the faces list.  0:left, 1:right, 2:bottom, 3:top, 4:back, 5:front
    xBevScl: how much to divide the end (+- x axis) bevel dimensions.  Set to current average radius to compensate for angular distortion on curved blocks
    """

    points = []
    faces = []
    faceinclude = [1 for x in range(6)]
    for x in FaceExclude: faceinclude[x]=0
    Top = zpos + ztop
    Btm = zpos - zbtm
    Wid = width/2.
    Thk = thick/2.

    # The front top point
    points.append([xpos, Thk, Top])
    # The front left point
    points.append([xpos-Wid, Thk, zpos])
    # The front bottom point
    points.append([xpos, Thk, Btm])
    # The front right point
    points.append([xpos+Wid, Thk, zpos])

    MirrorPoints = []
    for i in points:
        MirrorPoints.append([i[0],-i[1],i[2]])
    points += MirrorPoints
    points[6][2] += bevel

    faces.append([3,2,1,0])
    faces.append([4,5,6,7])
    faces.append([4,7,3,0])
    faces.append([5,4,0,1])
    faces.append([6,5,1,2])
    faces.append([7,6,2,3])
    # Offset the vertex numbers by the number of verticies already in the list
    for i in range(len(faces)):
        for j in range(len(faces[i])): faces[i][j] += vll

    return points, faces


#class openings in the wall
class opening:
    __doc__ = """\
    This is the class for holding the data for the openings in the wall.
    It has methods for returning the edges of the opening for any given position value,
    as well as bevel settings and top and bottom positions.
    It stores the 'style' of the opening, and all other pertinent information.
    """
    # x = 0. # x position of the opening
    # z = 0. # x position of the opening
    # w = 0. # width of the opening
    # h = 0. # height of the opening
    r = 0  # top radius of the arch (derived from 'v')
    rl = 0 # lower radius of the arch (derived from 'vl')
    rt = 0 # top arch thickness
    rtl = 0# lower arch thickness
    ts = 0 # Opening side thickness, if greater than average width, replaces it.
    c = 0  # top arch corner position (for low arches), distance from the top of the straight sides
    cl = 0 # lower arch corner position (for low arches), distance from the top of the straight sides
    # form = 0 # arch type (unused for now)
    # b = 0. # back face bevel distance, like an arrow slit
    v = 0. # top arch height
    vl = 0.# lower arch height
    # variable "s" is used for "side" in the "edge" function.
    # it is a signed int, multiplied by the width to get + or - of the center

    def btm(self):
        if self.vl <= self.w/2 : return self.z-self.h/2-self.vl-self.rtl
        else: return self.z - sqrt((self.rl+self.rtl)**2 - (self.rl - self.w/2 )**2)  - self.h/2


    def top(self):
        if self.v <= self.w/2 : return self.z+self.h/2+self.v+self.rt
        else: return sqrt((self.r+self.rt)**2 - (self.r - self.w/2 )**2) + self.z + self.h/2


    #crits returns the critical split points, or discontinuities, used for making rows
    def crits(self):
        critlist = []
        if self.vl>0: # for lower arch
            # add the top point if it is pointed
            #if self.vl >= self.w/2.: critlist.append(self.btm())
            if self.vl < self.w/2.:#else: for low arches, with wedge blocks under them
                #critlist.append(self.btm())
                critlist.append(self.z-self.h/2 - self.cl)

        if self.h>0: # if it has a height, append points at the top and bottom of the main square section
            critlist += [self.z-self.h/2,self.z+self.h/2]
        else:  # otherwise, append just one in the center
            critlist.append(self.z)

        if self.v>0:  # for the upper arch
            if self.v < self.w/2.: # add the splits for the upper wedge blocks, if needed
                critlist.append(self.z+self.h/2 + self.c)
                #critlist.append(self.top())
            #otherwise just add the top point, if it is pointed
            #else: critlist.append(self.top())

        return critlist

    #
    # get the side position of the opening.
    # ht is the z position; s is the side: 1 for right, -1 for left
    # if the height passed is above or below the opening, return None
    #
    def edgeS(edgeParms, ht, s):

        wallTopZ=dims['t']
        wallHalfH=edgeParms.h/2
        wallHalfW=edgeParms.w/2
        wallBase=edgeParms.z

        # set the row radius: 1 for standard wall (flat)
        if settings['Round']:
            if settings['Curve']: r1 = abs(wallTopZ*sin(ht*pi/(wallTopZ*2)))
            else: r1 = abs(ht)
        else: r1 = 1

        #Go through all the options, and return the correct value
        if ht < edgeParms.btm(): #too low
            return None
        elif ht > edgeParms.top(): #too high
            return None

        # Check for circ returning None - prevent TypeError (script failure) with float.

        # in this range, pass the lower arch info
        elif ht <= wallBase-wallHalfH-edgeParms.cl:
            if edgeParms.vl > wallHalfW:
                circVal = circ(ht-wallBase+wallHalfH,edgeParms.rl+edgeParms.rtl)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*(wallHalfW-edgeParms.rl+circVal)/r1
            else:
                circVal = circ(ht-wallBase+wallHalfH+edgeParms.vl-edgeParms.rl,edgeParms.rl+edgeParms.rtl)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*circVal/r1

        #in this range, pass the top arch info
        elif ht >= wallBase+wallHalfH+edgeParms.c:
            if edgeParms.v > wallHalfW:
                circVal = circ(ht-wallBase-wallHalfH,edgeParms.r+edgeParms.rt)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*(wallHalfW-edgeParms.r+circVal)/r1
            else:
                circVal = circ(ht-(wallBase+wallHalfH+edgeParms.v-edgeParms.r),edgeParms.r+edgeParms.rt)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*circVal/r1

        #in this range pass the lower corner edge info
        elif ht <= wallBase-wallHalfH:
            d = sqrt(edgeParms.rtl**2 - edgeParms.cl**2)
            if edgeParms.cl > edgeParms.rtl/sqrt(2.): return edgeParms.x + s*(wallHalfW + (wallBase - wallHalfH - ht)*d/edgeParms.cl)/r1
            else: return edgeParms.x + s*( wallHalfW + d )/r1

        #in this range pass the upper corner edge info
        elif ht >= wallBase+wallHalfH:
            d = sqrt(edgeParms.rt**2 - edgeParms.c**2)
            if edgeParms.c > edgeParms.rt/sqrt(2.): return edgeParms.x + s*(wallHalfW + (ht - wallBase - wallHalfH )*d/edgeParms.c)/r1
            else: return edgeParms.x + s*( wallHalfW + d )/r1

        #in this range, pass the middle info (straight sides)
        else: return edgeParms.x + s*wallHalfW/r1


    # get the top or bottom of the opening
    # ht is the x position; archSide: 1 for top, -1 for bottom
    #
    def edgeV(self, ht, archSide):
        wallTopZ=dims['t']
        dist = abs(self.x-ht)

        def radialAdjust(dist, sideVal): # adjust distance and for radial geometry.
            if settings['Round']:
                if settings['Curve']:
                    dist = dist * abs(wallTopZ*sin(sideVal*pi/(wallTopZ*2)))
                else:
                    dist = dist * sideVal
            return dist

        if archSide > 0 : #check top down
            #hack for radialized masonry, import approx Z instead of self.top()
            dist = radialAdjust(dist, self.top())

            #no arch on top, flat
            if not self.r: return self.z+self.h/2

            #pointed arch on top
            elif self.v > self.w/2:
                circVal = circ(dist-self.w/2+self.r,self.r+self.rt)
                if circVal == None:
                    return 0.0
                else: return self.z+self.h/2+circVal

            #domed arch on top
            else:
                circVal = circ(dist,self.r+self.rt)
                if circVal == None:
                    return 0.0
                else: return self.z+self.h/2+self.v-self.r+circVal

        else: #check bottom up
            #hack for radialized masonry, import approx Z instead of self.top()
            dist = radialAdjust(dist, self.btm())

            #no arch on bottom
            if not self.rl: return self.z-self.h/2

            #pointed arch on bottom
            elif self.vl > self.w/2:
                circVal = circ(dist-self.w/2+self.rl,self.rl+self.rtl)
                if circVal == None:
                    return 0.0
                else: return self.z-self.h/2-circVal

            #old conditional? if (dist-self.w/2+self.rl)<=(self.rl+self.rtl):
            #domed arch on bottom
            else:
                circVal = circ(dist,self.rl+self.rtl) # dist-self.w/2+self.rl
                if circVal == None:
                    return 0.0
                else: return self.z-self.h/2-self.vl+self.rl-circVal


    #
    def edgeBev(self, ht):
        wallTopZ=dims['t']
        if ht > (self.z + self.h/2): return 0.0
        if ht < (self.z - self.h/2): return 0.0
        if settings['Round']:
            if settings['Curve']: r1 = abs(wallTopZ*sin(ht*pi/(wallTopZ*2)))
            else: r1 = abs(ht)
        else: r1 = 1
        bevel = self.b / r1
        return bevel
#
##
#

    def __init__(self, xpos, zpos, width, height, archHeight=0, archThk=0,
                 archHeightLower=0, archThkLower=0, bevel=0, edgeThk=0):
        self.x = float(xpos)
        self.z = float(zpos)
        self.w = float(width)
        self.h = float(height)
        self.rt = archThk
        self.rtl = archThkLower
        self.v = archHeight
        self.vl = archHeightLower

        #find the upper arch radius
        if archHeight >= width/2:
            # just one arch, low long
            self.r = (self.v**2)/self.w + self.w/4
        elif archHeight <= 0:
            # No arches
            self.r = 0
            self.v = 0
        else:
            # Two arches
            self.r = (self.w**2)/(8*self.v) + self.v/2.
            self.c = self.rt*cos(atan(self.w/(2*(self.r-self.v))))

        #find the lower arch radius
        if archHeightLower >= width/2:
            self.rl = (self.vl**2)/self.w + self.w/4
        elif archHeightLower <= 0:
            self.rl = 0
            self.vl = 0
        else:
            self.rl = (self.w**2)/(8*self.vl) + self.vl/2.
            self.cl = self.rtl*cos(atan(self.w/(2*(self.rl-self.vl))))

        #self.form = something?
        self.b = float(bevel)
        self.ts = edgeThk
#
#
#class for the whole wall boundaries; a sub-class of "opening"
class OpeningInv(opening):
    #this is supposed to switch the sides of the opening
    #so the wall will properly enclose the whole wall.

   def edgeS(self, ht, s):
       return opening.edgeS(self, ht, -s)

   def edgeV(self, ht, s):
       return opening.edgeV(self, ht, -s)

#class rows in the wall
class rowOb:
    __doc__ = """\
    This is the class for holding the data for individual rows of blocks.
    each row is required to have some edge blocks, and can also have
    intermediate sections of "normal" blocks.
    """

    #z = 0.
    #h = 0.
    radius = 1
    EdgeOffset = 0
#    BlocksEdge = []
#    RowSegments = []
#    BlocksNorm = []

    def FillBlocks(self):
        wallTopZ=dims['t']

        # Set the radius variable, in the case of radial geometry
        if settings['Round']:
            if settings['Curve']: self.radius = wallTopZ*(sin(self.z*pi/(wallTopZ*2)))
            else: self.radius = self.z

        #initialize internal variables from global settings

        SetH = settings['h']
# no HVar?
        SetWid = settings['w']
        SetWidVar = settings['wv']
        SetGrt = settings['g']
        SetDepth = settings['d']
        SetDepthVar = settings['dv']

        # height weight, make shorter rows have narrower blocks, and vice-versa
        rowHWt=((self.h/SetH-1)*ROW_H_WEIGHT+1)

        # set variables for persistent values: loop optimization, readability, single ref for changes.

        avgDist = rowHWt*SetWid/self.radius
        minDist = SetWid/self.radius
        deviation = rowHWt*SetWidVar/self.radius
        grtOffset = SetGrt/(2*self.radius)

        # init loop variables that may change...

        blockGap=SetGrt/self.radius
        ThisBlockHeight = self.h
        ThisBlockDepth = SetDepth+(rndd()*SetDepthVar)

        for segment in self.RowSegments:
            divs = fill(segment[0]+grtOffset, segment[1]-grtOffset, avgDist, minDist, deviation)

            # loop through the divisions, adding blocks for each one
            for i in range(len(divs)-1):
                ThisBlockx = (divs[i]+divs[i+1])/2
                ThisBlockw = divs[i+1]-divs[i]-blockGap

                self.BlocksNorm.append([ThisBlockx, self.z, ThisBlockw, ThisBlockHeight, ThisBlockDepth, None])

                if SetDepthVar: # vary depth
                    ThisBlockDepth = SetDepth+(rndd()*SetDepthVar)

    def __init__(self,centerheight,rowheight,edgeoffset=0):
        self.z = float(centerheight)
        self.h = float(rowheight)
        self.EdgeOffset = float(edgeoffset)

#THIS INITILIZATION IS IMPORTANT!  OTHERWISE ALL OBJECTS WILL HAVE THE SAME LISTS!
        self.BlocksEdge = []
        self.RowSegments = []
        self.BlocksNorm = []

#
def arch(ra,rt,x,z, archStart, archEnd, bevel, bevAngle, vll):
    __doc__ = """\
    Makes a list of faces and vertexes for arches.
    ra: the radius of the arch, to the center of the bricks
    rt: the thickness of the arch
    x: x center location of the circular arc, as if the arch opening were centered on x = 0
    z: z center location of the arch
    anglebeg: start angle of the arch, in radians, from vertical?
    angleend: end angle of the arch, in radians, from vertical?
    bevel: how much to bevel the inside of the arch.
    vll: how long is the vertex list already?
    """
    avlist = []
    aflist = []

    #initialize internal variables for global settings
#overkill? no, first step to eliminating "globals", and hope too improve performance.
    SetH = settings['h']
    SetWid = settings['w']
    SetWidVar = settings['wv']
    SetGrt = settings['g']
    SetDepth = settings['d']
    SetDepthVar = settings['dv']
    wallTopZ=dims['t']

    wallCirc=settings['Round']

    ArchInner = ra-rt/2
    ArchOuter = ra+rt/2-SetGrt

    DepthBack = -SetDepth/2-rndc()*SetDepthVar
    DepthFront = SetDepth/2+rndc()*SetDepthVar

# there's something wrong here...
    if wallCirc: subdivision = settings['sdv']
    else: subdivision = 0.12

    blockGap=SetGrt/(2*ra) # grout offset
    # set up the offsets, it will be the same for every block
    offsets = ([[0]*2 + [bevel]] + [[0]*3]*3)*2

    #make the divisions in the "length" of the arch
    divs = fill(archStart, archEnd, settings['w']/ra, settings['w']/ra, settings['wv']/ra)

    for i in range(len(divs)-1):
         # modify block offsets for bevel.
        if i == 0:
            ThisOffset = offsets[:]
            pointsToAffect=(0,2,3)

            for num in pointsToAffect:
                offsets[num]=ThisOffset[num][:]
                offsets[num][0]+=bevAngle
        elif i == len(divs)-2:
            ThisOffset=offsets[:]
            pointsToAffect=(4,6,7)

            for num in pointsToAffect:
                offsets[num]=ThisOffset[num][:]
                offsets[num][0]-=bevAngle
        else:
            ThisOffset = offsets

        geom = MakeABlock([divs[i]+blockGap, divs[i+1]-blockGap, ArchInner, ArchOuter, DepthBack, DepthFront],
                          subdivision, len(avlist) + vll, ThisOffset, [], None, ra)

        avlist += geom[0]
        aflist += geom[1]

        if SetDepthVar: # vary depth
            DepthBack = -SetDepth/2-rndc()*SetDepthVar
            DepthFront = SetDepth/2+rndc()*SetDepthVar

    for i,vert in enumerate(avlist):
        v0 = vert[2]*sin(vert[0]) + x
        v1 = vert[1]
        v2 = vert[2]*cos(vert[0]) + z

        if wallCirc:
            if settings['Curve']: r1 = wallTopZ*(sin(v2*pi/(wallTopZ*2)))
            else: r1 = v2
            v0 = v0/r1

        avlist[i] = [v0,v1,v2]

    return (avlist,aflist)


#################################################################
#
# Make wedge blocks for openings.
#
#  example:
#   wedgeBlocks(row, LeftWedgeEdge, LNerEdge, LEB, r1)
#   wedgeBlocks(row, RNerEdge, RightWedgeEdge, rSide, r1)
#
def wedgeBlocks(row, opening, leftPos, rightPos, edgeSide, r1):

    wedgeWRad=settings['w']/r1

    wedgeEdges = fill(leftPos, rightPos, wedgeWRad, wedgeWRad, settings['wv']/r1)

    blockDepth=settings['d']
    blockDepthV=settings['dv']
    blockGap=settings['g']/r1

    for i in range(len(wedgeEdges)-1):
        x = (wedgeEdges[i+1] + wedgeEdges[i])/2
        w = wedgeEdges[i+1] - wedgeEdges[i] - blockGap
        halfBW=w/2

        ThisBlockDepth = blockDepth+rndd()*blockDepthV

        LeftVertOffset =  -( row.z - (row.h/2)*edgeSide - (opening.edgeV(x-halfBW,edgeSide)))
        RightVertOffset = -( row.z - (row.h/2)*edgeSide - opening.edgeV(x+halfBW,edgeSide) )

        #Wedges are on top = off, blank, off, blank
        #Wedges are on btm = blank, off, blank, off
        ThisBlockOffsets = [[0,0,LeftVertOffset]]*2 + [[0]*3]*2 + [[0,0,RightVertOffset]]*2

        # Instert or append "blank" for top or bottom wedges.
        if edgeSide == 1: ThisBlockOffsets = ThisBlockOffsets + [[0]*3]*2
        else: ThisBlockOffsets = [[0]*3]*2 + ThisBlockOffsets

        row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,ThisBlockOffsets])


############################################################
#
#
    #set end blocks
    #check for openings, record top and bottom of row for right and left of each
    #if both top and bottom intersect create blocks on each edge, appropriate to the size of the overlap
    #if only one side intersects, run fill to get edge positions, but this should never happen
    #
#
def rowProcessing(row, holeList, WallBoundaries):

    if settings['Round']:#this checks for radial stonework, and sets the row radius if required
        if settings['Curve']: r1 = abs(dims['t']*sin(row.z*pi/(dims['t']*2)))
        else: r1 = abs(row.z)
    else: r1 = 1

    # set block working values
    blockWidth=settings['w']
    blockWVar=settings['wv']
    blockDepth=settings['d']
    blockDVar=settings['dv']

    blockGap=settings['g']/r1

    # set row working values
    rowH=row.h
    rowH2=rowH/2
    rowEdge=row.EdgeOffset/r1
    rowStart=dims['s']+rowEdge
# shouldn't rowEnd be minus rowEdge?
    rowEnd=dims['e']+rowEdge
    rowTop = row.z+rowH2
    rowBtm = row.z-rowH2

    # left and right wall limits for top and bottom of row.
    edgetop=[[rowStart,WallBoundaries],[rowEnd,WallBoundaries]]
    edgebtm=[[rowStart,WallBoundaries],[rowEnd,WallBoundaries]]

    for hole in holeList:
        #check the top and bottom of the row, looking at the opening from the right
        holeEdge = [hole.edgeS(rowTop, -1), hole.edgeS(rowBtm, -1)]

        # If either one hit the opening, make split points for the side of the opening.
        if holeEdge[0] or holeEdge[1]:
            holeEdge += [hole.edgeS(rowTop, 1), hole.edgeS(rowBtm, 1)]

            # If one of them missed for some reason, set that value to
            # the middle of the opening.
            for i,pos in enumerate(holeEdge):
                if pos == None: holeEdge[i] = hole.x

            # add the intersects to the list of edge points
            edgetop.append([holeEdge[0],hole])
            edgetop.append([holeEdge[2],hole])
            edgebtm.append([holeEdge[1],hole])
            edgebtm.append([holeEdge[3],hole])

    # make the walls in order, sort the intersects.
#  remove edge points that are out of order;
#  else the "oddity" where overlapping openings create blocks inversely.
    edgetop.sort()
    edgebtm.sort()

    # These two loops trim the edges to the limits of the wall.
    # This way openings extending outside the wall don't enlarge the wall.
    while True:
        try:
            if (edgetop[-1][0] > rowEnd) or (edgebtm[-1][0] > rowEnd):
                edgetop[-2:] = []
                edgebtm[-2:] = []
            else: break
        except IndexError: break
    #still trimming the edges...
    while True:
        try:
            if (edgetop[0][0] < rowStart) or (edgebtm[0][0] < rowStart):
                edgetop[:2] = []
                edgebtm[:2] = []
            else: break
        except IndexError: break

    # finally, make edge blocks and rows!

    # Process each section, a pair of points in edgetop,
    # and place the edge blocks and inbetween normal block zones into the row object.

    blockHMin=settings['hm']

    #maximum distance to span with one block
    MaxWid = (blockWidth+blockWVar)/r1

    for OpnSplitNo in range(int(len(edgetop)/2)):
        lEdgeIndx=2*OpnSplitNo
        rEdgeIndx=lEdgeIndx+1

        leftOpening = edgetop[lEdgeIndx][1]
        rightOpening = edgetop[rEdgeIndx][1]

        #find the difference between the edge top and bottom on both sides
        LTop = edgetop[lEdgeIndx][0]
        LBtm = edgebtm[lEdgeIndx][0]
        RTop = edgetop[rEdgeIndx][0]
        RBtm = edgebtm[rEdgeIndx][0]
        LDiff = LBtm-LTop
        RDiff = RTop-RBtm

        # set side edge limits from top and bottom
        if LDiff > 0: # if furthest edge is top,
            LEB = 1
            LFarEdge = LTop #The furthest edge
            LNerEdge = LBtm #the nearer edge
        else: # furthest edge is bottom
            LEB = -1
            LFarEdge = LBtm
            LNerEdge = LTop

        if RDiff > 0: # if furthest edge is top,
            rSide = 1
            RFarEdge = RTop #The furthest edge
            RNerEdge = RBtm #the nearer edge
        else: # furthest edge is bottom
            rSide = -1
            RFarEdge = RBtm # The furthest edge
            RNerEdge = RTop # the nearer edge

        blockXx=RNerEdge-LNerEdge # The space between the closest edges of the openings in this section of the row
        blockXm=(RNerEdge + LNerEdge)/2 # The mid point between the nearest edges

        #check the left and right sides for wedge blocks
        #find the edge of the correct side, offset for minimum block height.  The LEB decides top or bottom
        ZPositionCheck = row.z + (rowH2-blockHMin)*LEB
#edgeS may return "None"
        LeftWedgeEdge = leftOpening.edgeS(ZPositionCheck,1)

        if (abs(LDiff) > blockWidth) or (not LeftWedgeEdge):
            #make wedge blocks
            if not LeftWedgeEdge: LeftWedgeEdge = leftOpening.x
            wedgeBlocks(row, leftOpening, LeftWedgeEdge, LNerEdge, LEB, r1)
            #set the near and far edge settings to vertical, so the other edge blocks don't interfere
            LFarEdge , LTop , LBtm = LNerEdge, LNerEdge, LNerEdge
            LDiff = 0

        #Now do the wedge blocks for the right, same drill... repeated code?
        #find the edge of the correct side, offset for minimum block height.
        ZPositionCheck = row.z + (rowH2-blockHMin)*rSide
#edgeS may return "None"
        RightWedgeEdge = rightOpening.edgeS(ZPositionCheck,-1)
        if (abs(RDiff) > blockWidth) or (not RightWedgeEdge):
            #make wedge blocks
            if not RightWedgeEdge: RightWedgeEdge = rightOpening.x
            wedgeBlocks(row, rightOpening, RNerEdge, RightWedgeEdge, rSide, r1)

            #set the near and far edge settings to vertical, so the other edge blocks don't interfere
            RFarEdge , RTop , RBtm = RNerEdge, RNerEdge, RNerEdge
            RDiff = 0

        # Single block - needed for arch "point" (keystone).
        if blockXx < MaxWid:
            x = (LNerEdge + RNerEdge)/2.
            w = blockXx
            ThisBlockDepth = rndd()*blockDVar+blockDepth
            BtmOff = LBtm - LNerEdge
            TopOff = LTop - LNerEdge
            ThisBlockOffsets = [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2
            BtmOff = RBtm - RNerEdge
            TopOff = RTop - RNerEdge
            ThisBlockOffsets += [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2

            pointsToAffect=(0,2)
            bevelBlockOffsets(ThisBlockOffsets,leftOpening.edgeBev(rowTop),pointsToAffect)

            pointsToAffect=(4,6)
            bevelBlockOffsets(ThisBlockOffsets,-rightOpening.edgeBev(rowTop),pointsToAffect)

            row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,ThisBlockOffsets])
            continue

        # must be two or more blocks

        # Left offsets
        BtmOff = LBtm - LNerEdge
        TopOff = LTop - LNerEdge
        leftOffsets = [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2 + [[0]*3]*4
        bevelL = leftOpening.edgeBev(rowTop)

        pointsToAffect=(0,2)
        bevelBlockOffsets(leftOffsets,bevelL,pointsToAffect)

        # Right offsets
        BtmOff = RBtm - RNerEdge
        TopOff = RTop - RNerEdge
        rightOffsets = [[0]*3]*4 + [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2
        bevelR = rightOpening.edgeBev(rowTop)

        pointsToAffect=(4,6)
        bevelBlockOffsets(rightOffsets,-bevelR,pointsToAffect)

        if blockXx < MaxWid*2: # only two blocks?
            #div is the x position of the dividing point between the two bricks
            div = blockXm + (rndd()*blockWVar)/r1

            #set the x position and width for the left block
            x = (div + LNerEdge)/2 - blockGap/4
            w = (div - LNerEdge) - blockGap/2
            ThisBlockDepth = rndd()*blockDVar+blockDepth
            #For reference: EdgeBlocks = [[x,z,w,h,d,[corner offset matrix]],[etc.]]
            row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,leftOffsets])

            #Initialize for the block on the right side
            x = (div + RNerEdge)/2 + blockGap/4
            w = (RNerEdge - div) - blockGap/2
            ThisBlockDepth = rndd()*blockDVar+blockDepth
            row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,rightOffsets])
            continue

        # more than two blocks in the row, and no wedge blocks

        #make Left edge block
        #set the x position and width for the block
        widOptions = [blockWidth, bevelL + blockWidth, leftOpening.ts]
        baseWidMax = max(widOptions)
        w = baseWidMax+row.EdgeOffset+(rndd()*blockWVar)
        widOptions[0] = blockWidth
        widOptions[2] = w
        w = max(widOptions) / r1 - blockGap
        x = w/2 + LNerEdge + blockGap/2
        BlockRowL = x + w/2
        ThisBlockDepth = rndd()*blockDVar+blockDepth
        row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,leftOffsets])

        #make Right edge block
        #set the x position and width for the block
        widOptions = [blockWidth, bevelR + blockWidth, rightOpening.ts]
        baseWidMax = max(widOptions)
        w = baseWidMax+row.EdgeOffset+(rndd()*blockWVar)
        widOptions[0] = blockWidth
        widOptions[2] = w
        w = max(widOptions) / r1 - blockGap
        x = RNerEdge - w/2 - blockGap/2
        BlockRowR = x - w/2
        ThisBlockDepth = rndd()*blockDVar+blockDepth
        row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,rightOffsets])

        row.RowSegments.append([BlockRowL,BlockRowR])


###################################
#
# create lists of blocks for wall.
#
# Returns: list of rows.
#
def wallPlan(sRef,holeList):

    rows = []

    wallTop=sRef.properties.wallZ
    wallWid=sRef.properties.wallX
    blockHMin=sRef.properties.HeightMin
    blockHMax=sRef.properties.blockZ
    blockHVar=sRef.properties.HeightVar
    groutG=sRef.properties.Grout

    blockHMin+=groutG
    rowHMin=blockHMin

    # splits are a row division, for openings
    splits=[0] # split bottom row

    #add a split for each critical point on each opening
    for hole in holeList: splits += hole.crits()

    #and, a split for the top row
    splits.append(wallTop)
    splits.sort()

    #divs are the normal old row divisions, add them between the top and bottom split
# what's with "[1:-1]" at end????
    divs = fill(splits[0],splits[-1],blockHMax,blockHMin,blockHVar)[1:-1]

    #remove the divisions that are too close to the splits, so we don't get tiny thin rows
    for i in range(len(divs)-1,-1,-1):
        for j in range(len(splits)):
            diff = abs(divs[i] - splits[j])
            #(blockHMin+groutG) is the old minimum value
            if diff < (blockHMax-blockHVar+groutG):
                del(divs[i])
                break

    #now merge the divs and splits lists
    divs += splits
    divs.sort()

    #trim the rows to the bottom and top of the wall
    if divs[0] < 0: divs[:1] = []
    if divs[-1] > wallTop: divs[-1:] = []

    #now, make the data for each row
    #rows = [[center height,row height,edge offset],[etc.]]

    divCount = len(divs)-1 # number of divs to check
    divCheck = 0 # current div entry

    while divCheck < divCount:
        RowZ = (divs[divCheck]+divs[divCheck+1])/2
        RowHeight = divs[divCheck+1]-divs[divCheck]-groutG
        EdgeOffset = settings['eoff']*(fmod(divCheck,2)-0.5)

        # if row height is too shallow: delete next div entry, decrement total, and recheck current entry.
        if RowHeight < rowHMin:
            del(divs[divCheck+1])
            divCount -= 1 # Adjust count for removed div entry.
            continue

        rows.append(rowOb(RowZ, RowHeight, EdgeOffset))

        divCheck += 1 # on to next div entry

    # set up opening object to handle the edges of the wall
    WallBoundaries = OpeningInv((dims['s'] + dims['e'])/2,wallTop/2,wallWid,wallTop)

    #Go over each row in the list, set up edge blocks and block sections
    for rownum in range(len(rows)):
        rowProcessing(rows[rownum], holeList, WallBoundaries)

    return rows


#####################################
#
# Makes arches for the top and bottom
# hole is the "wall opening" that the arch is for.
#
def archGeneration(hole, vlist, flist, sideSign):

    avlist = []
    aflist = []

    if sideSign == 1: # top
        r = hole.r #radius of the arch
        rt = hole.rt #thickness of the arch (stone height)
        v = hole.v #height of the arch
        c = hole.c
    else: # bottom
        r = hole.rl #radius of the arch
        rt = hole.rtl #thickness of the arch (stone height)
        v = hole.vl #height of the arch
        c = hole.cl

    ra = r + rt/2 #average radius of the arch
    x = hole.x
    w = hole.w
    holeW2=w/2
    h = hole.h
    z = hole.z
    bev = hole.b

    blockHMin=settings['hm']
    blockGap=settings['g']
    blockDepth=settings['d']
    blockDVar=settings['dv']

    if v > holeW2: # two arcs, to make a pointed arch
        # positioning
        zpos = z + (h/2)*sideSign
        xoffset = r - holeW2
        #left side top, right side bottom
        #angles reference straight up, and are in radians
        bevRad = r + bev
        bevHt = sqrt(bevRad**2 - (bevRad - (holeW2 + bev))**2)
        midHalfAngle = atan(v/(r-holeW2))
        midHalfAngleBevel = atan(bevHt/(r-holeW2))
        bevelAngle = midHalfAngle - midHalfAngleBevel
        anglebeg = (pi/2)*(-sideSign)
        angleend = (pi/2)*(-sideSign) + midHalfAngle

        avlist,aflist = arch(ra,rt,(xoffset)*(sideSign),zpos,anglebeg,angleend,bev,bevelAngle,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+hole.x,vert[1],vert[2]]
        vlist += avlist
        flist += aflist

        #right side top, left side bottom
        #angles reference straight up, and are in radians
        anglebeg = (pi/2)*(sideSign) - midHalfAngle
        angleend = (pi/2)*(sideSign)

        avlist,aflist = arch(ra,rt,(xoffset)*(-sideSign),zpos,anglebeg,angleend,bev,bevelAngle,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+hole.x,vert[1],vert[2]]

        vlist += avlist
        flist += aflist

        #keystone
        Dpth = blockDepth+rndc()*blockDVar
        angleBevel = (pi/2)*(sideSign) - midHalfAngle
        Wdth = (rt - blockGap - bev) * 2 * sin(angleBevel) * sideSign #note, sin may be negative
        MidZ = ((sideSign)*(bevHt + h/2.0) + z) + (rt - blockGap - bev) * cos(angleBevel) #note, cos may come out negative too
        nearCorner = sideSign*(MidZ - z) - v - h/2

        if sideSign == 1:
            TopHt = hole.top() - MidZ - blockGap
            BtmHt = nearCorner
        else:
            BtmHt =  - (hole.btm() - MidZ) - blockGap
            TopHt = nearCorner

        # set the amout to bevel the keystone
        keystoneBevel = (bevHt - v)*sideSign
        if Wdth >= blockHMin:
            avlist,aflist = MakeAKeystone(x, Wdth, MidZ, TopHt, BtmHt, Dpth, keystoneBevel, len(vlist))

            if settings['Round']:
                for i,vert in enumerate(avlist):
                    if settings['Curve']: r1 = dims['t']*sin(vert[2]*pi/(dims['t']*2))
                    else: r1 = vert[2]
                    avlist[i] = [((vert[0]-hole.x)/r1)+hole.x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist

    else: # only one arc - curve not peak.
#bottom (sideSign -1) arch has poorly sized blocks...

        zpos = z + (sideSign * (h/2 + v - r)) # single arc positioning

        #angles reference straight up, and are in radians
        if sideSign == -1: angleOffset = pi
        else: angleOffset = 0.0

        if v < holeW2:
            halfangle = atan(w/(2*(r-v)))

            anglebeg = angleOffset - halfangle
            angleend = angleOffset + halfangle
        else:
            anglebeg = angleOffset - pi/2
            angleend = angleOffset + pi/2

        avlist,aflist = arch(ra,rt,0,zpos,anglebeg,angleend,bev,0.0,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+x,vert[1],vert[2]]

        vlist += avlist
        flist += aflist

        #Make the Side Stones
        width = sqrt(rt**2 - c**2) - blockGap

        if c > blockHMin + blockGap and c < width + blockGap:
            if settings['Round']: subdivision = settings['sdv'] * (zpos + (h/2)*sideSign)
            else: subdivision = settings['sdv']

            #set the height of the block, it should be as high as the max corner position, minus grout
            height = c - blockGap*(0.5 + c/(width + blockGap))

            #the vertical offset for the short side of the block
            voff = sideSign * (blockHMin - height)
            xstart = holeW2
            zstart = z + sideSign * (h/2 + blockGap/2)
            woffset = width*(blockHMin + blockGap/2)/(c - blockGap/2)
            depth = blockDepth+(rndd()*blockDVar)

            if sideSign == 1:
                offsets = [[0]*3]*6 + [[0]*2 + [voff]]*2
                topSide = zstart+height
                btmSide = zstart
            else:
                offsets = [[0]*3]*4 + [[0]*2 + [voff]]*2 + [[0]*3]*2
                topSide = zstart
                btmSide = zstart-height

            pointsToAffect=(4,6) # left
            bevelBlockOffsets(offsets,bev,pointsToAffect)

            avlist,aflist = MakeABlock([x-xstart-width, x-xstart- woffset, btmSide, topSide, -depth/2, depth/2], subdivision, len(vlist), Offsets=offsets, xBevScl=1)

# top didn't use radialized in prev version; just noting for clarity - may need to revise for "sideSign == 1"
            if settings['Round']:
                for i,vert in enumerate(avlist): avlist[i] = [((vert[0]-x)/vert[2])+x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist

            if sideSign == 1:
                offsets = [[0]*3]*2 + [[0]*2 + [voff]]*2 + [[0]*3]*4
                topSide = zstart+height
                btmSide = zstart
            else:
                offsets = [[0]*2 + [voff]]*2 + [[0]*3]*6
                topSide = zstart
                btmSide = zstart-height

            pointsToAffect=(0,2) # right
            bevelBlockOffsets(offsets,bev,pointsToAffect)

            avlist,aflist = MakeABlock([x+xstart+woffset, x+xstart+width, btmSide, topSide, -depth/2, depth/2], subdivision, len(vlist), Offsets=offsets, xBevScl=1)

# top didn't use radialized in prev version; just noting for clarity - may need to revise for "sideSign == 1"
            if settings['Round']:
                for i,vert in enumerate(avlist): avlist[i] = [((vert[0]-x)/vert[2])+x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist
