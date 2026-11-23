"""Rebuild one original prop and studio photograph per study using bpy 4.5."""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PI = math.pi
TAU = math.tau
sin, cos = math.sin, math.cos
M = {}


def material(name, rgb, metal=0, rough=.42):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    color = tuple(int(rgb[i:i+2], 16)/255 for i in (0, 2, 4))
    rgba = tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in color)+(1,)
    m.diffuse_color = rgba
    bs = m.node_tree.nodes.get('Principled BSDF')
    for field, value in [('Base Color', rgba), ('Metallic', metal), ('Roughness', rough)]:
        bs.inputs[field].default_value = value
    M[name] = m


def finish(o, name, mat):
    o.name = name
    o.data.materials.append(M[mat])
    return o


def bevel(o, width):
    if width:
        m = o.modifiers.new('Machined edges', 'BEVEL')
        m.width, m.segments = width, 3
        m = o.modifiers.new('Face normals', 'WEIGHTED_NORMAL')
        m.keep_sharp = True
    return o


def box(name, p, dims, mat, b=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = bpy.context.object
    for v in o.data.vertices:
        for i in range(3):
            v.co[i] *= dims[i]
    return bevel(finish(o, name, mat), b)


def rod(name, start, end, radius, mat, n=24):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=radius, depth=(b-a).length,
                                        location=(a+b)/2)
    o = bpy.context.object
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    for face in o.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return bevel(finish(o, name, mat), min(radius*.1, .02))


