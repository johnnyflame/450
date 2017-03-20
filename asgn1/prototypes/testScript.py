import bpy
import Init
import random
from bpy import context
from math import sin, cos, radians

#global data from the user
width = 1
length = 1
height = 1 



dimensions = (width,length,height)

#Get the curser location in the scenes
cursor = context.scene.cursor_location






def make_ground():
    ground = bpy.ops.mesh.primitive_plane_add
    ground(location = (0,0,0))
    
    groundsize = [x * 30 for x in dimensions]
    bpy.ops.transform.resize(value = groundsize)
    
    
 
       

def temple():
    
    podium_x = 1
    podium_y = 1
    
    podium_width = 3.0
    podium_length = podium_width * 1.95
    podium_height = podium_width / 4.75

    columns_per_shortedge = 6
    columns_per_longedge = 11
    
    column_base_size = podium_width/15.0 #change this later, definite hardcode here.
    column_base_height = podium_height / 10.0
    column_base_edge = column_base_size / 4.0
    
    column_pillar_height = 2   
    column_pillar_radius = column_base_size * 0.9   
    
    temple_body_width = podium_width * 0.90
    temple_body_length = podium_length * 0.5
    temple_body_height = column_pillar_height
    
    
    #Construction of the temple starts here.
    
    
    podium = bpy.ops.mesh.primitive_cube_add
    podium(location = (podium_x,podium_y,podium_height))   
    bpy.ops.transform.resize(value = (podium_width,podium_length,podium_height))
       
     
    temple_body = bpy.ops.mesh.primitive_cube_add
    temple_body(location = (podium_x,podium_y - podium_length/2,2 * podium_height + column_base_height + temple_body_height))   
    bpy.ops.transform.resize(value = (temple_body_width,temple_body_length,temple_body_height))

  #  cursor=(podium_width,0,s)
   
    
    for s in range(0,columns_per_longedge):
        
        #left-hand side columns on long edge
        bpy.ops.mesh.primitive_cube_add(location = (podium_x + (podium_width - column_base_size - column_base_edge) , podium_y +
        podium_length/2.0 - s * (2 * (podium_length * 0.75) - column_base_size)/(columns_per_longedge - 1), 2 * podium_height + column_base_height))        
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
        
        column = bpy.ops.mesh.primitive_cylinder_add        
        column(location = (podium_x + (podium_width - column_base_size - column_base_edge) ,
          podium_y + podium_length/2.0 - s * (2 * (podium_length * 0.75) - column_base_size)/(columns_per_longedge - 1),
           2 * podium_height + column_base_height + column_pillar_height ))
        bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))   
         
 
      
      #right-hand side columns on long edge
        bpy.ops.mesh.primitive_cube_add(location = (podium_x - (podium_width - column_base_size - column_base_edge) , podium_y +
        podium_length/2.0 - s * (2 * (podium_length * 0.75) - column_base_size)/(columns_per_longedge - 1), 2 * podium_height + column_base_height))        
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
        
        column = bpy.ops.mesh.primitive_cylinder_add        
        column(location = (podium_x - (podium_width - column_base_size - column_base_edge) ,
          podium_y + podium_length/2.0 - s * (2 * (podium_length * 0.75) - column_base_size)/(columns_per_longedge - 1),
           2 * podium_height + column_base_height + column_pillar_height ))
        bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))   
    
    

    
   
    
    




def make_pillars():
    
    #increase the radial distance the cube through the loop
    radialdist = 6

    # Initialize some variables
    xsize = 1.0
    ysize = 1.0
    zsize = 1.0
    theta = 0.0
    z = 1.0
    two_pi_over_8 = 6.28/8.0


    pillars = bpy.ops.mesh.primitive_cylinder_add

    diameter = 0.5

    while theta < 6.28:
        x = radialdist * cos(theta)
        y = radialdist * sin(theta)
        
        pillars(location = (x,y,z))
        
        bpy.ops.transform.resize(value = (diameter,diameter, 1))
        
        theta += two_pi_over_8
    


#Testing code starts here


# Remove existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


make_ground()
temple()    
#make_pillars()