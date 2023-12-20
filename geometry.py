from geometry_script import *

@tree("Cube Tree")
def cube_tree(size: Vector = (1, 1, 1)):
    return cube(size=size)

@tree("repeat grid")
def repeat_grid(geometry: Geometry, width: Int, height: Int):
    g = grid(
        size_x=width, size_y=height,
        vertices_x=width, vertices_y=height
    ).mesh.mesh_to_points()
    i = ico_sphere(radius=0.5,subdivisions=3)
    
    g = g.instance_on_points(instance=i.mesh)
    
    g = g.set_shade_smooth()
    vector_math()
    return g

@tree("Instance Grid")
def instance_grid(instance: Geometry):
    """ Instance the input geometry on a grid """
    return grid().mesh_to_points().instance_on_points(instance=instance)

@tree("Cube Grid")
def cube_grid():
    """ Create a grid of cubes """
    return instance_grid(instance=ico_sphere(size=0.2))

@tree("Primitive Shapes")
def primitive_shapes():
    yield cube().mesh
    yield ico_sphere().mesh
    yield cylinder().mesh

@tree("Voxelize")
def voxelize(geometry: Geometry, resolution: Float = 0.2):
    return geometry.mesh_to_volume(
        interior_band_width=resolution,
        fill_volume=False
    ).distribute_points_in_volume(
        mode=DistributePointsInVolume.Mode.DENSITY_GRID,
        spacing=resolution
    ).instance_on_points(
        instance=cube(size=resolution)
    )
    
@tree("torus")
def makeTorus(geometry: Geometry,
            inner_radius: Float = 1.0,
            outer_radius: Float = 5.0,
            res: Int = 32
    ):
    a = curve_circle(radius=inner_radius,resolution=res)
    b = curve_circle(radius=outer_radius,resolution=res)
    c = curve_to_mesh(curve=b,profile_curve=a)
    return c.set_shade_smooth(geometry=geometry)

@tree("Voxel Grid")
def voxel_grid():
    return voxelize(geometry=ico_sphere(size=0.2))

@tree("City Builder")
def city_builder(
    geometry: Geometry,
    seed: Int,
    road_width: Float = 0.25,
    size_x: Float = 5, size_y: Float = 5, density: Float = 10,
    building_size_min: Vector = (0.1, 0.1, 0.2),
    building_size_max: Vector = (0.3, 0.3, 1),
):
    # Road mesh
    yield geometry.curve_to_mesh(profile_curve=curve_line(
        start=combine_xyz(x=road_width * -0.5),
        end=combine_xyz(x=road_width * 0.5)
    ))
    # Building points
    building_points = grid(size_x=size_x, size_y=size_y).mesh.distribute_points_on_faces(density=density, seed=seed).points
    road_points = geometry.curve_to_points(mode=CurveToPoints.Mode.EVALUATED).points
    # Delete points within the curve
    building_points = building_points.delete_geometry(
        domain=DeleteGeometry.Domain.POINT,
        selection=geometry_proximity(target_element=GeometryProximity.TargetElement.POINTS, target=road_points, source_position=position()).distance < road_width
    )
    # Building instances
    yield building_points.instance_on_points(
        instance=cube().transform(translation=(0, 0, 0.5)),
        scale=random_value(data_type=RandomValue.DataType.FLOAT_VECTOR, min=building_size_min, max=building_size_max, seed=seed),
    )