def ring(name, p, radius, wire, mat, rot=(0,0,0), scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(location=p, major_radius=radius, minor_radius=wire,
                                     major_segments=36, minor_segments=8)
    o = bpy.context.object
    o.rotation_euler, o.scale = rot, scale
    for f in o.data.polygons:
        f.use_smooth = True
    return finish(o, name, mat)


def cable(name, points, width, mat):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions, c.bevel_depth, c.bevel_resolution = '3D', width, 3
    spline = c.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, v in zip(spline.points, points):
        p.co = (*v, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    return finish(o, name, mat)


def skin(name, bands, mat, b=0, smooth=False):
    """Loft a closed sequence of polygonal cross-sections."""
    n = len(bands[0])
    faces = [tuple(reversed(range(n)))]
    for j in range(len(bands)-1):
        for k in range(n):
            a = j*n+k
            t = j*n+(k+1)%n
            faces.append((a,t,t+n,a+n))
    faces.append(tuple(range((len(bands)-1)*n,len(bands)*n)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([v for band in bands for v in band],[],faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    for f in mesh.polygons:
        f.use_smooth = smooth
    return bevel(finish(o,name,mat), b)


def turned(name, profile, mat, n=64, flutes=0):
    return skin(name, [[(r*(1+flutes*cos(12*a))*cos(a),r*(1+flutes*cos(12*a))*sin(a),z)
                        for a in (TAU*k/n for k in range(n))] for z,r in profile],
                mat, smooth=True)


def lettering(name, s, p, size, mat, rotation=(PI/2,0,0)):
    c = bpy.data.curves.new(name, 'FONT')
    c.body, c.size, c.extrude, c.align_x = s, size, .001, 'CENTER'
    o = bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    o.location, o.rotation_euler = p, rotation
    return finish(o,name,mat)


def sealskin(name, sections, mat):
    bands = []
    for x,w,z0,z1 in sections:
        bands.append([(x,-w*.76,z0),(x,w*.76,z0),(x,w,z0+.08),(x,w*.92,z1-.05),
                      (x,w*.70,z1),(x,-w*.70,z1),(x,-w*.92,z1-.05),(x,-w,z0+.08)])
    return skin(name,bands,mat,.035)


def apex():
    box('Undertray',(0,0,.53),(4.18,1.42,.24),'rubber',.10)
    sealskin('Stamped monocoque',[(-2.30,.54,.60,.79),(-1.86,.86,.57,1.02),
             (-.64,.88,.54,1.15),(.56,.85,.54,1.13),(1.98,.76,.60,.98)],'bone')
    sealskin('Tinted polycarbonate', [(-1.23,.62,1.03,1.17),(-.62,.60,1.08,1.72),
             (.08,.56,1.10,1.74),(.46,.62,1.04,1.28)],'glass')
    box('Cab visor',(-.29,0,1.744),(.83,.94,.075),'bone',.07)
    for side in [-1,1]:
        y = side*.55
        rod('Windshield pillar',(-1.23,y,1.09),(-.65,y*.89,1.72),.035,'steel')
        rod('Door pillar',(.13,y,1.15),(.07,y*.88,1.72),.028,'steel')
        rod('Sill guard',(-1.08,side*.94,.55),(1.06,side*.94,.55),.056,'steel')
        for x in (-1.48,1.36):
            z=.54
            rod('Axle',(x,0,z),(x,side*.99,z),.10,'steel')
            rod('Wishbone',(x+.31,side*.50,.72),(x,side*.98,.51),.041,'steel')
            rod('Sidewall',(x,side*.86,z),(x,side*1.14,z),.50,'rubber',56)
            ring('Raised bead',(x,side*1.15,z),.36,.038,'rubber',(PI/2,0,0))
            rod('Wheel dish',(x,side*1.14,z),(x,side*1.158,z),.298,'steel',40)
            for k in range(8):
                a=k*TAU/8
                rod('Spoke',(x+.12*cos(a),side*1.18,z+.12*sin(a)),
                    (x+.29*cos(a+.22),side*1.17,z+.29*sin(a+.22)),.025,'bone')
            rod('Hub',(x,side*1.16,z),(x,side*1.205,z),.105,'oxide',8)
            for k in range(28):
                a=k*TAU/28
                o=box('Tread',(x+.499*sin(a),side*1.0,z+.499*cos(a)),(.069,.27,.035),'rubber',.009)
                o.rotation_euler=(0,a,.12*side)
    for y in [-.55,.55]:
        box('Lamp recess',(-2.18,y,.81),(.16,.25,.11),'rubber')
        box('Headlamp',(-2.255,y,.82),(.035,.20,.052),'ivory',.01)
    for i in range(6):
        box('Hood vent',(-1.80+i*.075,0,1.016+i*.012),(.027,.47,.027),'rubber',.007)
    box('Rear pallet',(1.14,0,1.095),(1.36,1.43,.13),'steel')
    box('Dispatch box',(1.12,0,1.38),(1.13,1.12,.53),'oxide',.08)
    box('Lid',(1.12,0,1.67),(1.19,1.18,.09),'oxide')
    for x in [.77,1.47]:
        box('Webbing across lid',(x,0,1.726),(.09,1.17,.025),'rubber',.008)
        for side in [-1,1]:
            box('Tie down',(x,side*.568,1.40),(.085,.025,.53),'rubber',.01)
            box('Cam buckle',(x,side*.59,1.39),(.12,.033,.095),'steel',.013)
    lettering('Pallet marking','POST / 17',(1.12,-.569,1.43),.105,'ivory')
    lettering('Callsign','17',(-.28,-.839,.80),.25,'rubber')
    return (-6,-8,4.45),(0,0,.93),5.75,'asphalt'


def vesper():
    turned('Fluted incense bowl',[(.08,.19),(.16,.29),(.23,.23),(.32,.31),(.49,.65),
           (.68,.83),(.86,.87),(.98,.81)],'bronze',96,.027)
    turned('Upper coal cup',[(.87,.81),(1.02,.83),(1.14,.68),(1.39,.47),(1.51,.21)],'patina')
    for z,r in [(.13,.26),(.34,.34),(.76,.86),(.91,.88),(1.02,.80),(1.5,.20)]:
        ring('Turned moulding',(0,0,z),r,.034,'brass')
    for j in range(12):
        a=j*TAU/12
        points=[]
        for k in range(17):
            t=k/16
            z=1.01+t*.46
            rad=.805-.50*t+.035*sin(PI*t)
            ang=a+.12*sin(PI*t)
            points.append((rad*cos(ang),rad*sin(ang),z))
        cable('Vault rib',points,.027,'brass')
        tip=rod('Crown finial',(.77*cos(a),.77*sin(a),.98),(.74*cos(a),.74*sin(a),1.16),.033,'brass',8)
    turned('Spire',[(1.49,.17),(1.57,.22),(1.64,.09),(1.75,.12),(1.88,.024)],'brass')
    for j in range(3):
        a=j*TAU/3+.26
        ring('Anchor eye',(.86*cos(a),.86*sin(a),.93),.093,.026,'brass',(PI/2,0,a))
        for k in range(15):
            t=k/14
            r=.86*(1-t)+.10*t
            ring('Interlocked chain',(r*cos(a),r*sin(a),1.04+1.66*t),.075,.015,
                 'brass',(PI/2,.38,a+k%2*PI/2),(1,1.34,1))
    ring('Carrying eye',(0,0,2.83),.17,.035,'bronze',(PI/2,0,.30))
    return (4,-6,3.45),(0,0,1.43),5.5,'plum'


def relay():
    box('Olive cast housing',(0,0,.83),(2.95,1.24,1.42),'olive',.15)
    box('Front gasket',(0,-.642,.84),(2.75,.09,1.22),'rubber',.10)
    box('Front plate',(0,-.698,.84),(2.64,.055,1.12),'olive',.07)
    for x in [-1.16,1.16]:
        for z in [.38,1.30]:
            rod('Captive screw',(x,-.735,z),(x,-.757,z),.047,'steel',8)
            box('Driver slot',(x,-.759,z),(.06,.006,.011),'rubber',.002)
    box('Dial bezel',(-.55,-.75,1.02),(.99,.10,.42),'rubber',.05)
    box('Dial glass',(-.55,-.809,1.02),(.88,.018,.30),'ivory',.02)
    for k in range(19):
        box('Tuning scale',(-.94+k*.043,-.82,1.045),(.008,.006,.045 if k%3 else .082),'rubber',0)
    box('Vernier needle',(-.46,-.824,1.02),(.018,.009,.23),'oxide',.002)
    lettering('Frequency strip','FIELD  /  09',(-.54,-.736,.68),.11,'ivory')
    for j in range(8):
        box('Speaker louvre',(.63,-.75,.79+j*.064),(.76-.02*abs(j-3),.07,.032),'rubber',.014)
    for x in [-.94,-.54,-.14,.68]:
        rod('Rotary selector',(x,-.735,.47),(x,-.879,.47),.101,'rubber',20)
        box('Index mark',(x,-.882,.515),(.015,.006,.055),'ivory',.002)
    cable('Grab handle',[(-.92,0,1.49),(-.92,0,1.88),(-.84,0,1.98),(.84,0,1.98),(.92,0,1.88),(.92,0,1.49)],.067,'steel')
    rod('Sleeved grip',(-.65,0,1.98),(.65,0,1.98),.087,'rubber')
    for j in range(3):
        rod('Telescopic mast',(-1.23-j*.11,.28,1.48+j*.44),(-1.34-j*.11,.28,1.94+j*.44),
            .043-.010*j,'steel')
    for x in [-1.25,1.25]:
        box('Rubber runner',(x,0,.11),(.32,1.08,.22),'rubber')
    return (4,-7,3.35),(0,0,1.32),5.8,'slate'


def pollen():
    for x in [-.88,.88]:
        box('Sled foot',(x,0,.14),(.32,1.82,.27),'wood',.06)
    box('Catch tray',(0,0,.35),(2.44,1.60,.20),'green',.09)
    for x in [-1.01,1.01]:
        box('Cast standard',(x,.08,1.48),(.16,.20,2.24),'green')
        for z in [.52,2.41]:
            rod('Cross pin',(x,-.07,z),(x,-.12,z),.068,'brass',6)
    box('Cast bridge',(0,.08,2.54),(2.30,.30,.23),'green',.06)
    for i in range(20):
        a=TAU*i/20
        stave=box('Beech stave',(.72*cos(a),.72*sin(a),.91),(.118,.202,.92),
                  ['wood','honey','beech'][i%3],.022)
        stave.rotation_euler.z=a
    for z in [.55,1.15]:
        ring('Basket hoop',(0,0,z),.782,.036,'steel')
    rod('Pressed platen',(0,0,1.27),(0,0,1.40),.65,'beech',48)
    rod('Press screw',(0,.08,1.40),(0,.08,2.91),.087,'steel')
    cable('Helical screw thread',[(.093*cos(k*.22),.08+.093*sin(k*.22),1.42+k*.0024)
                                  for k in range(605)],.018,'steel')
    rod('Thread collar',(0,.08,2.58),(0,.08,2.77),.14,'brass',12)
    rod('Crank lever',(-.66,.08,2.91),(.78,.08,2.91),.039,'steel')
    for x in [-.66,.78]:
        rod('Beech grip',(x,.08,2.86),(x,.08,3.02),.072,'wood')
    box('Press nameplate',(0,-.082,2.54),(.85,.025,.15),'ivory',.012)
    lettering('Press mark','PIP  /  No. 03',(0,-.098,2.505),.10,'green')
    box('Pour spout',(0,-.93,.36),(.23,.39,.08),'green',.025)
    return (4,-6.5,3.9),(0,0,1.47),5.7,'sage'


def scene(key):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M.clear()
    palette=[('rubber','252A30',0,.70),('steel','97A6AC',.77,.29),('bone','E4D7B8',.38,.30),
             ('glass','365265',.58,.15),('oxide','C35730',.32,.37),('ivory','F8DA9E',.09,.36),
             ('brass','C6A055',.78,.26),('bronze','93633D',.77,.36),('patina','366962',.66,.48),
             ('olive','626E57',.33,.48),('green','357365',.32,.36),('wood','9C5D39',0,.56),
             ('honey','D19A60',0,.5),('beech','B97D49',0,.56),('asphalt','41404C',0,.9),
             ('plum','4F3D48',0,.88),('slate','425353',0,.88),('sage','B7BEA4',0,.85)]
    for args in palette:
        material(*args)
    eye,aim,scale,floor={'apex':apex,'vesper':vesper,'relay':relay,'pollen':pollen}[key]()
    out=ROOT/'studies'/key/'model'
    out.mkdir(exist_ok=True)
    # Convert only asset geometry; the studio floor, lighting and camera are not shipped.
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.export_scene.gltf(filepath=str(out/'prop.glb'),export_format='GLB',use_selection=True)
    sc=bpy.context.scene
    sc.world=bpy.data.worlds.new('Softbox surround')
    sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.53,.54,.59,1)
    sc.world.node_tree.nodes['Background'].inputs[1].default_value=.48
    box('Studio ground',(0,0,-.12),(200,200,.22),floor,0)
    bpy.ops.object.camera_add(location=eye)
    cam=bpy.context.object
    cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'
    cam.data.ortho_scale=scale
    sc.camera=cam
    for p,power,size,col in [((-4,-4,7),740,5,(1,.88,.76)),((4,-1,5),580,4,(.80,.89,1)),
                             ((1,5,6),1050,3,(1,.93,.81))]:
        bpy.ops.object.light_add(type='AREA',location=p)
        lamp=bpy.context.object
        lamp.rotation_euler=(Vector(aim)-lamp.location).to_track_quat('-Z','Y').to_euler()
        lamp.data.energy,lamp.data.shape,lamp.data.size,lamp.data.color=power,'DISK',size,col
    sc.render.engine='CYCLES'
    sc.cycles.samples=20
    sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED'
    sc.render.threads=8
    sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage=1080,760,100
    sc.render.filepath=str(out/'studio.png')
    bpy.ops.render.render(write_still=True)


if __name__=='__main__':
    for study in sys.argv[1:] or ['apex','vesper','relay','pollen']:
        scene(study)
