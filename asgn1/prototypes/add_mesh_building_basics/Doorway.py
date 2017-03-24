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
Create an "Opening" framework (doorway), based on "Sove" from "SayPRODUCTIONS".
  Major revisions to UI and operations, may still be used for original design.
'''
# Author(s): Antonio Vazquez (antonioya), Jambay
#
# @todo: add door "position" to offset from jamb (front) or depth (back),
#  need to add door "base" if not in portal to complete door (all 4 sides),
#  also option to ignore arch as cover (no transom) - or just force.
# @todo: fix to allow use in Edit mode - once finalized in object mode, delete,
#  create another object (i.e. wall), switch to Edit mode, add again and object
#  will be in same location and grouped with first object.
# @todo: Knob add color options.
# @todo: Knob add finish "style" (shine, matte, etc).
#
################################################################################

import bpy
from bpy.props import BoolProperty,EnumProperty,FloatProperty,IntProperty,FloatVectorProperty
from bpy_extras.object_utils import object_data_add
import operator
from math import pi, sin, cos, sqrt, atan
from add_mesh_building_basics.UtilMats import uMatRGBSet
from add_mesh_building_basics.Door import *

# constants
PORTAL_MAX_XZ=30 # Max Blender units for portal width and height.
NOTCH_DFLT=0.30 # Common setting for notch V spacing.
DOOR_DF=0.08 # Initial door depth and frame inset.


################################################################################
#
#  UI functions and object creation.
#  Many UI defaults are set by "Style" - not menu item definition.
#
class addDoorway(bpy.types.Operator):
    bl_idname = "mesh.add_doorway"
    bl_label = "Doorway"
    bl_description = "Portal/Frame/Doorway"
    bl_options = {'REGISTER', 'UNDO'}

# @todo: Default and Arched are basically same now, revise settings, also
#  add "Window" Style (min portal, glass door with panels, etc...).
    Style = EnumProperty(items=(
        ('0',"Default","Portal only"),
        ("1","Arched","Arched portal and door"),
        ("2","Right pane",""),
        ("3","Split entry",""),
        ("4","Pizza Oven","")
        ),
        name="Style",description="Frame/portal style.")
    curStyle='firstUse' # programatic values/defaults, not property settings.
#    curStyle=Style # First use based on parameter defaults.

    portRGB=FloatVectorProperty(min=0,max=1,default=(1,1,1),subtype='COLOR',size=3)


    portX=FloatProperty(name='Width',min=0.01,max=PORTAL_MAX_XZ,default=4,precision=3,description='Frame inner/opening width')
    portZ=FloatProperty(name='Height',min=0.01,max=PORTAL_MAX_XZ,default=6,description='Height')
    caseW=FloatProperty(name='Struts',min=0.01,max=1,default=0.15,description='Casing side width.')
    portD=FloatProperty(name='Depth',min=0,max=1,default=0.20,description='Frame inner/opening depth')
    portS=FloatProperty(name='Sill',min=0.00,max=3.00,default=0.44,precision=3,description='Threshold/sill height')
    topMrgn=FloatProperty(name='Zmargin',min=0.01,max=3.0,default=0.33,description='Offset from top.')
    jambD=FloatProperty(name='Jamb',min=0.01,max=1,default=0.15,description='Jamb (portal face) depth forward')
    portA=BoolProperty(name='Arched',default=True,description='Arch portal')
    archZ=FloatProperty(name='',min=0.01,max=2,default=0.30,description='Arch height')
    archS=IntProperty(name='Segments',min=2,max=360,default=36,description='Arch segments, 2=center peak')

    archMode=EnumProperty(items =(
        ('1',"Difference",""),
        ('2',"Radius","")
        ),
        name="",description="Set panel arch curvature method.")

    archRad=IntProperty(name='',min=1,max=10000,default=30,description="Set panel arch radius range.") #Cap

    notchC=IntProperty(name='Notch',min=0,max=10,default=1,description='Horizontal cut-outs in frame.')
    notchZ=FloatProperty(name='Height',min=0.01,max=0.10,default=0.03,description='Notch height')
    notchD=FloatProperty(name='Depth',min=0.01,max=0.10,default=0.02,description='Notch depth')

    nZO0=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=0.90,description='Vertical offset from top/previous notch.')
    nZO1=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO2=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO3=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO4=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO5=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO6=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO7=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO8=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)
    nZO9=FloatProperty(min=0.01,max=PORTAL_MAX_XZ,default=NOTCH_DFLT)

    # door has no height or width, tracks with portal sizing.
    doorP=BoolProperty(name='Door',default=True,description='Create door')
    doorRGB=FloatVectorProperty(min=0,max=1,default=(0.5,0.5,0.5),subtype='COLOR',size=3)

    doorPD=bpy.props.FloatProperty(name='Depth',min=0.05,max=0.50,default=DOOR_DF,precision=2,description='Door depth')
    doorPI=bpy.props.FloatProperty(name='Indent',min=0.05,max=0.25,default=DOOR_DF,precision=2,description='Door frame size')
    doorPS=bpy.props.FloatProperty(name='Cleave',min=0.2,max=0.8,default=0.5,precision=3,description='Door split position')

    hingeL=BoolProperty(default=False,description="knob location")

    door2=BoolProperty(name='Split',default=False,description='Double door')

    doorKnob=bpy.props.EnumProperty(items=(
        ('0',"None",""),
        ('1',"Lever",""),
        ('2',"Diamond",""), # need better name... and should be Glass/transparent.
        ('3',"Rounded",""),
        ('4',"Bar","")
        ),
        name="Knob",default='1',description="Handle model")

    knobRGB=FloatVectorProperty(min=0,max=1,default=(0,0,0),subtype='COLOR',size=3)


# @todo: add Styles for sidelights.
    dcutP=BoolProperty(name='Sidelight',default=False,description='Door side pane')

    dcut2=bpy.props.EnumProperty(items=(
        ('1',"Right",""),
        ('2',"Left",""),
        ('3',"Both sides","")
        ),
        name="Side",description="Sets pane location")
    dcutW=FloatProperty(name='Width %',min=0.01,max=0.50,default=0.25,precision=3,description='Side pane width% of portal.')

    dPanC=IntProperty(name='Columns',min=1,max=5,default=1,description='Panel columns')
    pWO0=FloatProperty(min=0.01,max=1,default=1,description='Pane width - divided by number of columns.')
    pWO1=FloatProperty(min=0.01,max=1,default=1)
    pWO2=FloatProperty(min=0.01,max=1,default=1)
    pWO3=FloatProperty(min=0.01,max=1,default=1)
    pWO4=FloatProperty(min=0.01,max=1,default=1)

    dPanR=IntProperty(name='Rows',min=1,max=5,default=1,description='Panel rows')
    pZO0=FloatProperty(min=0.01,max=1,default=1,description='Pane height - divided by number of rows.')
    pZO1=FloatProperty(min=0.01,max=1,default=1)
    pZO2=FloatProperty(min=0.01,max=1,default=1)
    pZO3=FloatProperty(min=0.01,max=1,default=1)
    pZO4=FloatProperty(min=0.01,max=1,default=1)

    dPanG=bpy.props.FloatProperty(name='Gap',min=0.02,max=0.5,default=0.05,precision=2,description='Panel separation')

    dpanRGB=FloatVectorProperty(min=0,max=1,default=(0.1,0.05,0),subtype='COLOR',size=3)


    dPanTilt=BoolProperty(name='Slant',default=False,description='Incline door top, neg for left peak.')
    dpanAngle=IntProperty(min=-86,max=86,default=30)
    dPanTmatch=BoolProperty(name='Match',default=False,description='Match incline sides for additional panels.')

    #--------------------------------------------------------------
    def draw(self,context):
        layout = self.layout
        layout.prop(self,'Style')

        box=layout.box()
        box.prop(self,'portRGB',text='Color')

        box.prop(self,'portX')
        box.prop(self,'portZ')
        box.prop(self,'caseW')
        box.prop(self,'portS')
        box.prop(self,'topMrgn')

        row=box.row()
        row.prop(self,'jambD')
        row.prop(self,'portD')

        row=box.row()
        row.prop(self,'portA')
        if self.portA: # Arched portal, arched door.
            row.prop(self,'archZ')
            if self.doorP:
                row=box.row()
                row.prop(self,'archMode')

                if self.archMode=='2':
                    row.prop(self,'archRad')

                box.prop(self,'archS') # Arch segments, 2=center peak.

        box.prop(self,'notchC')
        if self.notchC:
            row=box.row()
            row.prop(self,'notchZ')
            row.prop(self,'notchD')
            for i in range(self.notchC):
                box.prop(self,'nZO'+str(i),text='Interval')

        box=layout.box()
        row=box.row()
        row.prop(self,'doorP')
        if self.doorP:
            row.prop(self,'door2') # split door
            if self.door2:
                box.prop(self,"doorPS")

            box.prop(self,'doorRGB',text='Color')

            box.prop(self,'doorPI')
            box.prop(self,'doorPD')

            box.prop(self,'dpanRGB',text='Color')

            box.prop(self,"dPanG")

            box.prop(self,'doorKnob')
            if self.doorKnob != '0':
                row=box.row()
                row.prop(self,'hingeL')
                row.prop(self,'knobRGB',text='')

            box.prop(self,"dPanC")
            for i in range(self.dPanC):
                box.prop(self,'pWO'+str(i),text='Width')

            box.prop(self,"dPanR")
            for i in range(self.dPanR):
                box.prop(self,'pZO'+str(i),text='Height')

            box.prop(self,'dcutP')
            if self.dcutP:
                box.prop(self,'dcut2')
                box.prop(self,'dcutW',slider=True)

            if not self.portA: # No slant if arched.
                row=box.row()
                row.prop(self,'dPanTilt')
                if self.dPanTilt:
                    # if split door or panel allow "match tilt" sides.
                    if self.dcutP or self.door2:
                        row.prop(self,'dPanTmatch')

                    box.prop(self,'dpanAngle',text='Angle')

    def execute(self,context):
        # validate UI setting limits, individual and relative to other parameters.
# @todo: fix - Invaild test for limit now that portX is "singular".
# @todo: need to check arch in bounds of portal overall height too.
#    if self.portA: # Arched?
#        if self.archZ>self.portX: # Arch cannot exceed width
#            self.archZ=self.portX

        if bpy.context.mode == "OBJECT":
            if self.curStyle!=self.Style: # only change for "new" style selection.
                self.curStyle=self.Style
                portalStyles(self,self.Style)

            add_portalObj(self,context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Option only valid in Object mode")
            return {'CANCELLED'}


################################################################################
#
# Set parameters for selected style - predefined designs.
#
#  All styles are based on default settings - they only set differences.
#   Use "Default" style to reset; this selection does not set every parameter.
#    Default style is not the same as parameter definition. First use/creation
#    will be different than selecting "Default" after modification.
#   Results will vary depending on previous style selection or manual changes.
#
# @todo: Create more styles.
#
def portalStyles(sRef,PortalStyle):

    if PortalStyle=='0': # set/reset (most) defaults
        sRef.portM='2'
        sRef.portX=4
        sRef.portZ=6
        sRef.caseW=0.15
        sRef.portS=0.44
        sRef.topMrgn=0.33
        sRef.jambD=0.15
        sRef.portD=0.20
        sRef.portA=False
        sRef.notchC=1
        sRef.notchZ=0.02
        sRef.notchD=0.03
        sRef.nZO0=0.90
        sRef.nZO1=NOTCH_DFLT
        sRef.nZO2=NOTCH_DFLT
        sRef.nZO3=NOTCH_DFLT
        sRef.nZO4=NOTCH_DFLT
        sRef.nZO5=NOTCH_DFLT
        sRef.nZO6=NOTCH_DFLT
        sRef.nZO7=NOTCH_DFLT
        sRef.nZO8=NOTCH_DFLT
        sRef.nZO9=NOTCH_DFLT
        sRef.doorP=True
        sRef.curMat='reset'
        sRef.door2=False
        sRef.hingeL=False
        sRef.doorPD=DOOR_DF
        sRef.doorPI=DOOR_DF
        sRef.doorPS=0.50
        sRef.dcutP=False
        sRef.doorKnob='1'

    if PortalStyle=='1': # Arched - no frills
        sRef.portA=True
#        sRef.archZ=0.30
        sRef.notchC=0
        sRef.doorP=True

    if PortalStyle=='2': # Right pane - no frills
        sRef.notchC=0
        sRef.doorP=True
        sRef.dcutP=True

    if PortalStyle=='3': # Split entry - no frills
        sRef.notchC=0
        sRef.doorP=True
        sRef.door2=True

    if PortalStyle=='4': # Pizza oven
        sRef.portX=1
        sRef.portZ=1
        sRef.portS=0.25
        sRef.topMrgn=0.25
        sRef.jambD=0.20
        sRef.portD=0.50
        sRef.portA=True
        sRef.archZ=0.25
        sRef.notchC = 0


################################################################################
#
def add_portalObj(sRef,context):
    # also, more efficient to use local variable than sRef.value
    workPortX=sRef.portX/2 # Portal is centered so split width.
    workArchZ=sRef.archZ*2 # Set scale for arch for portal width.

    fc=[];vr=[]

    portInner=-workPortX-sRef.caseW # Left side indent from frame.
    portOuter=workPortX+sRef.caseW
    portSill=sRef.portS
    portTopIn=sRef.portZ-sRef.topMrgn
    portJ=-sRef.jambD # (negative) offset forward from portal frame.

    vr.append([portInner,0,0])
    vr.append([portOuter,0,0])
    vr.append([portOuter,0,sRef.portZ])
    vr.append([portInner,0,sRef.portZ])
    vr.append([-workPortX,sRef.portD,portSill])
    vr.append([ workPortX,sRef.portD,portSill])
    vr.append([ workPortX,sRef.portD,portTopIn])
    vr.append([-workPortX,sRef.portD,portTopIn])
    vr.append([portInner,portJ,0])
    vr.append([portOuter,portJ,0])
    vr.append([portOuter,portJ,sRef.portZ])
    vr.append([portInner,portJ,sRef.portZ])
    vr.append([-workPortX,portJ,portSill])
    vr.append([ workPortX,portJ,portSill])
    vr.append([ workPortX,portJ,portTopIn])
    vr.append([-workPortX,portJ,portTopIn])

    fc.append([ 8, 0, 1, 9])
    fc.append([ 8, 9,13,12])
    fc.append([12,13, 5, 4])
    fc.append([11,10, 2, 3])

    if sRef.notchC: # nothches?
        fc.append([11,3,16,17]);fc.append([15,11,17,18]);fc.append([7,15,18,24])
        fc.append([25,19,14,6]);fc.append([19,20,10,14]);fc.append([20,21,2,10])
        ou=sRef.notchC*12
        fc.append([4,7,12+ou,24+ou]);fc.append([6,5,25+ou,13+ou])

        routerSteps=[sRef.nZO0,sRef.nZO1,sRef.nZO2,sRef.nZO3,sRef.nZO4,
            sRef.nZO5,sRef.nZO6,sRef.nZO7,sRef.nZO8,sRef.nZO9]

        add_Notches(sRef,vr,fc,routerSteps,sRef.notchC,portInner,portOuter)
    else:
        fc.append([0,8,11,3]);fc.append([8,12,15,11]);fc.append([12,4,7,15])
        fc.append([5,13,14,6]);fc.append([13,9,10,14]);fc.append([9,1,2,10])

    if not sRef.portA: # square/flat top
        fc.append([14,10,11,15]);fc.append([6,14,15,7])
    else: # Arched
        vr[6][2]-=workArchZ;vr[7][2]-=workArchZ;vr[14][2]-=workArchZ;vr[15][2]-=workArchZ
        O=workPortX/workArchZ
        H1=sqrt(((workPortX**2)+(workArchZ**2))/2)
# creates keyhole effect...
#        H1=sqrt(((workPortX**2)+(workArchZ**2))/4)
        H2=H1*O
        R=sqrt(((H1**2)+(H2**2))/2)
# creates keyhole effect...
#        R=sqrt(((H1**2)+(H2**2))/4)
        M=portTopIn-R
        A=pi-atan(O)*2

# what's with 1-24 fixed range?
        for a in range(1,24):
            p=(a*A/12)+(pi*1.5)-A
            vr.append([cos(p)*R,sRef.portD,M-sin(p)*R])
            vr.append([cos(p)*R,portJ,M-sin(p)*R])
            n=len(vr)
            if a==1:
                fc.append([n-1,15,7,n-2])
                fc.append([15,n-1,11])
            elif a<23:
                fc.append([n-1,n-3,n-4,n-2])
                if a<13:   fc.append([n-3,n-1,11])
                elif a==13:fc.append([n-3,n-1,10,11])
                else:      fc.append([n-3,n-1,10])
            elif a==23:
                fc.append([n-1,n-3,n-4,n-2])
                fc.append([n-3,n-1,10])
                fc.append([14,n-1,n-2,6])
                fc.append([n-1,14,10])

    portMesh = bpy.data.meshes.new(name='Doorway')
    portObj=bpy.data.objects.new('Doorway',portMesh)

    if sRef.doorP: # add door
        add_paneObj(sRef,context,portObj)

    portMesh.from_pydata(vr,[],fc)
    portMesh.materials.append(uMatRGBSet('Port_mat',sRef.portRGB,matMod=True))

    portMesh.update(calc_edges=True)
    object_data_add(context,portMesh,operator=None)

    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()


################################################################################
#
def add_Notches(sRef,vr,fc,routerSteps,routerCount,portInner,portOuter):

    workPortX=sRef.portX/2 # Portal is centered so split width.

    z=sRef.portZ
    portJ=-sRef.jambD # (negative) offset forward from portal frame.
    routerChalf=routerCount/2

    for i in range(routerCount):
        z-=routerSteps[i]

        vr.append([portInner,0,z]);vr.append([portInner,portJ,z])
        vr.append([-workPortX,portJ,z]);vr.append([workPortX,portJ,z])
        vr.append([portOuter,portJ,z]);vr.append([portOuter,0,z])
        vr.append([portInner+sRef.notchD,0,z])
        vr.append([portInner+sRef.notchD,portJ+sRef.notchD,z])
        vr.append([-workPortX,portJ+sRef.notchD,z])
        vr.append([workPortX,portJ+sRef.notchD,z])
        vr.append([portOuter-sRef.notchD,portJ+sRef.notchD,z])
        vr.append([portOuter-sRef.notchD,0,z])

        z-=sRef.notchZ
        vr.append([portInner,0,z]);vr.append([portInner,portJ,z])
        vr.append([-workPortX,portJ,z])
        vr.append([workPortX,portJ,z]);vr.append([portOuter,portJ,z])
        vr.append([portOuter,0,z])
        vr.append([portInner+sRef.notchD,0,z])
        vr.append([portInner+sRef.notchD,portJ+sRef.notchD,z])
        vr.append([-workPortX,portJ+sRef.notchD,z])
        vr.append([workPortX,portJ+sRef.notchD,z])
        vr.append([portOuter-sRef.notchD,portJ+sRef.notchD,z])
        vr.append([portOuter-sRef.notchD,0,z])

        n=len(vr)
        fc.append([n-1,n-2,n-8,n-7]);fc.append([n-3,n-9,n-8,n-2])
        fc.append([n-2,n-1,n-13,n-14]);fc.append([n-3,n-2,n-14,n-15])
        fc.append([n-15,n-14,n-20,n-21]);fc.append([n-14,n-13,n-19,n-20])
        fc.append([n-4,n-5,n-11,n-10]);fc.append([n-5,n-6,n-12,n-11])
        fc.append([n-5,n-4,n-16,n-17]);fc.append([n-6,n-5,n-17,n-18])
        fc.append([n-24,n-18,n-17,n-23]);fc.append([n-23,n-17,n-16,n-22])

        if routerCount>1:
            if routerCount%2==0:
                if i<routerChalf:fc.append([7,n-16,n-4]);fc.append([6,n-3,n-15])
                if i+1<routerChalf:fc.append([7,n- 4,n+8]);fc.append([6,n+9,n- 3])
                if i+1>routerChalf:fc.append([4,n-16,n-4]);fc.append([5,n-3,n-15])
                if i+1>routerChalf and i+1<routerCount:fc.append([4,n-4,n+8]);fc.append([5,n+9,n-3])
            else:
                if i<routerCount//2:
                    fc.append([7,n-16,n-4]);fc.append([6,n-3,n-15])
                    fc.append([7,n-4,n+8]);fc.append([6,n+9,n-3])
                if i>routerCount//2:fc.append([4,n-16,n-4]);fc.append([5,n-3,n-15])
                if i+1>routerCount//2 and i+1<routerCount:fc.append([4,n-4,n+8]);fc.append([5,n+9,n-3])

        if i<routerCount-1 and routerCount>1:
            fc.append([n-7,n-8,n+4,n+5]);fc.append([n-8,n-9,n+3,n+4]);fc.append([n-9,n-3,n+9,n+3])
            fc.append([n-10,n-11,n+1,n+2]);fc.append([n-11,n-12,n,n+1]);fc.append([n-4,n-10,n+2,n+8])

        if i==routerCount-1:
            fc.append([0,8,n-11,n-12]);fc.append([8,12,n-10,n-11]);fc.append([12,4,n-4,n-10])
            fc.append([5,13,n-9,n-3]);fc.append([13,9,n-8,n-9]);fc.append([9,1,n-7,n-8])
