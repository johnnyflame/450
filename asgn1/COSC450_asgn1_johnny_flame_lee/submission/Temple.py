import imp
import bpy
import Init
import random
import bmesh
import mathutils
import Render 
imp.reload(Render)





def main():

    # Set up lighting and camera
    setup()    


    # demonstrating the creation of a temple
    temple_1 = create(10,10,10,"temple") 
    # A temple can be moved once created
    temple_1.location = (0, 0, 0)
      
    # Render the scene
    Render.render((15, 10, 8), (0, 0, 3), '//render.png')
    
    
    








# These textures are procedurally generated.
# Sampled the example code here. 
def procedural_material(name, colour):
    # Shade is a brighter version of colour
    # Made by multiplying all of colour values by 1.2
    shade = list(map(lambda x: x*1.2, colour))
    
    
    #Texture type is randomly selected out of a list of appropriate patterns
    texture_type = random.choice(['NOISE','MUSGRAVE',"MARBLE","CLOUDS"])
    
    # A noise texture
    tex = bpy.data.textures.new(name+'_tex', type=texture_type)
    
    # Basic material
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = colour
    mat.specular_intensity =  0.3
    
    # And add the texture with colour etc.
    matTex = mat.texture_slots.add()
    matTex.texture = tex;
    matTex.mapping = 'SPHERE'
    matTex.scale[2] = 5;
    matTex.color = shade;
    
    matTex.blend_type = 'SCREEN'

    return mat
    


def setup():
    """Clear the scene then set up materials, lights, etc."""
        
    # Remove existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    sun_energy = random.uniform(0.5,0.9)

    # Add a sun
    sun = bpy.ops.object.lamp_add(type='SUN', location = (-20, 2, 20))
    bpy.context.selected_objects.clear()
    bpy.context.selected_objects.append(sun)
    bpy.context.object.rotation_euler = mathutils.Euler((-0.7, -0.7, 0), 'XYZ')
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
    bpy.context.object.data.energy = sun_energy
    bpy.context.object.data.color = (1,random.uniform(0.2,0.55),random.uniform(0.1,0.3))


    # And some ambient light
    bpy.context.scene.world.light_settings.use_environment_light = True
    bpy.context.scene.world.light_settings.environment_energy = 1 - sun_energy
        





    




def create(xSize, ySize, height, name):
    """Create a building with the given dimensions and name"""
    

    # Create the ground where the temple sits, the ground also represents the area specified by user
    make_ground(xSize,ySize,height)
    
    
    # Create a temple.
    obj = temple(xSize,ySize,height,name)


    # Return the reference so that the building can be moved
    return obj





def make_ground(xSize,ySize,height):
    dimensions = (xSize,ySize,height)
    ground = bpy.ops.mesh.primitive_plane_add
    
    ground(location = (xSize*0.5,ySize*0.5,0))
    
    groundsize = [x * 0.5 for x in dimensions]
    bpy.ops.transform.resize(value = groundsize)
    bpy.context.selected_objects[0].name = "Ground"
    

    groundTexture = bpy.data.textures.new('groundTexture', type='IMAGE')
    
    groundimage = random.randint(0,8) 
     
    groundTexture.image = bpy.data.images.load('//materials/ground/' + str(groundimage) + '.jpg')

    # Make a new material with this texture
    groundMaterial = bpy.data.materials.new('groundMaterial')
    groundMaterial.specular_intensity = 0.0 # Not shiny

    # And add the texture to the material
    groundMatTex = groundMaterial.texture_slots.add()
    groundMatTex.texture = groundTexture
 #   groundMatTex.mapping = 'SPHERE'
    
    bpy.context.object.data.materials.append(groundMaterial)
    bpy.context.object.active_material.texture_slots[0].scale[0] = 1
    bpy.context.object.active_material.texture_slots[0].scale[1] = 1
    bpy.context.object.active_material.texture_slots[0].scale[2] = 1
 
    
        

