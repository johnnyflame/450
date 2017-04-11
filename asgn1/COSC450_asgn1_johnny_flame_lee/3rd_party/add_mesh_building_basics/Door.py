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
Extracted from/based on "door_maker.py" functions from archimesh to
 create "doors", also merged add_mesh_building_objects Window.py,
 known as Window Generator 2.
'''
# Author(s): SayPRODUCTIONS, Jambay
#
# @todo: fix "faces" for door.
#
# Wish list:
#  Sliding doors.
#  Louvered panels - see Stair Builder for base source (slanted stairs).
#  Glass material with "transparency" setting.
#
#  Knobs:
#   Handles appear on front and back of door, need to make that an option?
#    either none or different style for "sets".
#   Left or right only when split for single door action.
#   Horizontal option for "bar" shaped handle.
#   Predefined collection of knob "sets" (front/back, and locks).
#   doc note: Rosette = plate behind handle.
#
################################################################################

import bpy
from math import pi, sin, cos, sqrt, radians
from add_mesh_building_basics.UtilMats import uMatRGBSet
from add_mesh_building_basics.Knobs import *

# constants
DEFK=False # disable gap modifier for panels


################################################################################
#
# Generate "door" object.
#
# @todo: account for door depth (doorPD).
#
def add_paneObj(sRef,context,panelP):
    doorGap=0.002
    paneB=sRef.portS # Bottom efficiency reference.
    paneZ=sRef.portZ-sRef.topMrgn-paneB
    paneW=sRef.portX
    paneInd=0.0 # Sidelight offset.
    paneLoc=0.0 # Sidelight positioning.

    dMatRGB=sRef.doorRGB

    if sRef.dcutP: # sidelights...
        paneInd=paneW*sRef.dcutW
        paneW-=paneInd

        # set indent for pane location
        if sRef.dcut2 == '1': # right
            paneLoc=-paneInd

            # Create pane
            dPanes=create_panes(sRef,context,paneInd,paneZ,doorPan=False,revTilt=True)
            dPanes.parent=panelP

            dPanes.location.x+=paneW/2 # adjust for door.
            dPanes.location.z+=paneB # set base for portal "sill".

            myDoor=make_panel(sRef,context,dPanes,doorGap,paneInd,paneZ,dKnob=False)

# @todo: customize/separate pane material.
            # color pane - also used for door.
            myDoor.data.materials.append(uMatRGBSet('Door_mat',dMatRGB,matMod=True))
        elif sRef.dcut2 == '2': # left
            paneLoc=paneInd

            # Create pane
            dPanes=create_panes(sRef,context,paneInd,paneZ,doorPan=False,revTilt=True)
            dPanes.parent=panelP

            dPanes.location.x-=paneW/2 # adjust for door.
            dPanes.location.z+=paneB # set base for portal "sill".

            myDoor=make_panel(sRef,context,dPanes,doorGap,paneInd,paneZ,dKnob=False)

# @todo: customize/separate pane material.
            # color pane - also used for door.
            myDoor.data.materials.append(uMatRGBSet('Door_mat',dMatRGB,matMod=True))
        else: # both sides
            # Create left pane
            dPanes=create_panes(sRef,context,paneInd/2,paneZ,doorPan=False,revTilt=True)
            dPanes.parent=panelP

            dPanes.location.x-=((paneW+(paneInd/2))/2) # adjust for door.
            dPanes.location.z+=paneB # set base for portal "sill".

            myDoor=make_panel(sRef,context,dPanes,doorGap,paneInd/2,paneZ,dKnob=False)

# @todo: customize/separate pane material.
            # color pane - also used for door.
            myDoor.data.materials.append(uMatRGBSet('Door_mat',dMatRGB,matMod=True))

            # Create right pane
            dPanes=create_panes(sRef,context,paneInd/2,paneZ,doorPan=False,revTilt=False)
            dPanes.parent=panelP

            dPanes.location.x+=((paneW+(paneInd/2))/2) # adjust for door.
            dPanes.location.z+=paneB # set base for portal "sill".

            myDoor=make_panel(sRef,context,dPanes,doorGap,paneInd/2,paneZ,dKnob=False)

# @todo: customize/separate pane material.
            # color pane - also used for door.
            myDoor.data.materials.append(uMatRGBSet('Door_mat',dMatRGB,matMod=True))

    if sRef.door2: # split door?
# @todo: account for door gap (doorGap).
        widthL=paneW*sRef.doorPS
        widthR=paneW-widthL

        # left pane
        dPanes=create_panes(sRef,context,widthL-(doorGap*2),paneZ)
        dPanes.parent=panelP

        # set positioning for sidelights...
        if sRef.dcutP and sRef.dcut2 == '1': # right pane
            dPanes.location.x-=((widthR/2)+(paneInd/2))
        elif sRef.dcutP and sRef.dcut2 == '2': # left pane
            dPanes.location.x-=((widthR/2)-(paneInd/2))
        else: # simple split, sRef.dcutP already accounted for.
            dPanes.location.x-=(widthR/2)

        dPanes.location.z+=paneB # set base for portal "sill".

        myDoor=make_panel(sRef,context,dPanes,doorGap,widthL,paneZ,True)

        # color door - also used for right door.
        myDoor.data.materials.append(uMatRGBSet('Door_mat',dMatRGB,matMod=True))

        # right pane
        # a bit convoluded, but saves redundant code to work out for slant...
        rPaneTilt=True
# fixes pane but breaks door...
#        if sRef.dcutP and sRef.dcut2 == '1': # right pane
#            rPaneTilt=False

        dPanes=create_panes(sRef,context,widthR-(doorGap*2),paneZ,revTilt=rPaneTilt)
        dPanes.parent=panelP

        # set positioning for sidelights...
        if sRef.dcutP and sRef.dcut2 == '1': # right pane
            dPanes.location.x+=((widthL/2)-(paneInd/2))
        elif sRef.dcutP and sRef.dcut2 == '2': # left pane
            dPanes.location.x+=((widthL/2)+(paneInd/2))
        else: # simple split, cut already accounted for.
            dPanes.location.x+=(widthL/2)

        dPanes.location.z+=paneB # set base for portal "sill".

        myDoor=make_panel(sRef,context,dPanes,doorGap,widthR,paneZ)
    else: # single
        dPanes=create_panes(sRef,context,paneW-(doorGap*2),paneZ)
        dPanes.parent=panelP

        dPanes.location.x+=paneLoc/2 # adjusted for sidelights.
        dPanes.location.z+=paneB # set door base for portal "sill".

        myDoor=make_panel(sRef,context,dPanes,doorGap,paneW,paneZ)

    # color door
    myDoor.data.materials.append(uMatRGBSet('Door_mat',dMatRGB,matMod=True))

    panelP.select=True
    bpy.context.scene.objects.active=panelP


################################################################################
#
# Create door panel.
#
def make_panel(sRef,context,dParent,dGap,width,height,splitL=False,dKnob=True):
    wf=width-(dGap*2)
    pz=height/2
    deep = sRef.doorPD/2-(dGap*3)

    # works for single or double doors.
    if sRef.hingeL or splitL: # Open to left?
        hinge=True
        side=-1
        minX=0.0
        maxX=width
    else: # right
        hinge=False
        side=1
        minX=-width
        maxX=0.0

    minY=0.0 # locked
    maxY=deep
    minZ=-pz
    maxZ=pz-sRef.doorPI

    verts = [
        (minX,minY,minZ),(minX,maxY,minZ),
        (maxX,maxY,minZ),(maxX,minY,minZ),
        (minX,minY,maxZ),(minX,maxY,maxZ),
        (maxX,maxY,maxZ),(maxX,minY,maxZ)
        ]

    faces = [(4, 5, 1, 0),(5, 6, 2, 1),(6, 7, 3, 2),(7, 4, 0, 3),(0, 1, 2, 3),(7, 6, 5, 4)]

    doorMesh=bpy.data.meshes.new("Door")
    doorObj=bpy.data.objects.new("Door",doorMesh)

    doorObj.location=bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(doorObj)

    doorMesh.from_pydata(verts,[],faces)
    doorMesh.update(calc_edges=True)

    # Translate to doorframe and parent
    doorObj.parent=dParent
    doorObj.location.x=((wf*side)/2)
    doorObj.location.y=-(deep * 0.65)
    doorObj.location.z=height/2

    if dKnob and sRef.doorKnob != "0":
        handle1 = create_handle(sRef,context,0,wf,hinge)
        handle1.parent=doorObj
        handle1.select = True
        bpy.context.scene.objects.active = handle1
#        set_smooth(handle1)
#        set_modifier_subsurf(handle1)
        handle2 = create_handle(sRef,context,1,wf,hinge)
        handle2.parent=doorObj
#        set_smooth(handle2)
#        set_modifier_subsurf(handle2)

    return doorObj


################################################################################
#
# pane top shapes
#
def Fitil(vr,fc,X,Z,x,y,z,zz,xx):
    k3=z*2
    vr.extend([[X[x  ]+xx,-z+zz,Z[y  ]+xx],[X[x  ]+xx+k3,-z+zz,Z[y  ]+xx+k3],[X[x  ]+xx+k3,z+zz,Z[y  ]+xx+k3],[X[x  ]+xx,z+zz,Z[y  ]+xx]])
    vr.extend([[X[x  ]+xx,-z+zz,Z[y+1]-xx],[X[x  ]+xx+k3,-z+zz,Z[y+1]-xx-k3],[X[x  ]+xx+k3,z+zz,Z[y+1]-xx-k3],[X[x  ]+xx,z+zz,Z[y+1]-xx]])
    vr.extend([[X[x+1]-xx,-z+zz,Z[y+1]-xx],[X[x+1]-xx-k3,-z+zz,Z[y+1]-xx-k3],[X[x+1]-xx-k3,z+zz,Z[y+1]-xx-k3],[X[x+1]-xx,z+zz,Z[y+1]-xx]])
    vr.extend([[X[x+1]-xx,-z+zz,Z[y  ]+xx],[X[x+1]-xx-k3,-z+zz,Z[y  ]+xx+k3],[X[x+1]-xx-k3,z+zz,Z[y  ]+xx+k3],[X[x+1]-xx,z+zz,Z[y  ]+xx]])

    n=len(vr)
    fc.extend([[n-16,n-15,n-11,n-12],[n-15,n-14,n-10,n-11],[n-14,n-13,n- 9,n-10]])
    fc.extend([[n-12,n-11,n- 7,n- 8],[n-11,n-10,n- 6,n- 7],[n-10,n- 9,n- 5,n- 6]])
    fc.extend([[n- 8,n- 7,n- 3,n- 4],[n- 7,n- 6,n- 2,n- 3],[n- 6,n- 5,n- 1,n- 2]])
    fc.extend([[n- 4,n- 3,n-15,n-16],[n- 3,n- 2,n-14,n-15],[n- 2,n- 1,n-13,n-14]])

    z=0.005
    vr.extend([[X[x]+xx+k3,-z+zz,Z[y]+xx+k3],[X[x]+xx+k3,-z+zz,Z[y+1]-xx-k3],[X[x+1]-xx-k3,-z+zz,Z[y+1]-xx-k3],[X[x+1]-xx-k3,-z+zz,Z[y]+xx+k3]])
    vr.extend([[X[x]+xx+k3, z+zz,Z[y]+xx+k3],[X[x]+xx+k3, z+zz,Z[y+1]-xx-k3],[X[x+1]-xx-k3, z+zz,Z[y+1]-xx-k3],[X[x+1]-xx-k3, z+zz,Z[y]+xx+k3]])
    fc.extend([[n+1,n+0,n+3,n+2],[n+4,n+5,n+6,n+7]])

def Kapak(vr,fc,X,Z,x,y,z,zz):
    k2=z*2
    vr.extend([[X[x  ],-z+zz,Z[y  ]],[X[x  ]+k2,-z+zz,Z[y  ]+k2],[X[x  ]+k2,z+zz,Z[y  ]+k2],[X[x  ],z+zz,Z[y  ]]])
    vr.extend([[X[x  ],-z+zz,Z[y+1]],[X[x  ]+k2,-z+zz,Z[y+1]-k2],[X[x  ]+k2,z+zz,Z[y+1]-k2],[X[x  ],z+zz,Z[y+1]]])
    vr.extend([[X[x+1],-z+zz,Z[y+1]],[X[x+1]-k2,-z+zz,Z[y+1]-k2],[X[x+1]-k2,z+zz,Z[y+1]-k2],[X[x+1],z+zz,Z[y+1]]])
    vr.extend([[X[x+1],-z+zz,Z[y  ]],[X[x+1]-k2,-z+zz,Z[y  ]+k2],[X[x+1]-k2,z+zz,Z[y  ]+k2],[X[x+1],z+zz,Z[y  ]]])

    n=len(vr)
    fc.extend([[n-16,n-15,n-11,n-12],[n-15,n-14,n-10,n-11],[n-14,n-13,n- 9,n-10],[n-13,n-16,n-12,n- 9]])
    fc.extend([[n-12,n-11,n- 7,n- 8],[n-11,n-10,n- 6,n- 7],[n-10,n- 9,n- 5,n- 6],[n- 9,n-12,n- 8,n- 5]])
    fc.extend([[n- 8,n- 7,n- 3,n- 4],[n- 7,n- 6,n- 2,n- 3],[n- 6,n- 5,n- 1,n- 2],[n- 5,n- 8,n- 4,n- 1]])
    fc.extend([[n- 4,n- 3,n-15,n-16],[n- 3,n- 2,n-14,n-15],[n- 2,n- 1,n-13,n-14],[n- 1,n- 4,n-16,n-13]])


################################################################################
#
def create_panes(sRef,context,width,height,doorPan=True,revTilt=False):
    fc=[];vr=[];kx=[]

    if not sRef.dPanTmatch: # all the same peak side.
        revTilt=False

    k1=sRef.doorPI
    if doorPan:
        panCols=sRef.dPanC
    else:
        panCols=1

    colWMod=(width-(k1*2))/panCols

    if doorPan:
        panRows=sRef.dPanR
    else:
        panRows=1

    rowZMod=(height-(k1*2))/panRows # track to top.

    if panCols > 1 or panRows > 1:
        panGap=sRef.dPanG
    else:
        panGap=0.0

    k2=panGap # space between panels
    k2C=panGap/panCols # adjust gap by number of columns
    k2R=panGap/panRows # adjust gap by number of rows
    k3=0.0 # panel inner frame
    RES=sRef.archS

    u=k1
    X=[0,round(u,2)]

    # set panels for columns
    u+=sRef.pWO0*colWMod
    X.append(round(u,2))

    u+=k2C
    X.append(round(u,2))

    if panCols>1:u+=(sRef.pWO1-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))
    if panCols>2:u+=(sRef.pWO2-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))
    if panCols>3:u+=(sRef.pWO3-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))
    if panCols>4:u+=(sRef.pWO4-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))
#    if panCols>5:u+=(sRef.pWO5-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))
#    if panCols>6:u+=(sRef.pWO6-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))
#    if panCols>7:u+=(sRef.pWO7-k2C)*colWMod;X.append(round(u,2));u+=k2C;X.append(round(u,2))

    X[-1]=X[-2]+k1

    u=k1
    Z=[0,round(u,2)]

    # set panels for rows
    u+=sRef.pZO0*rowZMod

    Z.append(round(u,2))

    u+=k2R
    Z.append(round(u,2))

    if panRows> 1:u+=(sRef.pZO1-k2R)*rowZMod;Z.append(round(u,2));u+=k2R;Z.append(round(u,2))
    if panRows> 2:u+=(sRef.pZO2-k2R)*rowZMod;Z.append(round(u,2));u+=k2R;Z.append(round(u,2))
    if panRows> 3:u+=(sRef.pZO3-k2R)*rowZMod;Z.append(round(u,2));u+=k2R;Z.append(round(u,2))
    if panRows> 4:u+=(sRef.pZO4-k2R)*rowZMod;Z.append(round(u,2));u+=k2R;Z.append(round(u,2))

    Z[-1]=Z[-2]+k1
    u = X[-1]/2
    for i in range(0,len(X)):X[i]-=u

    # gap modifier for each column and row - True/False flag.
    kx=[[DEFK,DEFK,DEFK,DEFK,DEFK],
        [DEFK,DEFK,DEFK,DEFK,DEFK],
        [DEFK,DEFK,DEFK,DEFK,DEFK],
        [DEFK,DEFK,DEFK,DEFK,DEFK],
# only 5 rows at present...
#        [DEFK,DEFK,DEFK,DEFK,DEFK],
#        [DEFK,DEFK,DEFK,DEFK,DEFK],
#        [DEFK,DEFK,DEFK,DEFK,DEFK],
        [DEFK,DEFK,DEFK,DEFK,DEFK]]

#    kx=[[sRef.k00,sRef.k10,sRef.k20,sRef.k30,sRef.k40],
#        [sRef.k01,sRef.k11,sRef.k21,sRef.k31,sRef.k41],
#        [sRef.k02,sRef.k12,sRef.k22,sRef.k32,sRef.k42],
#        [sRef.k03,sRef.k13,sRef.k23,sRef.k33,sRef.k43],
#        [sRef.k04,sRef.k14,sRef.k24,sRef.k34,sRef.k44],
#        [sRef.k05,sRef.k15,sRef.k25,sRef.k35,sRef.k45],
#        [sRef.k06,sRef.k16,sRef.k26,sRef.k36,sRef.k46],
#        [sRef.k07,sRef.k17,sRef.k27,sRef.k37,sRef.k47]]

    cam=[];mer=[];ftl=[];SM=[]
#VERTICES ------------------------
    vr.extend([[X[0],-k1/2,Z[0]],[X[0],k1/2,Z[0]]])
    for x in range(1,len(X)-1):vr.extend([[X[x],-k1/2,Z[1]],[X[x], k1/2,Z[1]]])
    vr.extend([[X[-1],-k1/2,Z[0]],[X[-1], k1/2,Z[0]]])
    for z in range(2,len(Z)-2,2):
        for x in range(0,len(X)):vr.extend([[X[x],-k1/2,Z[z]],[X[x], k1/2,Z[z]]])
        for x in range(0,len(X)):vr.extend([[X[x],-k1/2,Z[z+1]],[X[x], k1/2,Z[z+1]]])

    z=len(Z)-2
    vr.extend([[X[0],-k1/2,Z[z+1]],[X[0], k1/2,Z[z+1]]])
    ALT=[];UST=[len(vr)-2,len(vr)-1]

    for x in range(1,len(X)-1):
        vr.extend([[X[x],-k1/2,Z[z]],[X[x], k1/2,Z[z]]])
        ALT.extend([len(vr)-2,len(vr)-1])

    vr.extend([[X[-1],-k1/2,Z[z+1]],[X[-1],k1/2,Z[z+1]]])
    SON=[len(vr)-2,len(vr)-1]

#FACES ---------------------------
    fc.append([0,1,3+panCols*4,2+panCols*4])
    FB=[0];FR=[1]

    for i in range(0,panCols*4,4):
        fc.append([i+3,i+2,i+4,i+5])
        FB.extend([i+2,i+4])
        FR.extend([i+3,i+5])

    FR.append(3+panCols*4);FB.append(2+panCols*4)
    FB.reverse()
    fc.extend([FB,FR])

    #Yatay
    Y=(panCols*4+4);V=panCols*4+2

    for z in range(0,(panRows-1)*Y*2,Y*2):
        fc.extend([[z+Y+1,z+Y,z+Y+4+panCols*4,z+Y+5+panCols*4],[z+Y+V,z+Y+V+1,z+Y+V+5+panCols*4,z+Y+V+4+panCols*4]])

        for i in range(0,panCols*4+2,2):
            fc.extend([[z+i+Y+0,z+i+Y+2,z+i+Y+V+4,z+i+Y+V+2],[z+i+Y  +3,z+i+Y  +1,z+i+Y+V+3,z+i+Y+V+5]])
        for i in range(0,panCols*4-3,4):
            fc.extend([[z+i+Y+2,z+i+Y+3,z+i+Y  +5,z+i+Y  +4],[z+i+Y+V+5,z+i+Y+V+4,z+i+Y+V+6,z+i+Y+V+7]])

    #Dikey
    for Y in range(0,panRows):
        z=Y*(panCols*4+4)*2
        for i in range(0,panCols*4+2,4):
            fc.extend([[z+i+1,z+i+0,z+i+V+2,z+i+V+3],[z+i+3,z+i+1,z+i+V+3,z+i+V+5],
            [z+i+2,z+i+3,z+i+V+5,z+i+V+4],[z+i+0,z+i+2,z+i+V+4,z+i+V+2]])

    #Fitil-------------------
    if not sRef.portA and not sRef.dPanTilt:
        y1=panRows
    else:
        y1=panRows-1

    for y in range(0,y1):
        for x in range(0,panCols):
            if  kx[x][y]==True:
                Kapak(vr,fc,X,Z,x*2+1,y*2+1,k2C/2,(k1+k2C)*0.5-0.01)
                Fitil(vr,fc,X,Z,x*2+1,y*2+1,k3,(k1+k2C)*0.5-0.01,k2C)
            else:
                Fitil(vr,fc,X,Z,x*2+1,y*2+1,k3,0,0)
            m=len(fc);cam.extend([m-1,m-2])
            ftl.extend([m-3,m-4,m-5,m-6,m-7,m-8,m-9,m-10,m-11,m-12,m-13,m-14])

    #-----------------------------------------------------
    # Check for arched first so portal setting is primary.
# should probably set "u" value to ensure previous/last usage proper for archMode.
    if sRef.portA:# Arched/Yay
        if   sRef.archMode=='1': # "Difference"
            archH=sRef.archZ
            archSqr=sqrt(u**2+archH**2)/2
            e=archSqr*(u/archH)
            archC=sqrt(archSqr**2+e**2)
            T1=Z[-1]-archH
        else: # "Radius"
            archC=sRef.archRad/100
            if archC<u+0.01: # limit radius minmum to height
                archC=u+0.01
                sRef.archRad=archC*100
            T1=sqrt(archC**2-u**2)+Z[-1]-archC

        R=archC-k1;F=R-k3*2
        K=R-k2;E=K-k3*2
        z=Z[-1]-archC

        vr[UST[0]][2]=T1;vr[UST[1]][2]=T1
        vr[SON[0]][2]=T1;vr[SON[1]][2]=T1
# get python error (sometimes) when split...
#  doorPI and not enough "room" for other options!!! 
        for i in ALT:vr[i][2]=sqrt(R**2-vr[i][0]**2)+z

        ON=[SON[0]];U1=[]
        for i in range(0,RES):
            A=i*pi/RES;x=cos(A)*archC
            if  x>-u and x<u:
                vr.append([x,-k1/2,sin(A)*archC+z]);ON.append(len(vr)-1)

        U1.extend(ON);U1.append(UST[0])
        ON.extend([UST[0],ALT[0]])
        AR=[];D1=[];D2=[]

        for i in range(0,len(ALT)-2,4):
            x1=vr[ALT[i+0]][0]; x2=vr[ALT[i+2]][0]
            ON.append(ALT[i+0]);AR.append(ALT[i+1])
            T1=[ALT[i+0]];      T2=[ALT[i+1]]
            for j in range(0,RES):
                A=j*pi/RES;x=-cos(A)*R
                if  x1<x and x<x2:
                    vr.extend([[x,-k1/2,sin(A)*R+z],[x,k1/2,sin(A)*R+z]])
                    ON.append(len(vr)-2);AR.append(len(vr)-1)
                    T1.append(len(vr)-2);T2.append(len(vr)-1)
            ON.append(ALT[i+2]);AR.append(ALT[i+3])
            T1.append(ALT[i+2]);T2.append(ALT[i+3])
            D1.append(T1);      D2.append(T2)

        AR.append(SON[1])
        U2=[SON[1]]

        for i in range(0,RES):
            A=i*pi/RES;x=cos(A)*archC
            if  x>-u and x<u:
                vr.append([x,k1/2,sin(A)*archC+z])
                AR.append(len(vr)-1);U2.append(len(vr)-1)

        AR.append(UST[1])
        U2.append(UST[1])
        AR.reverse()
        fc.extend([ON,AR])

        for i in range(0,len(U1)-1):fc.append([U1[i+1],U1[i],U2[i],U2[i+1]]);SM.append(len(fc)-1)

        for A in range(0,panCols):
            for i in range(0,len(D1[A])-1):
                fc.append([D1[A][i+1],D1[A][i],D2[A][i],D2[A][i+1]]);SM.append(len(fc)-1)

        y=panRows-1
        for x in range(0,panCols):
            if  kx[x][y]==True:
                fr=(k1+k2C)*0.5-0.01;ek=k2C
                R=archC-k1;K=R-k2C

                x1=X[x*2+1];x2=X[x*2+2]
                vr.extend([[x2,fr-k2C/2,z+1  ],[x2-k2C,fr-k2C/2,z+1     ],[x2-k2C,fr+k2C/2,z+1     ],[x2,fr+k2C/2,z+1  ]])
                vr.extend([[x2,fr-k2C/2,Z[-3]],[x2-k2C,fr-k2C/2,Z[-3]+k2C],[x2-k2C,fr+k2C/2,Z[-3]+k2C],[x2,fr+k2C/2,Z[-3]]])
                vr.extend([[x1,fr-k2C/2,Z[-3]],[x1+k2C,fr-k2C/2,Z[-3]+k2C],[x1+k2C,fr+k2C/2,Z[-3]+k2C],[x1,fr+k2C/2,Z[-3]]])
                vr.extend([[x1,fr-k2C/2,z+1  ],[x1+k2C,fr-k2C/2,z+1     ],[x1+k2C,fr+k2C/2,z+1     ],[x1,fr+k2C/2,z+1  ]])

                n=len(vr)
                fc.extend([[n-16,n-15,n-11,n-12],[n-15,n-14,n-10,n-11],[n-14,n-13,n- 9,n-10],[n-13,n-16,n-12,n- 9]])
                fc.extend([[n-12,n-11,n- 7,n- 8],[n-11,n-10,n- 6,n- 7],[n-10,n- 9,n- 5,n- 6],[n- 9,n-12,n- 8,n- 5]])
                fc.extend([[n- 8,n- 7,n- 3,n- 4],[n- 7,n- 6,n- 2,n- 3],[n- 6,n- 5,n- 1,n- 2],[n- 5,n- 8,n- 4,n- 1]])
                ALT=[n-16,n-15,n-14,n-13,n-4,n-3,n-2,n-1]
                vr[ALT[0]][2]=sqrt(R**2-vr[ALT[0]][0]**2)+z;vr[ALT[1]][2]=sqrt(K**2-vr[ALT[1]][0]**2)+z
                vr[ALT[2]][2]=sqrt(K**2-vr[ALT[2]][0]**2)+z;vr[ALT[3]][2]=sqrt(R**2-vr[ALT[3]][0]**2)+z
                vr[ALT[4]][2]=sqrt(R**2-vr[ALT[4]][0]**2)+z;vr[ALT[5]][2]=sqrt(K**2-vr[ALT[5]][0]**2)+z
                vr[ALT[6]][2]=sqrt(K**2-vr[ALT[6]][0]**2)+z;vr[ALT[7]][2]=sqrt(R**2-vr[ALT[7]][0]**2)+z

                D1=[];D2=[];T1=[];T2=[]
                for i in range(0,RES):
                    A =i*pi/RES;y1=cos(A)*R;y2=-cos(A)*K
                    if x1   <y1 and y1<x2:   vr.extend([[y1,fr-k2/2,sin(A)*R+z],[y1,fr+k2/2,sin(A)*R+z]]);T1.append(len(vr)-2);T2.append(len(vr)-1)
                    if x1+k2<y2 and y2<x2-k2:vr.extend([[y2,fr-k2/2,sin(A)*K+z],[y2,fr+k2/2,sin(A)*K+z]]);D1.append(len(vr)-2);D2.append(len(vr)-1)
                ON=[ALT[1],ALT[0]];ON.extend(T1);ON.extend([ALT[4],ALT[5]]);ON.extend(D1)
                AR=[ALT[2],ALT[3]];AR.extend(T2);AR.extend([ALT[7],ALT[6]]);AR.extend(D2);AR.reverse()

                if   D1==[] and T1==[]:fc.extend([ON,AR,[ALT[5],ALT[6],ALT[2],ALT[1]],[ALT[7],ALT[4],ALT[0],ALT[3]]]);                                                        m=len(fc);SM.extend([m-1,m-2])
                elif D1==[] and T1!=[]:fc.extend([ON,AR,[ALT[5],ALT[6],ALT[2],ALT[1]],[ALT[7],ALT[4],T1[-1],T2[-1]],[ALT[0],ALT[3],T2[0],T1[0]]]);                            m=len(fc);SM.extend([m-1,m-2,m-3])
                elif D1!=[] and T1==[]:fc.extend([ON,AR,[ALT[5],ALT[6],D2[0],D1[0]],[ALT[2],ALT[1],D1[-1],D2[-1]],[ALT[7],ALT[4],ALT[0],ALT[3]]]);                            m=len(fc);SM.extend([m-1,m-2,m-3])
                else:                  fc.extend([ON,AR,[ALT[5],ALT[6],D2[0],D1[0]],[ALT[2],ALT[1],D1[-1],D2[-1]],[ALT[7],ALT[4],T1[-1],T2[-1]],[ALT[0],ALT[3],T2[0],T1[0]]]);m=len(fc);SM.extend([m-1,m-2,m-3,m-4])

                for i in range(0,len(D1)-1):fc.append([D1[i+1],D1[i],D2[i],D2[i+1]]);SM.append(len(fc)-1)
                for i in range(0,len(T1)-1):fc.append([T1[i+1],T1[i],T2[i],T2[i+1]]);SM.append(len(fc)-1)
                R=archC-k1-k2;K=R-k3*2
            else:
                fr=0;ek=0
                R=archC-k1;K=R-k3*2

            #Fitil
            x1=X[x*2+1]+ek;x2=X[x*2+2]-ek
            vr.extend([[x2,fr-k3,z+1     ],[x2-k3*2,fr-k3,z+1          ],[x2-k3*2,fr+k3,z+1          ],[x2,fr+k3,z+1     ]])
            vr.extend([[x2,fr-k3,Z[-3]+ek],[x2-k3*2,fr-k3,Z[-3]+ek+k3*2],[x2-k3*2,fr+k3,Z[-3]+ek+k3*2],[x2,fr+k3,Z[-3]+ek]])
            vr.extend([[x1,fr-k3,Z[-3]+ek],[x1+k3*2,fr-k3,Z[-3]+ek+k3*2],[x1+k3*2,fr+k3,Z[-3]+ek+k3*2],[x1,fr+k3,Z[-3]+ek]])
            vr.extend([[x1,fr-k3,z+1     ],[x1+k3*2,fr-k3,z+1          ],[x1+k3*2,fr+k3,z+1          ],[x1,fr+k3,z+1     ]])

            n=len(vr)
            fc.extend([[n-16,n-15,n-11,n-12],[n-15,n-14,n-10,n-11],[n-14,n-13,n- 9,n-10]])
            fc.extend([[n-12,n-11,n- 7,n- 8],[n-11,n-10,n- 6,n- 7],[n-10,n- 9,n- 5,n- 6]])
            fc.extend([[n- 8,n- 7,n- 3,n- 4],[n- 7,n- 6,n- 2,n- 3],[n- 6,n- 5,n- 1,n- 2]])

            m=len(fc);ftl.extend([m-1,m-2,m-3,m-4,m-5,m-6,m-7,m-8,m-9])

            ALT=[n-16,n-15,n-14,n-13,n-4,n-3,n-2,n-1]
            vr[ALT[0]][2]=sqrt(R**2-vr[ALT[0]][0]**2)+z;vr[ALT[1]][2]=sqrt(K**2-vr[ALT[1]][0]**2)+z
            vr[ALT[2]][2]=sqrt(K**2-vr[ALT[2]][0]**2)+z;vr[ALT[3]][2]=sqrt(R**2-vr[ALT[3]][0]**2)+z
            vr[ALT[4]][2]=sqrt(R**2-vr[ALT[4]][0]**2)+z;vr[ALT[5]][2]=sqrt(K**2-vr[ALT[5]][0]**2)+z
            vr[ALT[6]][2]=sqrt(K**2-vr[ALT[6]][0]**2)+z;vr[ALT[7]][2]=sqrt(R**2-vr[ALT[7]][0]**2)+z

            D1=[];D2=[];T1=[];T2=[]
            for i in range(0,RES):
                A =i*pi/RES;y1=cos(A)*R;y2=-cos(A)*K
                if x1     <y1 and y1<x2:     vr.extend([[y1,fr-k3,sin(A)*R+z],[y1,fr+k3,sin(A)*R+z]]);T1.append(len(vr)-2);T2.append(len(vr)-1);ftl.extend([len(fc)-1,len(fc)-2])
                if x1+k3*2<y2 and y2<x2-k3*2:vr.extend([[y2,fr-k3,sin(A)*K+z],[y2,fr+k3,sin(A)*K+z]]);D1.append(len(vr)-2);D2.append(len(vr)-1);ftl.extend([len(fc)-1,len(fc)-2])

            ON=[ALT[1],ALT[0]];ON.extend(T1);ON.extend([ALT[4],ALT[5]]);ON.extend(D1)
            AR=[ALT[2],ALT[3]];AR.extend(T2);AR.extend([ALT[7],ALT[6]]);AR.extend(D2);AR.reverse()

            if D1==[]:
                fc.extend([ON,AR,[ALT[5],ALT[6],ALT[2],ALT[1]]])
                m=len(fc);ftl.extend([m-1,m-2,m-3]);SM.extend([m-1])
            else:
                fc.extend([ON,AR,[ALT[5],ALT[6],D2[0],D1[0]],[ALT[2],ALT[1],D1[-1],D2[-1]]]);m=len(fc);ftl.extend([m-1,m-2,m-3,m-4]);SM.extend([m-1,m-2])

            for i in range(0,len(D1)-1):fc.append([D1[i+1],D1[i],D2[i],D2[i+1]]);ftl.append(len(fc)-1);SM.append(len(fc)-1)

            #Cam
            x1=X[x*2+1]+ek+k3*2;x2=X[x*2+2]-ek-k3*2
            ON=[];AR=[]

            for i in range(0,RES):
                A= i*pi/RES;y1=-cos(A)*K
                if  x1<y1 and y1<x2:
                    vr.extend([[y1,fr-0.005,sin(A)*K+z],[y1,fr+0.005,sin(A)*K+z]])
                    n=len(vr);ON.append(n-1);AR.append(n-2)

            vr.extend([[x1,fr-0.005,sqrt(K**2-x1**2)+z],[x1,fr+0.005,sqrt(K**2-x1**2)+z]])
            vr.extend([[x1,fr-0.005,Z[-3]+ek+k3*2     ],[x1,fr+0.005,Z[-3]+ek+k3*2     ]])
            vr.extend([[x2,fr-0.005,Z[-3]+ek+k3*2     ],[x2,fr+0.005,Z[-3]+ek+k3*2     ]])
            vr.extend([[x2,fr-0.005,sqrt(K**2-x2**2)+z],[x2,fr+0.005,sqrt(K**2-x2**2)+z]])
            n=len(vr);ON.extend([n-1,n-3,n-5,n-7]);AR.extend([n-2,n-4,n-6,n-8])
            fc.append(ON);AR.reverse();fc.append(AR)
            m=len(fc);cam.extend([m-1,m-2])

    elif sRef.dPanTilt:# Inclined (Egri)
        H=sin(sRef.dpanAngle*pi/180)/cos(sRef.dpanAngle*pi/180)

        if revTilt: # set peak to opposite side, used by split hinge, right panel.
            H*=-1

        z=sqrt(k1**2+(k1*H)**2)
        k=sqrt(k2**2+(k2*H)**2)
        f=sqrt(k3**2+(k3*H)**2)*2
        vr[UST[0]][2]=Z[-1]+vr[UST[0]][0]*H
        vr[UST[1]][2]=Z[-1]+vr[UST[1]][0]*H
        for i in ALT:
            vr[i][2] =Z[-1]+vr[i][0]*H-z
        vr[SON[0]][2]=Z[-1]+vr[SON[0]][0]*H
        vr[SON[1]][2]=Z[-1]+vr[SON[1]][0]*H
        fc.append([UST[1],UST[0], SON[0],SON[1] ])
        for i in range(0,panCols*4,4):
            fc.append([ALT[i],ALT[i+1],ALT[i+3],ALT[i+2]])
        ON=[UST[0]]
        AR=[UST[1]]
        for i in range(0,len(ALT)-1,2):
            ON.append(ALT[i  ])
            AR.append(ALT[i+1])
        ON.append(SON[0])
        fc.append(ON)
        AR.append(SON[1])
        AR.reverse();fc.append(AR)
        y=panRows-1
        for x in range(0,panCols):
            if  kx[x][y]==True:
                Kapak(vr,fc,X,Z,x*2+1,y*2+1,k2/2,(k1+k2)*0.5-0.01)
                n=len(vr)
                vr[n- 5][2]=Z[-1]+vr[n- 5][0]*H-z
                vr[n- 6][2]=Z[-1]+vr[n- 6][0]*H-z-k
                vr[n- 7][2]=Z[-1]+vr[n- 7][0]*H-z-k
                vr[n- 8][2]=Z[-1]+vr[n- 8][0]*H-z
                vr[n- 9][2]=Z[-1]+vr[n- 9][0]*H-z
                vr[n-10][2]=Z[-1]+vr[n-10][0]*H-z-k
                vr[n-11][2]=Z[-1]+vr[n-11][0]*H-z-k
                vr[n-12][2]=Z[-1]+vr[n-12][0]*H-z
                Fitil(vr,fc,X,Z,x*2+1,y*2+1,k3,(k1+k2)*0.5-0.01,k2)
                n=len(vr)
                vr[n- 2][2]=Z[-1]+vr[n- 2][0]*H-z-k-f
                vr[n- 3][2]=Z[-1]+vr[n- 3][0]*H-z-k-f
                vr[n- 6][2]=Z[-1]+vr[n- 6][0]*H-z-k-f
                vr[n- 7][2]=Z[-1]+vr[n- 7][0]*H-z-k-f
                vr[n-13][2]=Z[-1]+vr[n-13][0]*H-z-k
                vr[n-14][2]=Z[-1]+vr[n-14][0]*H-z-k-f
                vr[n-15][2]=Z[-1]+vr[n-15][0]*H-z-k-f
                vr[n-16][2]=Z[-1]+vr[n-16][0]*H-z-k
                vr[n-17][2]=Z[-1]+vr[n-17][0]*H-z-k
                vr[n-18][2]=Z[-1]+vr[n-18][0]*H-z-k-f
                vr[n-19][2]=Z[-1]+vr[n-19][0]*H-z-k-f
                vr[n-20][2]=Z[-1]+vr[n-20][0]*H-z-k
            else:
                Fitil(vr,fc,X,Z,x*2+1,y*2+1,k3,0,0)
                n=len(vr)
                vr[n-2][2]=Z[-1]+vr[n-2][0]*H-z-f
                vr[n-3][2]=Z[-1]+vr[n-3][0]*H-z-f
                vr[n-6][2]=Z[-1]+vr[n-6][0]*H-z-f
                vr[n-7][2]=Z[-1]+vr[n-7][0]*H-z-f
                vr[n-13][2]=Z[-1]+vr[n-13][0]*H-z
                vr[n-14][2]=Z[-1]+vr[n-14][0]*H-z-f
                vr[n-15][2]=Z[-1]+vr[n-15][0]*H-z-f
                vr[n-16][2]=Z[-1]+vr[n-16][0]*H-z
                vr[n-17][2]=Z[-1]+vr[n-17][0]*H-z
                vr[n-18][2]=Z[-1]+vr[n-18][0]*H-z-f
                vr[n-19][2]=Z[-1]+vr[n-19][0]*H-z-f
                vr[n-20][2]=Z[-1]+vr[n-20][0]*H-z
            m=len(fc);cam.extend([m-1,m-2])
            ftl.extend([m-3,m-4,m-5,m-6,m-7,m-8,m-9,m-10,m-11,m-12,m-13,m-14])

    else: # Flat top/Duz
        fc.append([UST[1],UST[0],SON[0],SON[1]])
        for i in range(0,panCols*4,4):
            fc.append([ALT[i],ALT[i+1],ALT[i+3],ALT[i+2]])
        ON=[UST[0]]
        AR=[UST[1]]
        for i in range(0,len(ALT)-1,2):
            ON.append(ALT[i  ])
            AR.append(ALT[i+1])
        ON.append(SON[0])
        fc.append(ON)
        AR.append(SON[1])
        AR.reverse();fc.append(AR)

#OBJE -----------------------------------------------------------

    mesh = bpy.data.meshes.new(name='DoorPanels')
    mesh.from_pydata(vr,[],fc)

    panelObj=bpy.data.objects.new("DoorPanels",mesh)
    panelObj.location=bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(panelObj)

    # set material colors for panel casing.
    puMatRGBSet=sRef.dpanRGB
    mesh.materials.append(uMatRGBSet('PanelC_mat',puMatRGBSet,matMod=True))

    # set material colors for panel inner trim.
# Not being used? Does not show in view or render.
    mesh.materials.append(uMatRGBSet('PanelT_mat',puMatRGBSet,matMod=True))

    for i in ftl:
        mesh.polygons[i].material_index=1
    for i in cam:
        mesh.polygons[i].material_index=2
    for i in mer:
        mesh.polygons[i].material_index=3
    for i in SM:
        mesh.polygons[i].use_smooth = 1

    mesh.update(calc_edges=True)

    return panelObj


################################################################################
#
# Make knobs/handles for door.
#
def create_handle(sRef,context,Back,frame_width,hinge):

    if (sRef.doorKnob == "2"):
        handleVs,handleFs = handleKnob1()
    elif (sRef.doorKnob == "3"):
        handleVs,handleFs  = handleKnob2()
    elif (sRef.doorKnob == "4"):
        handleVs,handleFs  = handleBar()
    else:
        handleVs,handleFs  = handleLever() # default model

    # Open to right or left
    if hinge: # Open left?
        side = 1
    else:
        side = -1

    handleMesh=bpy.data.meshes.new("Handle_"+str(Back))
    handleMesh.from_pydata(handleVs,[],handleFs)
    handleMesh.update(calc_edges=True)

    # set material colors
    kuMatRGBSet=sRef.knobRGB
    handleMesh.materials.append(uMatRGBSet('knob_mat',kuMatRGBSet,matMod=True))

    handleObj=bpy.data.objects.new("Handle_"+str(Back),handleMesh)
    handleObj.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(handleObj)

    xrot = 0.0
    yrot = 0.0

    # Rotate if lever handle when left side open
    if sRef.doorKnob == "1" and hinge:
        yrot = pi

    # Flip for backside...
    if Back:
        xrot = pi

    handleObj.rotation_euler=(xrot,yrot,0)

    # Translate to door and parent
    handleObj.location.x=((frame_width-sRef.doorPI)*side)+(0.10*-side)

# @todo: fix position, not flush with door.
    if Back:
        handleObj.location.y=sRef.doorPD/2
    else:
        handleObj.location.y=0

    handleObj.location.z = 0
    handleObj.lock_rotation = (True, False, True)

    return handleObj
