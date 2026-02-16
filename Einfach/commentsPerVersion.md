Version 2:

classes: 
Vec3: x, y, z
Ray: origin, direction
Material: color, diffuse, specular, reflection
Plane: point, normal, material
Light: position, intensity
Scene: Objects, lights
Raytracer: ambient light?

possible Pressure Points: Sphere.intersects() if ray not normalized could break (tbs -> no)

NO AMBIENT LIGHT?
-> PROBLEM -> Edit = Picture has Cornelbox

second sphere invis bc its white on a white background

-> No rays give light? Why?

render(): fov = pi/3 -> 1.04

ray = (0|0|1), ([-1,1]|[-1,1]|-1)

error:
Traceback (most recent call last):
  File "c:/Users/Leon/Documents/Semester_4/ML1/ProjektarbeitLLMs/Einfach/Edits/V2/V2codeEdited2.py", line 261, in <module>
    render()
  File "c:/Users/Leon/Documents/Semester_4/ML1/ProjektarbeitLLMs/Einfach/Edits/V2/V2codeEdited2.py", line 246, in render
    col = tracer.trace(ray, tracer.max_depth)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:/Users/Leon/Documents/Semester_4/ML1/ProjektarbeitLLMs/Einfach/Edits/V2/V2codeEdited2.py", line 184, in trace
    view = (-ray.direction).normalized()
            ^^^^^^^^^^^^^^
TypeError: bad operand type for unary -: 'Vec3'

    view = (ray.direction.__mul__(-1)).normalized()


problem seems to be line 173 being (0,0,0)
and lines 178 - 181 (178 + 179)


shadow_ray always skips to next pixel

Error has been found to be lines 178-181 (line 173 is irrelevant to outcome)

why? it always hits something
what does it hit?

all pxl do this
Shadow hit at <__main__.Vec3 object at 0x000001f3d806ebc0>

Problem: Walls and Spheres are both treated as objects in the World, so the shadow_ray always hits (since the walls are around the whole World) which means hit =/= none -> continue is forced pixel stays same as line 173.

Fix:

if shadow_hit:
  occluder = None
  for obj in self.scene.objects:
    h = obj.intersect(shadow_ray)
    if h and abs(h.t - shadow_hit.t) < 1e-6:
      occluder = obj
      break
    if occluder is not None and not isinstance(occluder, Plane):
      dist_to_light = (light.position - hit.point).norm()
      if shadow_hit.t < dist_to_light:
        continue

find out if hit is a wall (Plane) and if yes ignore the Shadow ray cast. If not use the ray.
