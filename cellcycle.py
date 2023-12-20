import bpy
import math
from mathutils import Vector

# Function to create standard materials
def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    return mat

def hex_to_rgba(hex_color, alpha=1.0):
    """
    Convert a hex color string to a tuple of RGBA values.

    Parameters:
    hex_color (str): A hex color string (e.g., '#FF5733').
    alpha (float): Alpha (transparency) component, default is 1.0 (opaque).

    Returns:
    tuple: Tuple representing the RGBA color.
    """
    # Remove the '#' character and convert the string to upper case
    hex_color = hex_color.lstrip('#').upper()

    # Split the hex string into RGB components and convert to integers
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Scale the RGB values to the [0, 1] range and return with the alpha component
    return (r / 255.0, g / 255.0, b / 255.0, alpha)

def create_circular_gradient_material(name):
    # Create a new material
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Remove the default
    nodes.remove(nodes.get('Principled BSDF'))

    # Add necessary nodes
    tex_coord = nodes.new('ShaderNodeTexCoord')
    separate_xyz = nodes.new('ShaderNodeSeparateXYZ')
    math = nodes.new('ShaderNodeMath')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    material_output = nodes.get('Material Output')

    # Setup nodes
    math.operation = 'COSINE'
    #color_ramp.color_ramp.elements.new(0.5)
    #color_ramp.color_ramp.elements[0].color = (1, 0, 0, 1)  # Red
    #color_ramp.color_ramp.elements[1].color = (0, 1, 0, 1)  # Green
    #color_ramp.color_ramp.elements[2].color = (0, 0, 1, 1)  # Blue
    
    # Tricycle color palette
    ncolors = 8
    # Make sure there are exactly eight steps in the color_ramp and create new ones evenly spaced
    for i in range(ncolors - len(color_ramp.color_ramp.elements)):
        color_ramp.color_ramp.elements.new(1/(ncolors-1) * (i+1))

    color_ramp.color_ramp.elements[0].color = hex_to_rgba("#2E22EA")
    color_ramp.color_ramp.elements[1].color = hex_to_rgba("#9E3DFB")
    color_ramp.color_ramp.elements[2].color = hex_to_rgba("#F86BE2")
    color_ramp.color_ramp.elements[3].color = hex_to_rgba("#FCCE7B")
    color_ramp.color_ramp.elements[4].color = hex_to_rgba("#C4E416")
    color_ramp.color_ramp.elements[5].color = hex_to_rgba("#4BBA0F")
    color_ramp.color_ramp.elements[6].color = hex_to_rgba("#447D87")
    color_ramp.color_ramp.elements[7].color = hex_to_rgba("#2C24E9")

    # Link nodes
    links.new(tex_coord.outputs['Generated'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['X'], math.inputs[0])
    links.new(separate_xyz.outputs['Y'], math.inputs[1])
    links.new(math.outputs['Value'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

    return mat

# Function to create a unit circle ring
def create_circle_ring(major_radius=1, minor_radius=0.1):
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0), major_radius=major_radius, minor_radius=minor_radius)
    circle_ring = bpy.context.object
    #circle_ring_mat = create_gradient_material("Circle_Ring_Gradient")
    #circle_ring.data.materials.append(circle_ring_mat)
    # Apply smooth shading
    bpy.ops.object.shade_smooth()
    return circle_ring

# Function to create an arrow
#def create_arrow():
#    # Create an arrow with its tail at (0, 0, 0) and head on the ring
#    bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=1.2, location=(0.6, 0, 0), rotation=(0, 0, math.pi / 2))
#    arrow = bpy.context.object
#    arrow.rotation_mode = 'XYZ'
#    arrow_mat = create_material("Arrow_Material", (0.1, 0.2, 0.8, 1))  # Plastic blue shader
#    arrow.data.materials.append(arrow_mat)
#    return arrow

def create_arrow():
    # Shaft of the arrow (cylinder)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1, location=(0.5, 0, 0), rotation=(0, math.radians(90), 0))
    cylinder = bpy.context.object

    # Arrowhead (cone)
    bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=0.2, location=(1, 0, 0), rotation=(0, math.radians(90), 0))
    cone = bpy.context.object

    # Join cylinder and cone
    bpy.context.view_layer.objects.active = cylinder
    cylinder.select_set(True)
    cone.select_set(True)
    bpy.ops.object.join()

    # Apply material
    arrow = bpy.context.object
    arrow_mat = create_material("Arrow_Material", (0.1, 0.2, 0.8, 1))  # Plastic blue shader
    arrow.data.materials.append(arrow_mat)
    bpy.ops.object.shade_smooth()

    return arrow