def temple(xSize,ySize,height,name):
    
    bpy.ops.object.empty_add(location=(0,0,0))
    bpy.context.selected_objects[0].name = name
    axes = bpy.data.objects[name]
    
   
   
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
    

    # colours are precedurally generated. The spread between R,G and B is no larger than 20%, giving the building a mild look, avoiding any extreme colours. A boolean flag is used each time to determine whether to subtract or add to the previous colour.
    
    red = random.uniform(0.4,0.7)
    
    if bool(random.getrandbits(1)):
        green = red + red * random.uniform(0,0.18)
    else:
        green = red - red * random.uniform(0,0.18)
        
    if bool(random.getrandbits(1)):   
        blue = green + green * random.uniform(0,0.18)
    else:
        blue = green - green * random.uniform(0,0.18)
    
    temple_colour = (red,green,blue)
    
    
    podium_material = procedural_material('podium_skin',temple_colour)
    stair_material = procedural_material('stair_skin', temple_colour)
    temple_material = procedural_material('temple_skin', temple_colour)
    roof_material =   procedural_material('roof_skin', temple_colour)  
    dome_material =   procedural_material('dome_skin', (red, green, blue))  
    dome_roof_material = procedural_material('dome_roof_skin', (red, green, blue))
    
    column_material =  procedural_material('column_skin', (red, green, blue))  
    
    
    
    
    
    
    #######################################################################################################################
    ### This section is for randomized variables
    
    
    
    # Boolean flags with default values, chages with input dimensions.
    has_dome = False
    use_library = False
    is_fluted = False
    
    cap_height = random.uniform(0.1,0.5)
    cap_style = random.randint(0,20)
    flute_num = 8
    
    col_faces = random.randint(20,40)
    addendum_factor = random.uniform(0,0.3)
 
    # 25% chance that the temple will have a flat roof
    flat_top = random.uniform(0,1) < 0.25
    
    
    
    
     
    columns_per_shortedge = random.choice([2,4,6]) 
    columns_per_longedge =  random.randint(4,8)
    
    use_library = False
    
    
    #####################################################################################################################
    
    box_width = xSize
    box_length = ySize
    
    box_height = height
    
  

    # TODO: Currently the height shouldn't be greater than width, if it is, make the dome have extensions. 
    
    
    #NOTE: 1:1:0.7 seems to work quite well for a ratio
    
    if box_length/box_width >=1.5:
        columns_per_longedge =  random.randint(6,15)
    
    
    
   # make_ground(box_width,box_length,box_height)
   
    
                
    
    podium_x = box_width * 0.5
    podium_y = box_length * 0.5
    
    MAX_PODIUM_WIDTH = box_width * 0.5
    MAX_PODIUM_LENGTH = box_length * 0.5
    
    MAX_BUILDING_HEIGHT = box_height * 0.5
    available_height = MAX_BUILDING_HEIGHT
    
   
 
    
    
    
    podium_width = MAX_PODIUM_WIDTH * random.uniform(0.35,0.65)
    podium_length = MAX_PODIUM_LENGTH #parametise this, work out valid range
    
    podium_height = available_height * random.uniform(0.05,0.20)#parametise this, work out a range.    
    available_height -= podium_height 
    
    
   
    
    #Decision making for dome using random number  
    dome_generator = random.uniform(0,1)
    
    # If the length of the input is drastically greater than width,dome is very likely.
    if box_length/box_width >= 1.5 and box_length/box_width <= 2:
        if dome_generator > 0.3:
            has_dome = True

    
    
    
    # If the building has a dome, a new list of parameters are needed to make it look sensible.
    if has_dome:
        
        length_factor = random.uniform(0.43,0.63)
        
        podium_width = MAX_PODIUM_WIDTH * random.uniform(0.35,0.8)
        podium_length = MAX_PODIUM_LENGTH * length_factor#parametise this, work out valid range
    
        
        podium_x = box_width * 0.5
        podium_y = box_length * 0.5 + MAX_PODIUM_LENGTH * (1-length_factor)
        
        # Dome Parameters
   
        dome_body_height = MAX_BUILDING_HEIGHT * 0.77 

        dome_body_radius = MAX_PODIUM_WIDTH
        
        dome_locX = podium_x 
        dome_locY = MAX_PODIUM_LENGTH - (MAX_PODIUM_LENGTH-dome_body_radius)
        dome_locZ = dome_body_height 
        
        
        #determines the ratio of the rest of the temple to dome
        available_height *= random.uniform(0.5,0.8)
        
     
            
            
    else:
        podium_width = MAX_PODIUM_WIDTH * random.uniform(0.5,0.8)
        
        side_stair_width = podium_length * 0.44
        side_stair_length = (MAX_PODIUM_WIDTH -podium_width) * 2
        side_stair_height = podium_height * 2
        side_stair_model = random.choice(['1','2'])
                
        side_stair_locY = MAX_PODIUM_LENGTH * 2 -  (MAX_PODIUM_LENGTH -side_stair_width)/1.8 
        side_stair_locZ = side_stair_height
        
        stair_generator = random.uniform(0,1)
        
        if stair_generator < 0.33 :
            side_stair_length *= 0.5
            # Weird magic number, not sure why this works, but it works.
            side_stair_locX = MAX_PODIUM_WIDTH + MAX_PODIUM_WIDTH
            left_side = True                        
            make_side_stairs(side_stair_locX,side_stair_locY,side_stair_locZ,side_stair_width,side_stair_length,side_stair_height,left_side,side_stair_model,mat=stair_material)
            left_side = False
            side_stair_locX = MAX_PODIUM_WIDTH - MAX_PODIUM_WIDTH
            make_side_stairs(side_stair_locX,side_stair_locY,side_stair_locZ,side_stair_width,side_stair_length,side_stair_height,left_side,side_stair_model,mat=stair_material)
            
        elif stair_generator >= 0.33 and stair_generator < 0.66:
            podium_x = podium_x + (MAX_PODIUM_WIDTH - podium_width)
            # Weird magic number, not sure why this works, but it works.
            side_stair_locX = MAX_PODIUM_WIDTH - MAX_PODIUM_WIDTH
            left_side = False
            make_side_stairs(side_stair_locX,side_stair_locY,side_stair_locZ,side_stair_width,side_stair_length,side_stair_height,left_side,side_stair_model,mat=stair_material)
        elif stair_generator >= 0.66 and stair_generator < 0.95:
            podium_x = podium_x - (MAX_PODIUM_WIDTH - podium_width)
            # Weird magic number, not sure why this works, but it works.
            side_stair_locX = MAX_PODIUM_WIDTH + MAX_PODIUM_WIDTH
            left_side = True
            make_side_stairs(side_stair_locX,side_stair_locY,side_stair_locZ,side_stair_width,side_stair_length,side_stair_height,left_side,side_stair_model,mat=stair_material)
        else:
            podium_width = MAX_PODIUM_WIDTH
            
            

            
        
        
        
        
        
         
         
         
   
            
    # Calculate the size of the column base, using a nested min function to eliminated edge cases.
    
    column_base_size = min((podium_width/8),min(podium_width/(columns_per_shortedge * 2),podium_length/(columns_per_longedge * 2))) # determins the size of the pillars
        
    column_base_height = podium_height / 10
    column_base_edge = column_base_size / 4.0
    
    
    available_height -= column_base_height
    
    
    #paramized according to building height
    
   
    column_pillar_height = available_height * random.uniform(0.60,0.85)
    
    available_height -= column_pillar_height 
    
     
    column_pillar_radius = column_base_size * 0.9   
    
    temple_body_width = podium_width * 0.90
    temple_body_length = podium_length * 0.5
    temple_body_height = column_pillar_height + column_base_height
    
    
    
    
    
    
    
    
    
    top_width = temple_body_width * 1.1
    top_length = podium_length * 0.75
    top_height = available_height * random.uniform(0.1,0.5)
    
    available_height -=top_height   
    roof_base_height = available_height * random.uniform(0.1,0.5)
    
    available_height -=roof_base_height 
    
    roof_width = podium_width * 1.1
    roof_length = top_length * 1.1
    roof_height = available_height
    
    

    
    
    
    stair_locX = podium_x
    stair_locY = podium_y + podium_length
    stair_locZ = podium_height
    
    stair_length = podium_length * 0.25 - column_base_size
    stair_width = podium_width * 0.31 
    stair_height = podium_height 
    
  
    
    
    
    door_width = temple_body_width * 0.5
    door_length = temple_body_length * 0.1
    door_height = temple_body_height * 0.8

    door_locX = podium_x
    door_locY = podium_y
    door_locZ = 2 * podium_height + door_height
    
    

    
    # Construction of the temple starts here.
    
    
    podium = bpy.ops.mesh.primitive_cube_add
    podium(location = (podium_x,podium_y,podium_height))   
    bpy.ops.transform.resize(value = (podium_width,podium_length,podium_height))
    bpy.context.selected_objects[0].name = "Podium"
    
    
    podium_skin = bpy.data.objects["Podium"]
    podium_skin.data.materials.append(podium_material);

    #podium_skin.data.materials.append(random.choice(building_materials))
    
    
    
    temple_body_locX = podium_x
    temple_body_locY = podium_y - podium_length/2 + column_pillar_radius
    temple_body_locZ = 2 * podium_height + temple_body_height
         
    temple_body = bpy.ops.mesh.primitive_cube_add
    temple_body(location = (temple_body_locX,temple_body_locY,temple_body_locZ))  
    bpy.ops.transform.resize(value = (temple_body_width,temple_body_length,temple_body_height))
    bpy.context.selected_objects[0].name = "temple_body"
    temple_body_skin = bpy.data.objects["temple_body"]
    temple_body_skin.data.materials.append(temple_material);
    
    make_door(door_locX,door_locY,door_locZ,door_width,door_length,door_height)
                
    
    top_locX = podium_x
    top_locY = podium_y - podium_length/4 + column_pillar_radius
    top_locZ = 2 * podium_height + 2*column_base_height + 2*column_pillar_height + top_height
    
    
    
    
    top = bpy.ops.mesh.primitive_cube_add
    top(location = (top_locX,top_locY,top_locZ))
    bpy.ops.transform.resize(value = (top_width,top_length,top_height))
    bpy.context.selected_objects[0].name = "Top"
    
    top_skin = bpy.data.objects["Top"]
    top_skin.data.materials.append(temple_material);

    roofbase = bpy.ops.mesh.primitive_cube_add
    roofbase(location = (podium_x,podium_y - podium_length/4 + column_pillar_radius,2 * podium_height + 2*column_base_height + 2*column_pillar_height + 2*top_height + roof_base_height))
    bpy.ops.transform.resize(value = (roof_width,roof_length,roof_base_height))
    bpy.context.selected_objects[0].name = "roofbase"
    
    roof_base_skin = bpy.data.objects["roofbase"]
    roof_base_skin.data.materials.append(temple_material);


    roof = bpy.ops.mesh.primitive_cube_add
    roof(location = (podium_x,podium_y - podium_length/4 + column_pillar_radius,2 * podium_height + 2*column_base_height + 2* column_pillar_height + 2*top_height + 2*roof_base_height+ 
    roof_height ))
    bpy.ops.transform.resize(value = (roof_width,roof_length,roof_height))
    bpy.context.selected_objects[0].name = "Roof"
    
    Roof_skin = bpy.data.objects["Roof"]
    Roof_skin.data.materials.append(roof_material);
   
    
 

   # Make roof by folding in vertices
    if not flat_top: 
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
        column_z_location =  2 * podium_height + 2 * column_base_height + column_pillar_height
        
        
                   
        #left-hand side column bases on long edge
        bpy.ops.mesh.primitive_cube_add(location = (podium_x + x_offset, podium_y + y_offset
        , base_z_location))        
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
        
        bpy.context.selected_objects[0].name = "Columns_longedge"        
        column_base_skin = bpy.data.objects["Columns_longedge"]
        column_base_skin.data.materials.append(column_material) 
       
        
        
        
        #RHS column bases    
        bpy.ops.mesh.primitive_cube_add(location = (podium_x - x_offset , podium_y +
        y_offset, base_z_location))        
        bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height)) 
        
        bpy.context.selected_objects[0].name = "Columns_longedge"        
        column_base_skin = bpy.data.objects["Columns_longedge"]
        column_base_skin.data.materials.append(column_material) 
          

        if use_library:
            
            stylized_pillars(podium_x + x_offset, podium_y + y_offset
            , base_z_location +column_base_height,height=(column_pillar_height*2),b_width=column_base_size,cap_height=cap_height,cap_style=cap_style,flute_num=flute_num,col_faces=col_faces,addendum_factor=addendum_factor,column_colour=temple_colour)
                
            stylized_pillars(podium_x - x_offset, podium_y + y_offset
            , base_z_location +column_base_height,height=(column_pillar_height*2),b_width=column_base_size,cap_height=cap_height,cap_style=cap_style,flute_num=flute_num,col_faces=col_faces,addendum_factor=addendum_factor,column_colour=temple_colour)
            

            
        else:
                
            #LHS columns 
            column = bpy.ops.mesh.primitive_cylinder_add        
            column(location = (podium_x + x_offset , podium_y + y_offset,
              column_z_location ))
            bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))
            
            bpy.context.selected_objects[0].name = "Columns_longedge_pillars"        
            column_skin = bpy.data.objects["Columns_longedge_pillars"]
            column_skin.data.materials.append(column_material)                  
            #RHS columns     
            column = bpy.ops.mesh.primitive_cylinder_add        
            column(location = (podium_x - x_offset , podium_y + y_offset,
              column_z_location ))
            bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))
            
            bpy.context.selected_objects[0].name = "Columns_longedge_pillars"        
            column_skin = bpy.data.objects["Columns_longedge_pillars"]
            column_skin.data.materials.append(column_material)  
            
            #bpy.ops.object.mode_set(mode = 'EDIT')   
        
     
    bpy.ops.object.mode_set(mode = 'OBJECT')      
    for s in range (0, columns_per_shortedge):
        
        x_offset=(podium_width - column_base_size - column_base_edge) - s * (2 * (podium_width - column_base_size - column_base_edge)/(columns_per_shortedge -1))
        y_offset = podium_length /2.0
        base_z_location = 2 * podium_height + column_base_height
        
        # This ensures no overlap of objects.
        
        if s != 0 and s != columns_per_shortedge-1:
        
            bpy.ops.mesh.primitive_cube_add(location = (podium_x + x_offset, podium_y + y_offset, base_z_location))
            bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
            
            bpy.context.selected_objects[0].name = "Columns_shortedge_base"        
            column_base_skin = bpy.data.objects["Columns_shortedge_base"]
            column_base_skin.data.materials.append(column_material);
                    
            bpy.ops.mesh.primitive_cube_add(location = (podium_x + x_offset, podium_y - (podium_length - column_base_size -column_base_edge), 2 * podium_height + column_base_height))               
            bpy.ops.transform.resize(value = (column_base_size,column_base_size,column_base_height))
            
            bpy.context.selected_objects[0].name = "Columns_shortedge_base"        
            column_base_skin = bpy.data.objects["Columns_shortedge_base"]
            column_base_skin.data.materials.append(column_material);
            
             
            
            #bpy.ops.object.mode_set(mode = 'EDIT')   
        
            if use_library:
                       
                stylized_pillars(podium_x + x_offset, podium_y + y_offset
                    , base_z_location + column_base_height,height=(column_pillar_height*2),b_width=column_base_size,cap_height=cap_height,cap_style=cap_style,flute_num=flute_num,col_faces=col_faces,addendum_factor=addendum_factor,column_colour=temple_colour)
                    
                stylized_pillars(podium_x + x_offset, podium_y - (podium_length - column_base_size -column_base_edge), base_z_location + column_base_height,height=(column_pillar_height*2),b_width=column_base_size,cap_height=cap_height,cap_style=cap_style,flute_num=flute_num,col_faces=col_faces,addendum_factor=addendum_factor,column_colour=temple_colour)
                
  
            else:    
                column = bpy.ops.mesh.primitive_cylinder_add
                column(location = (podium_x + (podium_width - column_base_size - column_base_edge) - s * (2 * (podium_width - column_base_size - column_base_edge)/(columns_per_shortedge -1)), podium_y + podium_length/2.0,  column_z_location))       
                bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))
                
                bpy.context.selected_objects[0].name = "Columns_shortedge_pillar"        
                column_skin = bpy.data.objects["Columns_shortedge_pillar"]
                column_skin.data.materials.append(column_material);
                     
                   
                column = bpy.ops.mesh.primitive_cylinder_add
                column(location = (podium_x + (podium_width - column_base_size - column_base_edge) - s * (2 * (podium_width - column_base_size - column_base_edge)/(columns_per_shortedge -1)), podium_y - (podium_length - column_base_size -column_base_edge),  column_z_location ))
                
                bpy.ops.transform.resize(value = (column_pillar_radius,column_pillar_radius,column_pillar_height))
                
                bpy.context.selected_objects[0].name = "Columns_shortedge_pillar"        
                column_skin = bpy.data.objects["Columns_shortedge_pillar"]
                column_skin.data.materials.append(column_material);
                
                     
    bpy.ops.object.mode_set(mode = 'OBJECT') 
    
    

    if has_dome:
        make_dome(dome_locX,dome_locY,dome_locZ,height=dome_body_height,radius=dome_body_radius,body_mat=dome_material,roof_mat=dome_roof_material)
        
    make_stairs(stair_locX,stair_locY,stair_locZ,stair_height,stair_width,stair_length,length_offset=column_base_size,mat=stair_material)
    
    
    #attach everything in the scene, apart from the sun and the camera, to an axis
    for obj in bpy.data.objects:
        if obj.name != "Sun" and obj.name != "Camera" and obj.name != "Sun.001" and obj.name != "temple":
            obj.parent = axes
            
            
            
            
    return axes

    

    


    


