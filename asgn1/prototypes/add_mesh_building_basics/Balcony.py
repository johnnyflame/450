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
Create a "Balcony" structure, based on code from "SayPRODUCTIONS";
  major revisions to UI and operations, may still be used for original design.
'''
# Author(s): Antonio Vazquez (antonioya), Jambay
# Version: 0, 0, 3
#
# With some work could even resemble a porch.
#
# see "Tube" - thickness == 0 to eliminate segment; apply to all options to
# allow removing stacked elements.
#
# @todo: add vertical/horizontal connectors between elements for "valid"
#  physical structure... that ain't gonna happen.
#
################################################################################

import bpy, bmesh
from bpy.props import BoolProperty, EnumProperty, IntProperty
from bpy_extras.object_utils import object_data_add
from mathutils import Vector
import operator
import os
from math import pi, sin, cos, sqrt, atan
from add_mesh_building_basics.UtilMats import uMatRGBSet, uMatRGBSel

# constants
MAX_SEGS = 8 # segments/levels (stackable elements).
# @todo: make parameters that use BALCONY_SCALE "floats" and remove constant.
BALCONY_SCALE = 100 # divisor (scale) for option values.


################################################################################
# Set UI options for style.
def BalStyles(sRef,BalStyle):

    # set "common" usage/defaults (not used for all types).
# may need to rethink this - what are defaults otherwise?
    sRef.notchC0=0
    sRef.bk0=20
    sRef.notchZ0=3
    sRef.kg2=5
    sRef.Base='1'
    sRef.Lvl1='2'
    sRef.Lvl2='3'
    sRef.mg1=4
    sRef.my1=4

    if BalStyle=='1': # Slats
        sRef.bz0= 80
        sRef.notchC0=4;sRef.fd0=2;sRef.f00=16;sRef.f01=12;sRef.f02=12;sRef.f03=12
        sRef.kp2=True;sRef.kh2=5

    if BalStyle=='2': # Bulwark
        sRef.bz0= 15
        sRef.Lvl1='1';sRef.bz1=60;sRef.bk1=10;sRef.notchC1=0
        sRef.Lvl2='1';sRef.bz2= 15;sRef.bk2=20;sRef.notchC2=0
        sRef.Lvl3='2';sRef.my3=  4;sRef.mg3= 4
        sRef.Lvl4='3';sRef.kp4=True;sRef.kg4= 5;sRef.kh4=5

    if BalStyle=='3': # Glass
        sRef.bz0= 40;sRef.bk0=10
        sRef.Lvl1='4';sRef.cy1= 56
        sRef.kg2= 0;sRef.kh2=4

    if BalStyle=='4': # Marquiee
        sRef.bz0= 30

    if BalStyle=='5': # Eaves
        sRef.bz0= 27;sRef.notchC0=2;sRef.fd0=2;sRef.f00=7;sRef.f01=7

    if BalStyle=='6': # Railing
        sRef.bz0= 50;sRef.notchC0=2;sRef.fd0=2;sRef.f00=12;sRef.f01=20
        sRef.kp2=True;sRef.kh2=4
        sRef.Lvl3='3';sRef.kp3=True;sRef.kg3= 5;sRef.kh3=4
        sRef.Lvl4='3';sRef.kp4=True;sRef.kg4= 5;sRef.kh4=4
        sRef.Lvl5='3';sRef.kp5=True;sRef.kg5= 5;sRef.kh5=5


################################################################################
#
def EXT(PR,vr,fc,lz,mz,rz):
    n=len(vr)
    m=len(PR)

    if lz==0:
        for P in PR:vr.append([-mz,P[0],P[1]])
    else:
        for P in PR:vr.append([ P[0]-mz,  lz,P[1]])
        for P in PR:vr.append([ P[0]-mz,P[0],P[1]])

    if rz==0:
        for P in PR:vr.append([ mz,P[0],P[1]])
    else:
        for P in PR:vr.append([-P[0]+mz,P[0],P[1]])
        for P in PR:vr.append([-P[0]+mz,  rz,P[1]])

    if   lz==0 and rz==0:l=1
    elif lz==0 and rz> 0:l=2
    elif lz> 0 and rz==0:l=2
    elif lz> 0 and rz> 0:l=3

    for j in range(0,l):
        for i in range(0,m):
            a=j*m
            if i==m-1:fc.append([a+i+n,a+0+n+0,a+0+n+0+m,a+i+n+m])
            else:     fc.append([a+i+n,a+i+n+1,a+i+n+1+m,a+i+n+m])


################################################################################
#
def add_balcony(sRef,context):
    fc=[];vr=[];SM=[];Bal=[];Par=[];Mer=[];Crm=[];Glass=[];Dos=[];blok=[]

    #blok.append([Style,[Wall,[Slots]],[Flat],[Tube],[Glass]])
    blok.append([
        sRef.Base,
        [sRef.bz0,sRef.bk0,sRef.notchC0,sRef.notchZ0,sRef.fd0,
        [sRef.f00,sRef.f01,sRef.f02,sRef.f03,sRef.f04,sRef.f05,sRef.f06,sRef.f07]
        ], # Wall and Slots
        [sRef.my0,sRef.mg0], # Flat
        [sRef.kp0,sRef.kg0,sRef.kh0], # Tube
        [sRef.cy0] # Glass
        ])

    blok.append([sRef.Lvl1,[sRef.bz1,sRef.bk1,sRef.notchC1,sRef.notchZ1,sRef.fd1,
        [sRef.f10,sRef.f11,sRef.f12,sRef.f13,sRef.f14,sRef.f15,sRef.f16,sRef.f17]],
        [sRef.my1,sRef.mg1],[sRef.kp1,sRef.kg1,sRef.kh1],[sRef.cy1]])
    blok.append([sRef.Lvl2,[sRef.bz2,sRef.bk2,sRef.notchC2,sRef.notchZ2,sRef.fd2,
        [sRef.f20,sRef.f21,sRef.f22,sRef.f23,sRef.f24,sRef.f25,sRef.f26,sRef.f27]],
        [sRef.my2,sRef.mg2],[sRef.kp2,sRef.kg2,sRef.kh2],[sRef.cy2]])
    blok.append([sRef.Lvl3,[sRef.bz3,sRef.bk3,sRef.notchC3,sRef.notchZ3,sRef.fd3,
        [sRef.f30,sRef.f31,sRef.f32,sRef.f33,sRef.f34,sRef.f35,sRef.f36,sRef.f37]],
        [sRef.my3,sRef.mg3],[sRef.kp3,sRef.kg3,sRef.kh3],[sRef.cy3]])
    blok.append([sRef.Lvl4,[sRef.bz4,sRef.bk4,sRef.notchC4,sRef.notchZ4,sRef.fd4,
        [sRef.f40,sRef.f41,sRef.f42,sRef.f43,sRef.f44,sRef.f45,sRef.f46,sRef.f47]],
        [sRef.my4,sRef.mg4],[sRef.kp4,sRef.kg4,sRef.kh4],[sRef.cy4]])
    blok.append([sRef.Lvl5,[sRef.bz5,sRef.bk5,sRef.notchC5,sRef.notchZ5,sRef.fd5,
        [sRef.f50,sRef.f51,sRef.f52,sRef.f53,sRef.f54,sRef.f55,sRef.f56,sRef.f57]],
        [sRef.my5,sRef.mg5],[sRef.kp5,sRef.kg5,sRef.kh5],[sRef.cy5]])
    blok.append([sRef.Lvl6,[sRef.bz6,sRef.bk6,sRef.notchC6,sRef.notchZ6,sRef.fd6,
        [sRef.f60,sRef.f61,sRef.f62,sRef.f63,sRef.f64,sRef.f65,sRef.f66,sRef.f67]],
        [sRef.my6,sRef.mg6],[sRef.kp6,sRef.kg6,sRef.kh6],[sRef.cy6]])
    blok.append([sRef.Lvl7,[sRef.bz7,sRef.bk7,sRef.notchC7,sRef.notchZ7,sRef.fd7,
        [sRef.f70,sRef.f71,sRef.f72,sRef.f73,sRef.f74,sRef.f75,sRef.f76,sRef.f77]],
        [sRef.my7,sRef.mg7],[sRef.kp7,sRef.kg7,sRef.kh7],[sRef.cy7]])

    h=-sRef.FLz/BALCONY_SCALE
    dh=h+sRef.FLzI/BALCONY_SCALE
    du=sRef.FLy/BALCONY_SCALE
    lz=sRef.luz/BALCONY_SCALE
    mz=sRef.muz/BALCONY_SCALE
    rz=sRef.ruz/BALCONY_SCALE
    dg=-((blok[0][1][1]-sRef.ddg)/BALCONY_SCALE)

    if h<0:#Floor
        if lz==0 and rz==0:
            vr=[[-mz,du,h],[ mz,du, h],[-mz,dg, h],[ mz,dg, h],[-mz,dg, 0],
                [ mz,dg,0],[-mz, 0,dh],[ mz, 0,dh],[-mz,du,dh],[ mz,du,dh]]
            fc=[[0,1,3,2],[2,3,5,4],[6,7,9,8]];Dos=[0,1,2]
        if lz==0 and rz >0:
            vr=[[-mz,   du,h],[ mz-dg,du, h],[-mz,   dg, h],[ mz-dg,dg, h],[-mz,   dg, 0],
                [ mz-dg,dg,0],[-mz, 0,   dh],[ mz-dg, 0,dh],[-mz,   du,dh],[ mz-dg,du,dh],[ mz-dg,du,0]]
            fc=[[0,1,3,2],[2,3,5,4],[6,7,9,8],[3,1,10,5]];Dos=[0,1,2,3]
        if lz >0 and rz==0:
            vr=[[-mz+dg,du,h],[ mz,   du, h],[-mz+dg,dg, h],[ mz,   dg, h],[-mz+dg,dg, 0],
                [ mz,   dg,0],[-mz+dg, 0,dh],[ mz,    0,dh],[-mz+dg,du,dh],[ mz,   du,dh],[-mz+dg,du,0]]
            fc=[[0,1,3,2],[2,3,5,4],[6,7,9,8],[0,2,4,10]];Dos=[0,1,2,3]
        if lz >0 and rz >0:
            vr=[[-mz+dg,dg,0],[mz-dg,dg,0],[-mz+dg,dg, h],[mz-dg,dg, h],[-mz+dg,du, h],[mz-dg,du, h],
                [-mz+dg,du,0],[mz-dg,du,0],[-mz,    0,dh],[mz,    0,dh],[-mz,   du,dh],[mz,   du,dh]]
            fc=[[1,0,2,3],[3,2,4,5],[6,4,2,0],[3,5,7,1],[8,9,11,10]];Dos=[0,1,2,3,4]
    else:
        vr=[[-mz, 0, h],[mz, 0, h],[-mz,du, h],[mz,du, h],
            [-mz,du,dh],[mz,du,dh],[-mz, 0,dh],[mz, 0,dh]]
        fc=[[1,0,2,3],[5,4,6,7]];Dos=[0,1]

    z=0
    for i in range(MAX_SEGS):
        if blok[i][0]=='1':# Wall
            k1=blok[i][1][1]/BALCONY_SCALE
            h =blok[i][1][0]/BALCONY_SCALE
            notchZ=blok[i][1][3]/BALCONY_SCALE
            fd=blok[i][1][4]/BALCONY_SCALE
            PR=[[-k1,z],[0,z],[0,z+h],[-k1,z+h]]
            z+=h
            fz=z

            for f in range(blok[i][1][2]):
                fz-=blok[i][1][5][f]/BALCONY_SCALE
                PR.append([-k1,   fz   ]);PR.append([-k1+fd,fz   ])
                PR.append([-k1+fd,fz-notchZ]);PR.append([-k1,   fz-notchZ])
                fz-=notchZ
            BB=len(fc)
            EXT(PR,vr,fc,lz,mz,rz)
            BE=len(fc)
            for F in range(BB,BE):Bal.append(F)

        if blok[i][0]=='2':#Flat
            k1=blok[0][1][1]/BALCONY_SCALE;k2=blok[i][2][1]/BALCONY_SCALE;h=blok[i][2][0]/BALCONY_SCALE
            PR=[[-k1-k2,z],[k2,z],[k2,z+h],[-k1-k2,z+h]]
            z+=h
            BB=len(fc)
            EXT(PR,vr,fc,lz,mz,rz)
            BE=len(fc)
            for F in range(BB,BE):Mer.append(F)

        if blok[i][0]=='3' and blok[i][3][2]:#Tube - with height
            k1=blok[0][1][1]/BALCONY_SCALE;k2=blok[i][3][2]/BALCONY_SCALE;h=blok[i][3][1]/BALCONY_SCALE

            if blok[i][3][0]:# Round.
                PR=[];z+=h+k2
                for a in range(24):
                    x=-k1+cos(a*pi/12)*k2;y=z+sin(a*pi/12)*k2
                    PR.append([x,y])
                z+=k2
            else:# Square (default).
                z+=h
                PR=[[-k1-k2,z],[-k1+k2,z],[-k1+k2,z+k2*2],[-k1-k2,z+k2*2]]
                z+=k2*2

            BB=len(fc)
            EXT(PR,vr,fc,lz,mz,rz)
            BE=len(fc)
            for F in range(BB,BE):Crm.append(F)
            if blok[i][3][0] and blok[i][3][2]: # Round, with height?
                for F in range(BB,BE):SM.append(F)

        if blok[i][0]=='4':#Glass
            k1=blok[0][1][1]/BALCONY_SCALE;h=blok[i][4][0]/BALCONY_SCALE
            PR=[[-k1-0.001,z],[-k1+0.001,z],[-k1+0.001,z+h],[-k1-0.001,z+h]]
            z+=h;BB=len(fc);n=len(vr)
            fc.append([n+1,n,n+3,n+2])
            EXT(PR,vr,fc,lz,mz,rz)
            n=len(vr)
            fc.append([n-2,n-1,n-4,n-3])
            BE=len(fc)
            for F in range(BB,BE):Glass.append(F)

    mesh = bpy.data.meshes.new(name='Balcony')
    mesh.from_pydata(vr,[],fc)

    for i in SM:
        mesh.polygons[i].use_smooth = 1

# @todo: this is wrong, need to add material(s) for each item/object.
    mesh.materials.append(uMatRGBSet('Wall',uMatRGBSel('0')))
    mesh.materials.append(uMatRGBSet('Flat',uMatRGBSel('Black')))
    mesh.materials.append(uMatRGBSet('Tube',uMatRGBSel('2')))
    mesh.materials.append(uMatRGBSet('Glass',uMatRGBSel('4')))
    mesh.materials.append(uMatRGBSet('Floor',uMatRGBSel('White')))

    for i in Bal:mesh.polygons[i].material_index = 0
    for i in Mer:mesh.polygons[i].material_index = 1
    for i in Crm:mesh.polygons[i].material_index = 2
    for i in Glass:mesh.polygons[i].material_index = 3
    for i in Dos:mesh.polygons[i].material_index = 4
    for i in Par:mesh.polygons[i].material_index = 5

    mesh.update(calc_edges=True)
    object_data_add(context, mesh, operator=None)

# WTH? switch in and out of EDIT?
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()


################################################################################
#
class AddBalcony(bpy.types.Operator):
    bl_idname = "mesh.add_balcony"
    bl_label = "Balcony"
    bl_description = "Balcony/desk/Signage"
    bl_options = {'REGISTER', 'UNDO'}

    Style = EnumProperty(items=(
        ("1","Slats",""),
        ("2","Bulwark",""),
        ("3","Glass",""),
        ("4","Marquee",""),
        ("5","Eaves",""),
        ("6","Railing","")
        ),
        name="Style",description="Predefined design")
    curStyle=Style

    luz=IntProperty(name='<',min=0,max=1000,default=100)
    muz=IntProperty(         min=0,max=1000,default=100)
    ruz=IntProperty(name='>',min=0,max=1000,default=100)

    FLy=IntProperty(name='Depth',min=1,max=250,default=100,description="Floor depth (y).")
    FLzI=IntProperty(name='Height',min=1,max=100,default= 17,description="Floor inner plane vertical position.")
    FLz=IntProperty(name='BaseZ',min=-50,max=50,default=1,description="Floor origin offset.")
    ddg=IntProperty(min=0,max= 50,default= 10,description="Floor Width")

    #Type
    Base=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="1")

    #Base
    bz0=IntProperty(name='Height',min=1,max=100,default=80)
    bk0=IntProperty(name='Thickness', min=1,max= 50,default=20)
    notchC0=IntProperty(name='Notch',min=0,max=8,default=4,description='Horizontal cut-outs in wall.')
    notchZ0=IntProperty(min=1,max=10,default=3,description="Notch height")
    fd0=IntProperty(min=1,max=10,default=2,description="Notch depth")
    f00=IntProperty(min=1,max=100,default=16);f01=IntProperty(min=1,max=100,default=12)
    f02=IntProperty(min=1,max=100,default=12);f03=IntProperty(min=1,max=100,default=12)
    f04=IntProperty(min=1,max=100,default= 3);f05=IntProperty(min=1,max=100,default= 3)
    f06=IntProperty(min=1,max=100,default= 3);f07=IntProperty(min=1,max=100,default= 3)
    #Flat
    my0=IntProperty(name='Height',min=1,max=50,default=4)
    mg0=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp0=BoolProperty(default=False)
    kg0=IntProperty(min=0,max=50,default=5)
    kh0=IntProperty(min=0,max=20,default=5)
    #Glass
    cy0=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl1=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="2")
    # Wall
    bz1=IntProperty(name='Height',min=1,max=100,default=80)
    bk1=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC1=IntProperty(name='Notch',min=0,max=8,default=4)
    notchZ1=IntProperty(min=1,max= 10,default=3)
    fd1=IntProperty(min=1,max= 10,default=2)
    f10=IntProperty(min=1,max=100,default=3)
    f11=IntProperty(min=1,max=100,default=3)
    f12=IntProperty(min=1,max=100,default=3)
    f13=IntProperty(min=1,max=100,default=3)
    f14=IntProperty(min=1,max=100,default=3)
    f15=IntProperty(min=1,max=100,default=3)
    f16=IntProperty(min=1,max=100,default=3)
    f17=IntProperty(min=1,max=100,default=3)
    #Flat
    my1=IntProperty(name='Height',min=1,max=50,default=4)
    mg1=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp1=BoolProperty(default=False)
    kg1=IntProperty(min=0,max=50,default=5)
    kh1=IntProperty(min=0,max=20,default=5)
    #Glass
    cy1=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl2=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="3")
    #Balcony
    bz2=IntProperty(name='Height',min=1,max=100,default=80)
    bk2=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC2=IntProperty(name='Notch',min=0,max=8,default=4)
    notchZ2=IntProperty(min=1,max=10,default=3)
    fd2=IntProperty(min=1,max= 10,default=2)
    f20=IntProperty(min=1,max=100,default=3);f21=IntProperty(min=1,max=100,default=3)
    f22=IntProperty(min=1,max=100,default=3);f23=IntProperty(min=1,max=100,default=3)
    f24=IntProperty(min=1,max=100,default=3);f25=IntProperty(min=1,max=100,default=3)
    f26=IntProperty(min=1,max=100,default=3);f27=IntProperty(min=1,max=100,default=3)
    #Flat
    my2=IntProperty(name='Height',min=1,max=50,default=4)
    mg2=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp2=BoolProperty(default=False)
    kg2=IntProperty(min=0,max=50,default=5)
    kh2=IntProperty(min=0,max=20,default=5)
    #Glass
    cy2=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl3=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="3")
    #Balcony
    bz3=IntProperty(name='Height',min=1,max=100,default=80)
    bk3=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC3=IntProperty(name='Notch',min=0,max=8,default=4)
    notchZ3=IntProperty(min=1,max= 10,default=3)
    fd3=IntProperty(min=1,max= 10,default=2)
    f30=IntProperty(min=1,max=100,default=3);f31=IntProperty(min=1,max=100,default=3)
    f32=IntProperty(min=1,max=100,default=3);f33=IntProperty(min=1,max=100,default=3)
    f34=IntProperty(min=1,max=100,default=3);f35=IntProperty(min=1,max=100,default=3)
    f36=IntProperty(min=1,max=100,default=3);f37=IntProperty(min=1,max=100,default=3)
    #Flat
    my3=IntProperty(name='Height',min=1,max=50,default=4)
    mg3=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp3=BoolProperty(default = False)
    kg3=IntProperty(min=0,max=50,default=5)
    kh3=IntProperty(min=0,max=20,default=5)
    #Glass
    cy3=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl4=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="3")
    #Wall
    bz4=IntProperty(name='Height',min=1,max=100,default=80)
    bk4=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC4=IntProperty(name='Notch',min=0,max=8,default=4,)
    notchZ4=IntProperty(min=1,max= 10,default=3)
    fd4=IntProperty(min=1,max=10,default=2)
    f40=IntProperty(min=1,max=100,default=3);f41=IntProperty(min=1,max=100,default=3)
    f42=IntProperty(min=1,max=100,default=3);f43=IntProperty(min=1,max=100,default=3)
    f44=IntProperty(min=1,max=100,default=3);f45=IntProperty(min=1,max=100,default=3)
    f46=IntProperty(min=1,max=100,default=3);f47=IntProperty(min=1,max=100,default=3)
    #Flat
    my4=IntProperty(name='Height',min=1,max=50,default=4)
    mg4=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp4=BoolProperty(default=False)
    kg4=IntProperty(min=0,max=50,default=5)
    kh4=IntProperty(min=0,max=20,default=5)
    #Glass
    cy4=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl5=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="3")
    #Wall
    bz5=IntProperty(name='Height',min=1,max=100,default=80)
    bk5=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC5=IntProperty(name='Notch',min=0,max=8,default=4)
    notchZ5=IntProperty(min=1,max= 10,default=3)
    fd5=IntProperty(min=1,max= 10,default=2)
    f50=IntProperty(min=1,max=100,default=3);f51=IntProperty(min=1,max=100,default=3)
    f52=IntProperty(min=1,max=100,default=3);f53=IntProperty(min=1,max=100,default=3)
    f54=IntProperty(min=1,max=100,default=3);f55=IntProperty(min=1,max=100,default=3)
    f56=IntProperty(min=1,max=100,default=3);f57=IntProperty(min=1,max=100,default=3)
    #Flat
    my5=IntProperty(name='Height',min=1,max=50,default=4)
    mg5=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp5=BoolProperty(default=False)
    kg5=IntProperty(min=0,max=50,default=5)
    kh5=IntProperty(min=0,max=20,default=5)
    #Glass
    cy5=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl6=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="3")
    #Wall
    bz6=IntProperty(name='Height',min=1,max=100,default=80)
    bk6=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC6=IntProperty(name='Notch',min=0,max=8,default=4)
    notchZ6=IntProperty(min=1,max= 10,default=3)
    fd6=IntProperty(min=1,max= 10,default=2)
    f60=IntProperty(min=1,max=100,default=3);f61=IntProperty(min=1,max=100,default=3)
    f62=IntProperty(min=1,max=100,default=3);f63=IntProperty(min=1,max=100,default=3)
    f64=IntProperty(min=1,max=100,default=3);f65=IntProperty(min=1,max=100,default=3)
    f66=IntProperty(min=1,max=100,default=3);f67=IntProperty(min=1,max=100,default=3)
    #Flat
    my6=IntProperty(name='Height',min=1,max=50,default=4)
    mg6=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp6=BoolProperty(default=False)
    kg6=IntProperty(min=0,max=50,default=5)
    kh6=IntProperty(min=0,max=20,default=5)
    #Glass
    cy6=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    #Type
    Lvl7=EnumProperty(items=(
        ("1","Wall",""),
        ("2","Flat",""),
        ("3","Tube",""),
        ("4","Glass",""),
        ),
        default="3")
    #Wall
    bz7=IntProperty(name='Height',min=1,max=100,default=80)
    bk7=IntProperty(name='Thickness',min=1,max= 50,default=20)
    notchC7=IntProperty(name='Notch',min=0,max=8,default=4)
    notchZ7=IntProperty(min=1,max= 10,default=3)
    fd7=IntProperty(min=1,max= 10,default=2)
    f70=IntProperty(min=1,max=100,default=3);f71=IntProperty(min=1,max=100,default=3)
    f72=IntProperty(min=1,max=100,default=3);f73=IntProperty(min=1,max=100,default=3)
    f74=IntProperty(min=1,max=100,default=3);f75=IntProperty(min=1,max=100,default=3)
    f76=IntProperty(min=1,max=100,default=3);f77=IntProperty(min=1,max=100,default=3)
    #Flat
    my7=IntProperty(name='Height',min=1,max=50,default=4)
    mg7=IntProperty(name='Thickness',min=0,max=20,default=4)
    #Tube
    kp7=BoolProperty(default=False,description="Pipe shape.")
    kg7=IntProperty(min=0,max=50,default=5,description='Spacing from lower element.')
    kh7=IntProperty(min=0,max=20,default=5,description='Thickness; set to 0 to remove segment.')
    #Glass
    cy7=IntProperty(name='Height',min=1,max=100,default=20)

    #--------------------------------------------------------------
    def draw(self, context):
        layout = self.layout

        layout.prop(self,'Style')
        layout.prop(self,'muz',text="Width")
        row=layout.row()
        row.label(text="side depth")
        row=layout.row()
        row.prop(self,'luz',text="Left")
        row.prop(self,'ruz',text="Right")

        layout.label('Floor')
        row=layout.row()
        row.prop(self,'FLy') # depth
        row.prop(self,'FLzI') # inner plane vertical position.
        row=layout.row()
        row.prop(self,'FLz') # floor origin subset from 3D cursor.
        row.prop(self,'ddg') # width reduction, 0=match primary, to be continued...

        # create/initialize lists for elements.
        ls=[];lf=[]

        ls.append(self.Base);lf.append(self.notchC0)
        ls.append(self.Lvl1);lf.append(self.notchC1)
        ls.append(self.Lvl2);lf.append(self.notchC2)
        ls.append(self.Lvl3);lf.append(self.notchC3)
        ls.append(self.Lvl4);lf.append(self.notchC4)
        ls.append(self.Lvl5);lf.append(self.notchC5)
        ls.append(self.Lvl6);lf.append(self.notchC6)
        ls.append(self.Lvl7);lf.append(self.notchC7)

        for i in range(MAX_SEGS-1,-1,-1):
            box=layout.box()
            if i:
                box.prop(self,'Lvl'+str(i))
            else:
                box.prop(self,'Base')

            if ls[i]=='1':# Wall
                box.prop(self,'bz'+str(i))
                box.prop(self,'bk'+str(i))
                box.prop(self,'notchC'+str(i))
                if lf[i]>0:
                    row=box.row()
                    row.prop(self,'notchZ'+str(i),text='Height')
                    row.prop(self,'fd'+str(i),text='Depth')
                for f in range(lf[i]):
                    box.prop(self,'f'+str(i)+str(f),text='Interval')

            if ls[i]=='2':#Flat
                row=box.row()
                row.prop(self,'my'+str(i))
                row.prop(self,'mg'+str(i))

            if ls[i]=='3':#Tube
                row=box.row()
                row.prop(self,'kp'+str(i),text='O')
                row.prop(self,'kg'+str(i),text='Gap')
                box.prop(self,'kh'+str(i),text='Thickness')

            if ls[i]=='4':#Glass
                box.prop(self,'cy'+str(i))

    ##########-##########-##########-##########

    def execute(self, context):
        if self.curStyle!=self.Style: # Don't modify/reset unless new style selected.
            BalStyles(self,self.Style)
            self.curStyle=self.Style

        add_balcony(self,context)

        return {'FINISHED'}