# Function to create a particle that draws a line
def create_particle():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.05, location=(0, 0, 0))
    particle = bpy.context.object
    particle_mat = create_material("Particle_Material", (0.2, 0.2, 0.9, 1))  # Blue
    particle.data.materials.append(particle_mat)
    bpy.ops.object.shade_smooth()

    curve = bpy.data.curves.new('particle_path', 'CURVE')
    curve.dimensions = '3D'
    curve_obj = bpy.data.objects.new('particle_path_obj', curve)
    bpy.context.collection.objects.link(curve_obj)
    curve_obj_mat = create_material("Curve_Material", (1, 1, 1, 1))  # White
    curve_obj.data.materials.append(curve_obj_mat)
    bpy.ops.object.shade_smooth()

    # Add a Build modifier to the curve
    build_modifier = curve_obj.modifiers.new(name="Build", type='BUILD')
    build_modifier.frame_start = 1
    build_modifier.frame_duration = 360  # Set this to match your animation length

    return particle, curve_obj


# Function to set up the animation
def setup_animation(arrow, particle, curve_obj, rate_of_progression):
    frame_start = 1
    frame_end = 360  # Fixed end frame
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end

    # Ensure the curve is properly initialized
    curve_obj.data.splines.clear()  # Clear existing splines
    spline = curve_obj.data.splines.new(type='POLY')
    spline.points.add(frame_end)  # Points for each frame

    # Make sure the curve is visible and renderable
    curve_obj.data.bevel_depth = 0.01  # Give some thickness to the curve for visibility
    curve_obj.data.use_path = True  # Enable path

    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        angle = 2 * math.pi * frame / frame_end * rate_of_progression

        # Update arrow position and rotation
        arrow.location.x = math.cos(angle) * 0.6
        arrow.location.y = math.sin(angle) * 0.6
        arrow.rotation_euler[2] = angle

        # Update particle position
        particle.location.x = frame / frame_end * 10
        particle.location.y = math.sin(angle)

        # Update curve to follow particle
        spline.points[frame-1].co = (particle.location.x, particle.location.y, 0, 1)

        arrow.keyframe_insert(data_path="location", frame=frame)
        arrow.keyframe_insert(data_path="rotation_euler", frame=frame)
        particle.keyframe_insert(data_path="location", frame=frame)


# Function to add studio lighting
def add_studio_lighting():
    # Create a light data object
    light_data = bpy.data.lights.new(name="Studio_Light", type='AREA')
    light_data.energy = 1000  # Adjust the energy for desired intensity
    light_data.color = (0.8, 0.9, 1)  # Cool white light
    light_data.shape = 'RECTANGLE'
    light_data.size = 4  # Size of the light area

    # Create a new object with the light data
    light_object = bpy.data.objects.new(name="Studio_Light", object_data=light_data)
    bpy.context.collection.objects.link(light_object)

    # Position the light above the scene
    light_object.location = (0, 0, 5)
    light_object.rotation_euler[0] = math.radians(-90)  # Pointing downwards

    return light_object

def point_light_to_origin(light_obj):
    # Target position (origin)
    target_pos = Vector((0, 0, 0))

    # Direction from light to the target position
    direction = target_pos - light_obj.location
    direction.normalize()

    # Calculate the rotation angles
    rot_quat = direction.to_track_quat('-Z', 'Y')
    light_obj.rotation_euler = rot_quat.to_euler()

    return light_obj

def add_camera(height, scale=15):
    # Create the camera
    bpy.ops.object.camera_add(location=(4, 0, height))
    camera = bpy.context.object

    # Set camera to orthographic
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale  # Adjust based on your scene's scale

    # Point the camera directly downwards towards the XY plane
    camera.rotation_euler[0] = 0 #math.radians(-90)  # Rotate 90 degrees around the X-axis
    camera.rotation_euler[1] = 0
    camera.rotation_euler[2] = 0  # No Additional rotation around the Z-axis

    return camera

# Clear existing meshes and lights
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create objects and setup the scene
scene = bpy.context.scene

# Set Background color to black
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)


circle_ring = create_circle_ring()
circular_gradient_material = create_circular_gradient_material("CircularGradientMaterial")
circle_ring.data.materials.append(circular_gradient_material)

arrow = create_arrow()
particle, curve_obj = create_particle()

# Add camera and position it
camera = add_camera(height=15)

studio_light = add_studio_lighting()
point_light_to_origin(studio_light)


# Set up the animation
rate_of_progression = 4  # Adjust this value to change the rate of progression
setup_animation(arrow, particle, curve_obj, rate_of_progression)