#Using an addon to generate beautiful, stylized columns, lots of parameters to randomize here.
def stylized_pillars(locX,locY,locZ,height,b_width,cap_height,cap_style,flute_num,col_faces,addendum_factor,column_colour):
    
    #things to add to the parameter:
    #flutes

    total_height = height
    row_height=height
    
 
    bpy.ops.mesh.add_column(Style="0",col_base=True,addendum=addendum_factor,col_plinth=False,base_type=7,col_taper=0.01,col_flutes=flute_num,base_width=b_width,col_radius=b_width,cap_width=b_width*1.2,row_height=height*0.2,col_blocks=5,col_cap=True,cap_type=cap_style,cap_height=cap_height,cap_faces=6,col_faces=col_faces)
    
    bpy.context.object.location = (locX,locY,locZ)
    bpy.context.object.dimensions[2] = height
    
    bpy.context.object.active_material.diffuse_color = column_colour

    

    

        


# The 'dome' part of the building, as seen in Pantheon.
def make_dome(locX,locY,locZ,height,radius,body_mat,roof_mat):
    
    dome_radius = radius * 0.95
    dome_height = height * 0.9
    dome_locZ = locZ + 0.8 * dome_height
    
    
    dome_body = bpy.ops.mesh.primitive_cylinder_add
    dome_body(location = (locX,locY,locZ))
    bpy.ops.transform.resize(value=(radius,radius,height))
    
    bpy.context.selected_objects[0].name = "Dome"        
    dome_skin = bpy.data.objects["Dome"]
    dome_skin.data.materials.append(body_mat)
    

    dome = bpy.ops.mesh.primitive_uv_sphere_add
    dome(location = (locX,locY,dome_locZ))
    bpy.ops.transform.resize(value=(dome_radius,dome_radius,dome_height))
    
    bpy.context.selected_objects[0].name = "Dome_Roof"        
    dome_roof_skin = bpy.data.objects["Dome_Roof"]
    dome_roof_skin.data.materials.append(roof_mat)
    
   
    
    
    
