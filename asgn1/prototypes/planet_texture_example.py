import bpy      # Blender python libraries
import random   # Random numbers
import math     # Need some basic trigonometry for this example


# Set up background
world = bpy.context.scene.world
# Black background (it's spaaace)
world.zenith_color = (0,0,0)
world.horizon_color = (0,0,0)
# Add some ambient lighting (artistic, not realistic)
world.light_settings.use_environment_light = True
world.light_settings.environment_energy = 0.1

# Layer control. The sun is in a separate layer to the planets
# this allows me to put a point light source inside the sun.
# This light affects the planetLayer, but not the sunLayer, so the
# surface of the sun doesn't cast a shadow.
planetLayer = tuple(i == 0 for i in range(0,20))
sunLayer = tuple(i == 1 for i in range(0,20))

# Start with the sun layer and clear it out
bpy.data.scenes[0].layers = sunLayer
bpy.ops.object.select_pattern()
bpy.ops.object.delete()

# A material for the sun - bright, radient, and a little bit yellow
sunMaterial = bpy.data.materials.new("sunMaterial")
sunMaterial.diffuse_color = (1.0,1.0,0.9)
sunMaterial.diffuse_shader = 'LAMBERT'
sunMaterial.diffuse_intensity = 1.0
sunMaterial.emit = 1.0

# Add in a sphere for the sun
bpy.context.scene.cursor_location=(0,0,0)
sun = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4)
# Select the sphere we've just added
bpy.context.selected_objects.clear()
bpy.context.selected_objects.append(sun)
# And update its properties
bpy.context.selected_objects[0].name = 'Sun'
bpy.ops.transform.resize(value=(3, 3, 3))
bpy.ops.object.shade_smooth()
# Including its material
bpy.context.object.data.materials.append(sunMaterial)

# Switch to planet layer and clean it out
bpy.data.scenes[0].layers = planetLayer
bpy.ops.object.select_pattern()
bpy.ops.object.delete()

# A texture for rocky planets
# This is loaded from file, and wrapped around the sphere.
# The actual texture is of Mercury, not that it really matters
planetTexture = bpy.data.textures.new('planetTexture', type='IMAGE')
planetTexture.image = bpy.data.images.load('//mercury.png')

# Make a new material with this texture
planetMaterial = bpy.data.materials.new('planetMaterial')
planetMaterial.specular_intensity = 0.0 # Not shiny

# And add the texture to the material
planetMatTex = planetMaterial.texture_slots.add()
planetMatTex.texture = planetTexture
planetMatTex.mapping = 'SPHERE'

# Textured for gas planets
# These textures are procedurally generated.
# They're basically noise, but stretched to give a stripy effect
# We can specify a colour, which makes for a bit of variety as well
def makeGasMaterial(name, colour):
    # Shade is a darker version of colour
    # Made by multiplying all of colour values by 0.5
    shade = list(map(lambda x: x*0.5, colour))
    
    # A noise texture
    tex = bpy.data.textures.new(name+'_tex', type='STUCCI')
    tex.noise_scale = 0.5
    
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
    return mat
    

# Add a random number of planets
numPlanets = random.randint(4, 10)

for p in range(1, numPlanets):
    # Make a new planet
    planet =  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3)
    bpy.context.selected_objects.clear()
    bpy.context.selected_objects.append(planet)
    bpy.context.selected_objects[0].name =  'Planet_' + str(p)

    # Figure out where to put it
    orbitalRadius = pow(p,1.5)*2 + 3
    angle = random.uniform(0, 2*math.pi)
    bpy.ops.transform.translate(value=(orbitalRadius*math.sin(angle), orbitalRadius*math.cos(angle), 0))
    bpy.ops.object.shade_smooth()

    # Inner planets are small and rocky, outer ones are big and gaseous
    if (p < numPlanets/2):
        planetaryRadius = random.uniform(0.2, 0.7)
        bpy.ops.transform.resize(value=(planetaryRadius, planetaryRadius, planetaryRadius))
        bpy.context.object.data.materials.append(planetMaterial);
    else:
        planetaryRadius = random.uniform(0.5, 2)
        bpy.ops.transform.resize(value=(planetaryRadius, planetaryRadius, planetaryRadius))
        red = random.uniform(0.4,0.8)
        green = random.uniform(0.4,0.8)
        blue = random.uniform(0.4,0.8)
        newMaterial = makeGasMaterial('PlanetMaterial_' + str(p), (red, green, blue))
        bpy.context.object.data.materials.append(newMaterial);

# Add a light source at the centre of the Sun
# Note this is in the planet layer, not the sun layer
# because the light illuminates the planets, not the sun
light = bpy.ops.object.lamp_add(type='POINT', location=(0,0,0));
bpy.context.selected_objects.clear();
bpy.context.selected_objects.append(light)
bpy.context.selected_objects[0].name = 'SolarLight'
bpy.context.object.data.shadow_method = 'RAY_SHADOW'
bpy.context.object.data.use_shadow_layer = True
bpy.context.object.data.distance = 1000

# Make both layers visible
bpy.context.scene.layers[0] = True
bpy.context.scene.layers[1] = True

# Add in a camera above the sun, looking down
bpy.ops.object.camera_add(location=(0,0,100))
bpy.data.cameras[0].name = 'Camera'	

# Set this to be the active camera, and render the scene
bpy.context.scene.camera = bpy.data.objects['Camera']	
bpy.data.scenes['Scene'].render.filepath = '//render.png'	
bpy.ops.render.render(write_still = True)