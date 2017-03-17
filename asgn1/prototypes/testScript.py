import bpy
from bpy import context
from math import sin, cos, radians


cubeobject = bpy.ops.mesh.primitive_cube_add

#Get the curser location in the scenes
cursor = context.scene.cursor_location

#increase the radial distance the cube through the loop
radialdist = 5.0

# Initialize some variables
xsize = 1.0
ysize = 1.0
zsize = 1.0
theta = 0.0
z = 1.0
two_pi_over_8 = 6.28/8.0

while theta < 6.28:
    x = radialdist * cos(theta)
    y = radialdist * sin(theta)
    
    cubeobject(location = (x,y,z))
    
    bpy.ops.transform.resize(value = (0.2, 0.01, 0.5))
    
    theta += two_pi_over_8
    
    