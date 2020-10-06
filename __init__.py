
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
import time
from mathutils import Euler
from math import radians
from bpy.types import Operator 


bl_info = {
    "name": "Viewport Benchmark",
    "description": "Viewport Benchmark",
    "author": "Daniel Grauer",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
    "location": "Header",
    "category": "System",
    "wiki_url": "https://github.com/kromar/blender_ViewportBenchmark",
    "tracker_url": "https://github.com/kromar/blender_ViewportBenchmark/issues/new",
}


class VPB_OT_RunBenchmark(Operator): 
    """Run Viewport Benchmark.""" 
    bl_idname = "shelf_list.move_button" 
    bl_label = "Move a button in the list" 
        
    import bpy
import time
from mathutils import Euler
from math import radians
from bpy.types import Operator 


def set_view(degs, dist, angle, z):
    #view_3d.view_location = (0.0 , 0.0 , z)
    #view_3d.view_distance = dist
    eul = Euler((radians(angle), 0.0 , 0.0), 'XYZ')
    quat_ls = []
    
    for i in range(degs):
        eul.z = radians(i)
        quat = eul.to_quaternion()
        quat_ls.append(list(quat))
        
    return(quat_ls)

def spin_view(quat_ls1, degs, startAngle):
    for i in range(degs):
        #view_3d.view_rotation = quat_ls1[i+startAngle]
        ###########################################################
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        ###########################################################

def refresh():
    #view_3d.view_location = (0.0 , 0.0 , 1.0)
    #view_3d.view_distance = 16
    for i in range(5):
        ###########################################################
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        ###########################################################         
        
def bench(degs, dist, angle, z, timeout):    
    a = set_view(degs, dist, angle, z)
    t0 = t1 = time.time()
    degs1 = 0
    if degs < 15:
        step = degs
    else:
        step = 15
        
    for i in range(0, degs, step):
        spin_view(a, step, i)
        t1 = time.time()
        degs1 += step
        if t1 - t0 > timeout:
            break        
                    
    fps = 1 / ( (t1 - t0) / degs1)
    return(round(fps, 2))

    ###############################
    
