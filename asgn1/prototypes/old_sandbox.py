import bpy
import Init
import random
from bpy import context
from math import sin, cos, radians, pi
import bmesh

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
    bpy.context.selected_objects[0].name = "Ground"
    
    # A texture for rocky planets
# This is loaded from file, and wrapped around the sphere.
# The actual texture is of Mercury, not that it really matters
    groundTexture = bpy.data.textures.new('groundTexture', type='IMAGE')
    groundTexture.image = bpy.data.images.load('//materials/ground/ground_cracked_1.jpg')

    # Make a new material with this texture
    groundMaterial = bpy.data.materials.new('groundMaterial')
    groundMaterial.specular_intensity = 0.0 # Not shiny

    # And add the texture to the material
    groundMatTex = groundMaterial.texture_slots.add()
    groundMatTex.texture = groundTexture
 #   groundMatTex.mapping = 'SPHERE'
    
    bpy.context.object.data.materials.append(groundMaterial);
    
    
    
 
       

def temple():
    
    """
    Temple's components:
        
    - podium
    - column base
    - column pillars
    - body
    - top
    - roof
    """
    '''
    Ideas for randomization :
        
        -body type (dome or square)
        -Height
        -Orders (Number of columns in front and side
        -Size Of the pillars
        -The type of order (Ionian, Doric, Corinthian, Composite)
        -Fluted vs unfluted
        -Material/texture
        -woreness? (small probability that it is just a bunch of broken pillars, like the temple of Apollo)
    
    '''
    use_library = True
    

    
    
    podium_x = 1
    podium_y = 1
    
    podium_width = 3.0
    podium_length = podium_width * 1.95
    podium_height = podium_width / 4.75

    columns_per_shortedge = 6
    columns_per_longedge = 8
    
    column_base_size = podium_width/12.0 # determins the size of the pillars
    column_base_height = podium_height / 10.0
    column_base_edge = column_base_size / 4.0
    
    column_pillar_height = 2   
    column_pillar_radius = column_base_size * 0.9   
    
    temple_body_width = podium_width * 0.90
    temple_body_length = podium_length * 0.5
    temple_body_height = column_pillar_height
    
    top_width = temple_body_width * 1.1
    top_length = podium_length * 0.75
    top_height = podium_height * 0.5
    
    roof_base_height = podium_height * 0.5
    
    roof_width = podium_width * 1.1
    roof_length = top_length * 1.1
    roof_height = podium_height 
    
    
    #Construction of the temple starts here.
    
    
    podium = bpy.ops.mesh.primitive_cube_add
    podium(location = (podium_x,podium_y,podium_height))   
    bpy.ops.transform.resize(value = (podium_width,podium_length,podium_height))
    bpy.context.selected_objects[0].name = "Podium"
       
     
    temple_body = bpy.ops.mesh.primitive_cube_add
    temple_body(location = (podium_x,podium_y - podium_length/2 + column_pillar_radius,2 * podium_height + column_base_height + temple_body_height))   
    bpy.ops.transform.resize(value = (temple_body_width,temple_body_length,temple_body_height))
    bpy.context.selected_objects[0].name = "temple_body"
    
  


    
    top = bpy.ops.mesh.primitive_cube_add
    top(location = (podium_x,podium_y - podium_length/4 + column_pillar_radius,2 * podium_height + column_base_height + temple_body_height + column_pillar_height ))
    bpy.ops.transform.resize(value = (top_width,top_length,top_height))
    bpy.context.selected_objects[0].name = "Top"


    roofbase = bpy.ops.mesh.primitive_cube_add
    roofbase(location = (podium_x,podium_y - podium_length/4 + column_pillar_radius,2 * podium_height + column_base_height + temple_body_height + column_pillar_height + top_height + roof_base_height))
    bpy.ops.transform.resize(value = (roof_width,roof_length,roof_base_height))


    roof = bpy.ops.mesh.primitive_cube_add
    roof(location = (podium_x,podium_y - podium_length/4 + column_pillar_radius,2 * podium_height + column_base_height + temple_body_height + column_pillar_height + top_height + 2*roof_base_height+ 
    roof_height ))
    bpy.ops.transform.resize(value = (roof_width,roof_length,roof_height))
    bpy.context.selected_objects[0].name = "Roof"

   #Make roof
   
    bpy.ops.object.mode_set(mode = 'EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
        
    if hasattr(mesh.verts, "ensure_lookup_table"): 
        mesh.verts.ensure_lookup_table()
            
    for i in range (0,len(mesh.verts)):
        if (i == 7 or i == 3):    
            mesh.verts[i].select = True
        else:
            mesh.verts[i].select = False            
    bpy.ops.mesh.merge(type='CENTER')
   
   
    if hasattr(mesh.verts, "ensure_lookup_table"): 
        mesh.verts.ensure_lookup_table()
        
    for i in range (0,len(mesh.verts)):
        if (i == 1 or i == 5):    
            mesh.verts[i].select = True
        else:
            mesh.verts[i].select = False        
    bpy.ops.mesh.merge(type='CENTER')
   
   
   
   
   
   
   
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    for s in range(0,columns_per_longedge):
        x_offset = podium_width - column_base_size -column_base_edge
        y_offset = podium_length/2.0 - s * (2 * (podium_length * 0.75) - column_base_size - column_base_edge )/(columns_per_longedge - 1)
        
        base_z_location = (2 * podium_height + column_base_height)
        column_z_location =  2 * podium_height + column_base_height + column_pillar_height
        
        
                   
        #left-hand side column bases on long edge
        bpy.ops.mesh.primitive_cube_add(location = (podium_x + x_offset, podium_y + y_offset
        , base_z_location))        
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
        
        #RHS column bases    
        bpy.ops.mesh.primitive_cube_add(location = (podium_x - x_offset , podium_y +
        y_offset, base_z_location))        
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))   
        
            
        if use_library:
            
            stylized_pillars(podium_x + x_offset, podium_y + y_offset
            , base_z_location +column_base_height,height=(column_pillar_height*2)-top_height,b_width=column_base_size)
            
            stylized_pillars(podium_x - x_offset, podium_y + y_offset
            , base_z_location +column_base_height,height=(column_pillar_height*2)-top_height,b_width=column_base_size)
            
        else:
                
            #LHS columns 
            column = bpy.ops.mesh.primitive_cylinder_add        
            column(location = (podium_x + x_offset , podium_y + y_offset,
              column_z_location ))
            bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))                 
            #RHS columns
            
            
            column = bpy.ops.mesh.primitive_cylinder_add        
            column(location = (podium_x - x_offset , podium_y + y_offset,
              column_z_location ))
            bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))   
        
        
    for s in range (0, columns_per_shortedge):
        
        x_offset=(podium_width - column_base_size - column_base_edge) - s * (2 * (podium_width - column_base_size - column_base_edge)/(columns_per_shortedge -1))
        y_offset = podium_length /2.0
        base_z_location = 2 * podium_height + column_base_height
        
        bpy.ops.mesh.primitive_cube_add(location = (podium_x + x_offset, podium_y + y_offset, base_z_location))
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
        
        
        bpy.ops.mesh.primitive_cube_add(location = (podium_x + x_offset, podium_y - (podium_length - column_base_size -column_base_edge), 2 * podium_height + column_base_height))               
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
    
        if use_library:
        
            stylized_pillars(podium_x + x_offset, podium_y + y_offset
                , base_z_location + column_base_height,height=(column_pillar_height*2)-top_height,b_width=column_base_size)
                
            stylized_pillars(podium_x + x_offset, podium_y - (podium_length - column_base_size -column_base_edge), base_z_location + column_base_height,height=(column_pillar_height*2)-top_height,b_width=column_base_size)
    
    
    
    
    
    
        else:        
                column = bpy.ops.mesh.primitive_cylinder_add
                column(location = (podium_x + (podium_width - column_base_size - column_base_edge) - s * (2 * (podium_width - column_base_size - column_base_edge)/(columns_per_shortedge -1)), podium_y + podium_length/2.0,  2 * podium_height + column_base_height + column_pillar_height ))       
                bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))
                     
                   
                column = bpy.ops.mesh.primitive_cylinder_add
                column(location = (podium_x + (podium_width - column_base_size - column_base_edge) - s * (2 * (podium_width - column_base_size - column_base_edge)/(columns_per_shortedge -1)), podium_y - (podium_length - column_base_size -column_base_edge),  2 * podium_height + column_base_height + column_pillar_height ))
                
                bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))

    
  #  bpy.ops.object.mode_set(mode = 'OBJECT') 
    
    


def stylized_pillars(locX,locY,locZ,height,b_width):
    
    total_height = height
    row_height=height
    
    bpy.ops.mesh.add_column(Style="0",col_base=True,addendum=0.04,col_plinth=False,base_type=7,col_taper=0.03,col_flutes=8,base_width=b_width,col_radius=b_width,cap_width=b_width,row_height=height*0.2,col_blocks=5)
    bpy.context.object.location = (locX,locY,locZ)
    bpy.context.object.dimensions[2] = height

    
    

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

bpy.ops.object.mode_set(mode = 'OBJECT')


# Clear the scene: remove existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()



#adding camera here:
bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(13.019, 34.385, 32.3064), rotation=(1.28381, -1.48851e-06, -1.77894), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


# Add a sun
sun = bpy.ops.object.lamp_add(type='SUN', location = (-5, 5, 5))
bpy.context.selected_objects.clear()
bpy.context.selected_objects.append(sun)
bpy.context.object.rotation_euler = mathutils.Euler((-0.7, -0.7, 0), 'XYZ')

# And some ambient light
bpy.context.scene.world.light_settings.use_environment_light = True
bpy.context.scene.world.light_settings.environment_energy = 0.3


make_ground()
temple()    
