import bpy

def clear_scene():
    """Clears the scene of all objects and materials"""
    # Clear the scene of all objects
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    # Clear the scene of all materials
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)
    return

