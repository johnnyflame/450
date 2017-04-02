import imp
import bpy
import Init
import random
from bpy import context
from math import sin, cos, radians, pi
import bmesh
import mathutils

import Render 
imp.reload(Render)





#Get the curser location in the scenes
cursor = context.scene.cursor_location



def create(xSize, ySize, height, name):
    """Create a building with the given dimensions and name"""
    
    # Create an empty object to act as a reference and an object
    bpy.ops.object.empty_add(location=(0,0,0))
    bpy.context.selected_objects[0].name = name
    axes = bpy.data.objects[name]
    
    # Create a cube and resize it appropriately
    bpy.ops.mesh.primitive_cube_add(location=(xSize*0.5, ySize*0.5, height*0.5))
    bpy.context.selected_objects[0].name = name + ".block"
    bpy.ops.transform.resize(value=(xSize*0.5, ySize*0.5, height*0.5))
    
    # Assign a random concrete material to the block
    block = bpy.data.objects[name+".block"]
    block.data.materials.append(random.choice(Init.materials))
    
    # Make the block a child of the reference axes
    block.parent=axes
    
    # And the axes are returned so that the building can be moved
    return axes






def make_ground(xSize,ySize,height):
    dimensions = (xSize,ySize,height)
    ground = bpy.ops.mesh.primitive_plane_add
    
    ground(location = (xSize*0.5,ySize*0.5,0))
    
    groundsize = [x * 0.5 for x in dimensions]
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
    
    bpy.context.object.data.materials.append(groundMaterial)
    bpy.context.object.active_material.texture_slots[0].scale[0] = 5
    bpy.context.object.active_material.texture_slots[0].scale[1] = 5
    bpy.context.object.active_material.texture_slots[0].scale[2] = 5

    
    
    
 
       