def make_stairs(locX,locY,locZ,height,width,length,length_offset,mat):
        
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
    
    
    
    steps_no = random.randint(4,9)
    step_height = height * 2
    stair_depth = (length)/(steps_no)
        
    bpy.ops.mesh.archimesh_stairs(step_num = steps_no,height = step_height/(steps_no),
    depth=stair_depth,back=False,thickness=0,front_gap=0)
    bpy.context.object.location = (locX,locY-stair_depth ,locZ - height * 1.1)
    
    bpy.context.object.rotation_euler[2] = 3.14159

    bpy.ops.transform.resize(value = (width*2,length*2,1))
    
    bpy.context.selected_objects[0].name = "stairs"        
    stairs_skin = bpy.data.objects["stairs"]
    stairs_skin.data.materials.append(mat)
    
     
    
    
def make_side_stairs(locX,locY,locZ,width,length,height,left_side,model,mat):
    steps_no = random.randint(4,8)
    step_height = height 
    stair_depth = (length)/(steps_no)
        
    bpy.ops.mesh.archimesh_stairs(model=model,curve=True,max_width=width,step_num = steps_no,height = step_height/(steps_no),
    depth=stair_depth,back=True,thickness=0,front_gap=0)
    
    bpy.context.object.location = (locX,locY ,locZ - height)
    
    if left_side:
        bpy.context.object.rotation_euler[2] = 1.5708
    else:
        bpy.context.object.rotation_euler[2] = 4.71239


    bpy.context.selected_objects[0].name = "side_stairs"        
    stairs_skin = bpy.data.objects["side_stairs"]
    stairs_skin.data.materials.append(mat)
    

  #  bpy.ops.transform.resize(value = (width*2,length*2,1))
    

def make_door(locX,locY,locZ,width,length,height):
    
    door_length = length
    print("making a door")
    
    cutaway = bpy.ops.mesh.primitive_cube_add    
    cutaway(location = (locX,locY + length * 0.5,locZ))
    bpy.ops.transform.resize(value = (width,length*1.4,height*1.1))
    bpy.context.selected_objects[0].name = "DoorCutaway"
        
    object = bpy.data.objects['DoorCutaway']
    object.select = False
    
    current_object = bpy.data.objects['temple_body']
    current_object.select = True
    
    bpy.context.scene.objects.active = current_object
    
    
    
    bpy.ops.object.modifier_add(type='BOOLEAN')
    
    
    bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
    bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["DoorCutaway"]    
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
    current_object = bpy.data.objects['temple_body']
    current_object.select = False 
    
    
    
    
     
    current_object = bpy.data.objects['DoorCutaway']
    current_object.select = True
    bpy.ops.object.delete(use_global=False)
    
    
 
  
    



#Testing code starts here


# Clear the scene: remove existing objects




main()








#change the render engine

