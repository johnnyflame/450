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
Utility routines for material colors.
'''
#
################################################################################

import bpy


################################################################################
#
# Simple material management.
# Return new, existing, or modified material reference.
#
# @todo: create additional materials based on diffuse options.
#
def uMatRGBSet(matName,RGBs,matMod=False,dShader='LAMBERT',dNtz=1.0):

    if matName not in bpy.data.materials:
        mtl=bpy.data.materials.new(matName)
        matMod=True
    else:
        mtl=bpy.data.materials[matName]

    if matMod: # Set material values
        mtl.diffuse_color=RGBs
        mtl.diffuse_shader=dShader
        mtl.diffuse_intensity=dNtz

    return mtl


################################################################################
#
# Standard set of material colors - only used by Balcony.
# replaced by "color picker"...
#
def uMatRGBSel(objMtrl):

    matR=0.5
    matG=0.5
    matB=0.5

    # not default...
    if objMtrl=='0': # Metal
        matR=0.75
        matG=0.75
        matB=0.75
    elif objMtrl=='1': # Brown/wood
        matR=0.10
        matG=0.05
        matB=0
    elif objMtrl=='2': # Wood 2
        matR=0.40
        matG=0.20
        matB=0.0
    elif objMtrl=='3': # Wood 2
        matR=0.30
        matG=0.20
        matB=0.10
    elif objMtrl=='4': # glass
        matR=0.50
        matG=0.80
        matB=1.00
    elif objMtrl=='5': # Gold
        matR=0.7
        matG=0.5
        matB=0
    elif objMtrl=='6': # Olive
        matR=0.1
        matG=0.2
        matB=0.1
    elif objMtrl=='7': # Glossy - knob cycles default replacement.
        matR=0.57
        matG=0.55
        matB=0.73
    elif objMtrl=='8': # Glossy - knob cycles coded replacement.
        matR=0.73
        matG=0.78
        matB=0.80
    elif objMtrl=='Black':
        matR=0
        matG=0
        matB=0
    elif objMtrl=='White':
        matR=1
        matG=1
        matB=1

    return [matR,matG,matB]

