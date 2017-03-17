import bpy

# Select and delete all objects so we have an empty scene
bpy.ops.object.select_pattern()
bpy.ops.object.delete()

# Make a material which we will use for the spheres
myMaterial = bpy.data.materials.new("glass")
myMaterial.diffuse_color = (1.0, 0.0, 0.0)
myMaterial.diffuse_shader = 'LAMBERT'
myMaterial.diffuse_intensity = 1.0
myMaterial.specular_color = (0.0, 1.0, 0.0)
myMaterial.specular_shader = 'COOKTORR'
myMaterial.specular_intensity = 0.75
myMaterial.specular_hardness = 15

# Loop to create 10 spheres
for s in range(-5, 5):
    # Create a sphere s units along the z-axis
    bpy.context.scene.cursor_location=(0,0,s)
    sphere = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5)
   
    # Select just the newly created sphere
    bpy.context.selected_objects.clear()
    bpy.context.selected_objects.append(sphere)
    
    # Flatten the sphere slightly
    bpy.ops.transform.resize(value=(1.0,1.0,0.5))

    # And apply the material
    bpy.context.object.data.materials.append(myMaterial)
    
# Add a light to the scene, so we can see something
bpy.ops.object.lamp_add(type='POINT', location = (15, 10, 5))

# And a camera so we can render an image
cam = bpy.ops.object.camera_add(location= (10, 10, 0), rotation=(1.5,0,2.5))
bpy.data.cameras[0].name = 'Camera'
bpy.context.scene.camera = bpy.data.objects['Camera']

# Render the image to a file
# Note that // at the start of the filename is the path to the .blend file 
bpy.data.scenes['Scene'].render.filepath='//rendered.png'
bpy.ops.render.render(write_still = True)