def temple():
    
   
    """
    Temple's components:
        
    - podium
    - column base
    - column pillars
    - body
    - top
    - roof
    - Dome
    - Stairs
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
    #####################################################################################################################
    # Boolean flags with default values, chages with input dimensions.
    has_dome = False
    use_library = False
    is_fluted = False
    
    
    
     
    columns_per_shortedge = 2 #random.choice([2,4,6,8]) 
    columns_per_longedge =  2 #random.randint(4,8)
    #####################################################################################################################
    
    box_width = 26
    box_length = 26
    
    box_height = 17

    
    
    make_ground(box_width,box_length,box_height)
   
    if box_width < 3:
        use_library = False
                
    podium_x = box_width * 0.5
    podium_y = box_length * 0.5
    
    MAX_PODIUM_WIDTH = box_width * 0.5
    MAX_PODIUM_LENGTH = box_length * 0.5
    
    MAX_BUILDING_HEIGHT = box_height * 0.5
    
 #   MAX_BUILDING_HEIGHT = height * 0.5 
    
    
    
    
    podium_width = MAX_PODIUM_WIDTH * 0.5#random.uniform(0.35,0.6)
    podium_length = MAX_PODIUM_LENGTH #parametise this, work out valid range
    
    podium_height = MAX_BUILDING_HEIGHT / 5.88 #parametise this, work out a range.
    
    available_height = MAX_BUILDING_HEIGHT - podium_height 
    
    
    # If the building has a dome, a new list of parameters are needed to make it look sensible.
    if has_dome:
            
        podium_width = MAX_PODIUM_WIDTH * 0.5
        podium_length = podium_width * 1.80#parametise this, work out valid range
        podium_height = podium_width / 4.75 #parametise this.
        
        podium_x = box_width * 0.5
        podium_y = box_length * 0.5 + podium_length/2
        
        # Dome Parameters
        # height: randomize 
        dome_body_height = box_height * 0.5

        dome_body_radius = MAX_PODIUM_WIDTH
        
        dome_locX = podium_x 
        dome_locY = podium_y - podium_length 
        dome_locZ = dome_body_height 
   
            
        
        
    
    
   
    
    column_base_size = min((podium_width/8),min(podium_width/(columns_per_shortedge * 2),podium_length/(columns_per_longedge * 2))) # determins the size of the pillars
    
    
    column_base_height = podium_height / 10.0
    column_base_edge = column_base_size / 4.0
    
    
    #paramized according to building height
    
    #Changing the ratio drastically here is NOT recommented, 
    column_pillar_height = podium_width * 0.666  
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
    roof_height = podium_height * 1.0
    
    

    
    
    
    stair_locX = podium_x
    stair_locY = podium_y + podium_length
    stair_locZ = podium_height
    
    stair_length = podium_length * 0.25 - column_base_size
    stair_width = podium_width * 0.31 
    stair_height = podium_height 
    
    

    
    
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

   # Make roof by folding in vertices
   
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
    
    
    # Placing the column base tiles and the columns.
    
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
        
        # This ensures no overlap of objects.
        if s != 0 and s != columns_per_shortedge-1:
        
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
    

    if has_dome:                                    make_dome(dome_locX,dome_locY,dome_locZ,height=dome_body_height,radius=dome_body_radius)    

    make_stairs(stair_locX,stair_locY,stair_locZ,stair_height,stair_width,stair_length,length_offset=column_base_size)


#Using an addon to generate beautiful, stylized columns, lots of parameters to randomize here.
def stylized_pillars(locX,locY,locZ,height,b_width):
    
    total_height = height
    row_height=height
    
    bpy.ops.mesh.add_column(Style="0",col_base=True,addendum=0.04,col_plinth=False,base_type=7,col_taper=0.01,col_flutes=8,base_width=b_width,col_radius=b_width,cap_width=b_width,row_height=height*0.2,col_blocks=5)
    
    bpy.context.object.location = (locX,locY,locZ)
    bpy.context.object.dimensions[2] = height

    

        


# The 'dome' part of the building, as seen in Pantheon. Basically a ball and a cylinder with decorations
def make_dome(locX,locY,locZ,height,radius):
    
    dome_radius = radius * 0.95
    dome_height = height * 0.9
    dome_locZ = locZ + 0.80 * dome_height
    
    
    dome_body = bpy.ops.mesh.primitive_cylinder_add
    dome_body(location = (locX,locY,locZ))
    bpy.ops.transform.resize(value=(radius,radius,height))
    
    
    dome = bpy.ops.mesh.primitive_uv_sphere_add
    dome(location = (locX,locY,dome_locZ))
    bpy.ops.transform.resize(value=(dome_radius,dome_radius,dome_height))
    
    
    
def make_stairs(locX,locY,locZ,height,width,length,length_offset):
        
    cutaway = bpy.ops.mesh.primitive_cube_add    
    cutaway(location = (locX,locY,locZ))
    bpy.ops.transform.resize(value = (width,(length * 2) - length_offset,height*2))
    bpy.context.selected_objects[0].name = "Cutaway"
        
    object = bpy.data.objects['Cutaway']
    object.select = False
    
    current_object = bpy.data.objects['Podium']
    current_object.select = True
    
    bpy.context.scene.objects.active = current_object
    
    bpy.ops.object.modifier_add(type='BOOLEAN')
    
    
    bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
    bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["Cutaway"]    
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
    current_object = bpy.data.objects['Podium']
    current_object.select = False 
    
    current_object = bpy.data.objects['Cutaway']
    current_object.select = True
    bpy.ops.object.delete(use_global=False)
    
    
    
    steps_no = random.randint(3,8)
    step_height = height * 2
    
    

    bpy.ops.mesh.archimesh_stairs(step_num = steps_no,height = step_height/(steps_no + 1),
    depth=(length-length_offset)/steps_no,back=False,thickness=0,front_gap=0)
    bpy.context.object.location = (locX,locY ,locZ - height)
    
    bpy.context.object.rotation_euler[2] = 3.14159

    bpy.ops.transform.resize(value = (width*2,length*2,1))
    
    



        
        

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


# Clear the scene: remove existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()




# Add a sun
sun = bpy.ops.object.lamp_add(type='SUN', location = (-20, 2, 20))
bpy.context.selected_objects.clear()
bpy.context.selected_objects.append(sun)
bpy.context.object.rotation_euler = mathutils.Euler((-0.7, -0.7, 0), 'XYZ')
bpy.context.object.data.shadow_method = 'RAY_SHADOW'
bpy.context.object.data.energy = 0.70



# And some ambient light
bpy.context.scene.world.light_settings.use_environment_light = True
bpy.context.scene.world.light_settings.environment_energy = 0.3






temple()    



#Render.render((15, 10, 8), (0, 0, 3), '//render.png')