def execute():
    area = bpy.context.area
    area.type = 'VIEW_3D'
    objOp = bpy.ops.object
    meshOp = bpy.ops.mesh
    result = bpy.data.texts['result']

    bpy.ops.screen.screen_full_area()
    view_3d = bpy.context.screen.areas[0].spaces.active.region_3d

    width = bpy.context.area.width - 1
    height = bpy.context.area.height - 1
    scene = bpy.context.scene
    view = bpy.context.screen.areas[0].spaces.active
    bpy.context.preferences.view.show_object_info = False
    bpy.context.preferences.view.show_gizmo = False
    bpy.context.preferences.view.show_view_name = False

    rabbit = bpy.data.objects['Suzanne']
    #body = bpy.data.objects['body']
    #robot = bpy.data.objects['robot']

    #view_parameters
    rabbitView = [3.0, 90.0, 1.0]
    degs = 360
    timeout = 10 

    timeov1 = time.time()

    #set rabbit scene
    bpy.context.window.scene = bpy.data.scenes['Scene']
    #scene.collection[0] = True
    objOp.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = rabbit

    #rabbit - object mode - 4.2mln bench (5levels)
    refresh()
    view.shading.type = 'WIREFRAME'

    rabbit.modifiers.new(type='SUBSURF', name="sub")
    rabbit.modifiers.new(type='SIMPLE_DEFORM', name="dummy")
    rabbit.modifiers['dummy'].angle = 0
    rabbit.modifiers['sub'].levels = 1 #5

    refresh()
    fps10 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #objmode - wire - 4mln

    view.shading.type = 'SOLID'

    refresh()
    fps11 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #objmode - solid - 4mln

    #rabbit - edit mode 
    rabbit.modifiers['sub'].levels = 1
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    view.shading.type = 'WIREFRAME'
    objOp.mode_set(mode='OBJECT', toggle=False)
    #objOp.modifier_apply(modifier="sub")
    #objOp.modifier_apply(modifier="dummy")
    objOp.mode_set(mode='EDIT', toggle=False)

    refresh()
    fps12 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #editmode - wire - 265k
    
    #view.shading.type = 'MATERIAL'
    
    
    view.shading.type = 'SOLID'
    view.shading.show_xray_wireframe = True
    refresh()
    fps13 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #editmode - hiddenwire - 265k


    view.shading.show_xray_wireframe = False
    #meshOp.select_all(action='SELECT')
    refresh()
    fps14 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #editmode - solid - 265k

    
 
    rabbit.modifiers.clear()
    
    #delete rabbit scene
    view.shading.type = 'SOLID'
    #meshOp.delete(type='VERT')
    objOp.mode_set(mode='OBJECT', toggle=False)
    rabbit.select_set(True)
    #objOp.delete()

        
        
        
        
    timeov = round(time.time() - timeov1)
    timeovmin = int(timeov / 60)
    timeovsec = timeov - (timeovmin * 60)

    system = bpy.context.preferences.system
    version = str(bpy.app.version)
    hash = bpy.app.build_hash
    build_plat = bpy.app.build_platform
    build_date = bpy.app.build_date
    #vbos = system.use_vertex_buffer_objects
    af0 = system.anisotropic_filter
    if af0 == "FILTER_0":
        af = "Off"
    else:
        af = af0[7:] + "x"
    draw_met = system.image_draw_method
    mul_sam = system.viewport_aa
    #mip = system.use_mipmaps
    #mipgpu = system.use_gpu_mipmap

    result.clear()
    result.write("BLENDER VIEWPORT BENCHMARK\n\n")
    result.write("Blender version: %s\nRevision: %s , %s\nPlatform: %s\n\n" % (version, hash, build_date, build_plat))
    result.write("RESULTS\n\n")
    result.write("Object mode\n")
    #result.write("Wireframe\n-rabbit (4150 polys with 5 levels subsurf*, 4.2mln polys, 8.5mln tris): %.2f fps\n-bolts (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps10, fps20, fps41))
    #result.write("Solid\n-rabbit (5 levels subsurf*): %.2f fps\n-bolts (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps11, fps21, fps42))
    #result.write("Material\n-robot (225k polys): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n\n" % (fps40, fps43))
    result.write("Edit mode\n")
    result.write("Wireframe\n-rabbit (265k polys, 530k tris): %.2f fps\n\n" % fps12)
    result.write("Hiddenwire\n-rabbit (265k polys, 530k tris): %.2f fps\n\n" % fps13)
    result.write("Solid\n-rabbit (265k polys, 530k tris): %.2f fps\n\n\n" % fps14)
    result.write("Sculpt mode\n")
    #result.write("Solid matcap\n-basemesh (25k polys with 4 levels multires, 6.5mln polys, 13mln tris): %.2f fps\n-basemesh (5 levels multires, 26mln polys, 52mln tris): %.2f fps\n\n\n" % (fps30, fps31))
    #result.write("Screen resolution : %s x %s\nVBOs: %s\nAnisotropic filter: %s\nDraw method: %s\nMulti sample: %s\nMipmaps: %s\nGPU Mipmap: %s\n" % (width, height, vbos, af, draw_met, mul_sam, mip, mipgpu))
    result.write("Overall Time (to run the benchmark): %i min %i sec\n\n" % (timeovmin, timeovsec))
    #result.write("Average FPS:",((ps10+fps20+fps41+fps11+fps21+fps42+fps40+fps43+fps12+fps13+fps14+fps30+fps31)/13))
    #result.write("Average FPS:",(fps11+fps12+fps13+fps14)/4)
    result.write("*with dummy modifier: a simple deform modifier set with angle=0, in order not to leave subsurf at the bottom of the modifier stack. Otherwise VBOs would be disabled!!")

    bpy.ops.screen.back_to_previous()
    area.type = 'TEXT_EDITOR'


execute()

classes = (
    ) 


def register():
    for c in classes:
        bpy.utils.register_class(c)  

def unregister():
    [bpy.utils.unregister_class(c) for c in classes]

if __name__ == "__main__":
    register()

