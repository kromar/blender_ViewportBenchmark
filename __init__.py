
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
        
    def set_view(degs, dist, angle, z):
        view_3d.view_location = (0.0 , 0.0 , z)
        view_3d.view_distance = dist
        eul = Euler((radians(angle), 0.0 , 0.0), 'XYZ')
        quat_ls = []
        
        for i in range(degs):
            eul.z = radians(i)
            quat = eul.to_quaternion()
            quat_ls.append(list(quat))
            
        return(quat_ls)

    def spin_view(quat_ls1, degs, startAngle):
        for i in range(degs):
            view_3d.view_rotation = quat_ls1[i+startAngle]
            ###########################################################
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            ###########################################################

    def refresh():
        view_3d.view_location = (0.0 , 0.0 , 1.0)
        view_3d.view_distance = 16
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
    def execute(self, context):
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
        bpy.context.user_preferences.view.show_object_info = False
        bpy.context.user_preferences.view.show_mini_axis = False
        bpy.context.user_preferences.view.show_view_name = False

        rabbit = bpy.data.objects['rabbit']
        body = bpy.data.objects['body']
        robot = bpy.data.objects['robot']

        #view_parameters
        rabbitView = [3.0, 90.0, 1.0]
        boltsView = [15.0, 90.0, 1.5]
        basemeshView = [12.0, 60.0, 1.0]
        robotView = [2.5, 90.0, 1.2]
        degs = 360
        timeout = 10 

        timeov1 = time.time()

        #set rabbit scene
        bpy.context.screen.scene = bpy.data.scenes['bbb']
        scene.layers[0] = True
        objOp.select_all(action='DESELECT')
        scene.objects.active = rabbit

        #rabbit - object mode - 4.2mln bench (5levels)
        refresh()
        view.viewport_shade = 'WIREFRAME'

        rabbit.modifiers.new(type='SUBSURF', name="sub")
        rabbit.modifiers.new(type='SIMPLE_DEFORM', name="dummy")
        rabbit.modifiers['dummy'].angle = 0
        rabbit.modifiers['sub'].levels = 5 #5

        refresh()
        fps10 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #objmode - wire - 4mln

        view.viewport_shade = 'SOLID'

        refresh()
        fps11 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #objmode - solid - 4mln

        #rabbit - edit mode 
        rabbit.modifiers['sub'].levels = 3
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        view.viewport_shade = 'WIREFRAME'
        objOp.mode_set(mode='OBJECT', toggle=False)
        objOp.modifier_apply(apply_as='DATA', modifier="sub")
        objOp.modifier_apply(apply_as='DATA', modifier="dummy")
        objOp.mode_set(mode='EDIT', toggle=False)

        refresh()
        fps12 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #editmode - wire - 265k

        view.viewport_shade = 'SOLID'
        view.show_occlude_wire = True

        refresh()
        fps13 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #editmode - hiddenwire - 265k

        view.show_occlude_wire = False
        meshOp.select_all(action='SELECT')

        refresh()
        fps14 = bench(degs, rabbitView[0], rabbitView[1], rabbitView[2], timeout) #editmode - solid - 265k

        #delete rabbit scene
        view.viewport_shade = 'WIREFRAME'
        meshOp.delete(type='VERT')
        objOp.mode_set(mode='OBJECT', toggle=False)
        rabbit.select = True
        objOp.delete()

        #set bolts scene
        bpy.context.screen.scene = bpy.data.scenes['bolts']
        scene.layers[0] = True
        objOp.select_all(action='DESELECT')

        for obj in bpy.data.scenes['bolts'].objects:
            bpy.context.scene.objects.active = obj
            
            obj.modifiers.new(type='SUBSURF', name="sub")
            obj.modifiers['sub'].levels = 2 #2
            
            objOp.modifier_apply(apply_as="DATA", modifier="sub")

        refresh()    
        fps20 = bench(degs, boltsView[0], boltsView[1], boltsView[2], timeout) #objectmode - wire - 8mln

        view.viewport_shade = 'SOLID'

        refresh()
        fps21 = bench(degs, boltsView[0], boltsView[1], boltsView[2], timeout) #objectmode - solid - 8mln

        #delete bolts scene
        view.viewport_shade = 'WIREFRAME'
        for obj in bpy.data.scenes['bolts'].objects:
            bpy.context.scene.objects.active = obj
            objOp.mode_set(mode='EDIT', toggle=False)
            meshOp.select_all(action='SELECT')
            meshOp.delete(type='VERT')
            objOp.mode_set(mode='OBJECT', toggle=False)
            obj.select = True
            objOp.delete()
            
        #set basemesh scene
        bpy.context.screen.scene = bpy.data.scenes['basemesh']
        scene.objects.active = body
        objOp.mode_set(mode='SCULPT', toggle=False)
        body.modifiers.new(type='MULTIRES', name="mul")
        for i in range(4):
            objOp.multires_subdivide(modifier="mul")
            
        view.viewport_shade = 'SOLID'
        view.use_matcap = True
        view.matcap_icon = '18'

        refresh()
        fps30 = bench(degs, basemeshView[0], basemeshView[1], basemeshView[2], timeout) #sculptmode - matcap - 6.5mln

        objOp.multires_subdivide(modifier="mul")

        refresh()
        fps31 = bench(degs, basemeshView[0], basemeshView[1], basemeshView[2], timeout) #sculptmode - matcap - 26mln

        objOp.modifier_remove(modifier="mul")
        view.use_matcap = False

        #set robot scene
        bpy.context.screen.scene = bpy.data.scenes['lab']
        objOp.select_all(action='DESELECT')
        scene.objects.active = robot

        view.viewport_shade = 'MATERIAL'

        refresh()
        fps40 = bench(degs, robotView[0], robotView[1], robotView[2], timeout)  #objectmode - material shaded - 225k

        view.viewport_shade = 'WIREFRAME'

        robot.modifiers.new(type='SUBSURF', name="sub")
        robot.modifiers.new(type='SIMPLE_DEFORM', name="dummy")
        robot.modifiers['dummy'].angle = 0
        robot.modifiers['sub'].levels = 2

        refresh()
        fps41 = bench(720, robotView[0], robotView[1], robotView[2], timeout)  #objectmode - wire - 1400k

        view.viewport_shade = 'SOLID'

        refresh()
        fps42 = bench(720, robotView[0], robotView[1], robotView[2], timeout)  #objectmode - solid - 1400k

        view.viewport_shade = 'MATERIAL'

        refresh()
        fps43 = bench(degs, robotView[0], robotView[1], robotView[2], timeout)  #objectmode - material - 1400k

        robot.modifiers.clear()

        timeov = round(time.time() - timeov1)
        timeovmin = int(timeov / 60)
        timeovsec = timeov - (timeovmin * 60)

        system = bpy.context.user_preferences.system
        version = str(bpy.app.version)
        hash = bpy.app.build_hash
        build_plat = bpy.app.build_platform
        build_date = bpy.app.build_date
        vbos = system.use_vertex_buffer_objects
        af0 = system.anisotropic_filter
        if af0 == "FILTER_0":
            af = "Off"
        else:
            af = af0[7:] + "x"
        draw_met = system.window_draw_method
        mul_sam = system.multi_sample
        mip = system.use_mipmaps
        mipgpu = system.use_gpu_mipmap

        result.clear()
        result.write("BLENDER VIEWPORT BENCHMARK\n\n")
        result.write("Blender version: %s\nRevision: %s , %s\nPlatform: %s\n\n" % (version, hash, build_date, build_plat))
        result.write("RESULTS\n\n")
        result.write("Object mode\n")
        result.write("Wireframe\n-rabbit (4150 polys with 5 levels subsurf*, 4.2mln polys, 8.5mln tris): %.2f fps\n-bolts (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps10, fps20, fps41))
        result.write("Solid\n-rabbit (5 levels subsurf*): %.2f fps\n-bolts (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps11, fps21, fps42))
        result.write("Material\n-robot (225k polys): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n\n" % (fps40, fps43))
        result.write("Edit mode\n")
        result.write("Wireframe\n-rabbit (265k polys, 530k tris): %.2f fps\n\n" % fps12)
        result.write("Hiddenwire\n-rabbit (265k polys, 530k tris): %.2f fps\n\n" % fps13)
        result.write("Solid\n-rabbit (265k polys, 530k tris): %.2f fps\n\n\n" % fps14)
        result.write("Sculpt mode\n")
        result.write("Solid matcap\n-basemesh (25k polys with 4 levels multires, 6.5mln polys, 13mln tris): %.2f fps\n-basemesh (5 levels multires, 26mln polys, 52mln tris): %.2f fps\n\n\n" % (fps30, fps31))
        result.write("Screen resolution : %s x %s\nVBOs: %s\nAnisotropic filter: %s\nDraw method: %s\nMulti sample: %s\nMipmaps: %s\nGPU Mipmap: %s\n" % (width, height, vbos, af, draw_met, mul_sam, mip, mipgpu))
        result.write("Overall Time (to run the benchmark): %i min %i sec\n\n" % (timeovmin, timeovsec))
        result.write("Average FPS:",((ps10+fps20+fps41+fps11+fps21+fps42+fps40+fps43+fps12+fps13+fps14+fps30+fps31)/13))
        result.write("*with dummy modifier: a simple deform modifier set with angle=0, in order not to leave subsurf at the bottom of the modifier stack. Otherwise VBOs would be disabled!!")

        bpy.ops.screen.back_to_previous()
        area.type = 'TEXT_EDITOR'



classes = (
    ) 


def register():
    for c in classes:
        bpy.utils.register_class(c)  

def unregister():
    [bpy.utils.unregister_class(c) for c in classes]

if __name__ == "__main__":
    register()

