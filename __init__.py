
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
import bgl
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


def draw_button(self, context):
    #pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences    
    
    #if pref.button_toggle:
    if context.region.alignment == 'RIGHT':
        layout = self.layout
        row = layout.row(align=True)            
        row.operator(operator="viewport_benchmark.run", text="Run Benchmark", icon='SYSTEM', emboss=True, depress=False)
        

class VPB_OT_RunBenchmark(Operator): 
    """Run Viewport Benchmark""" 
    bl_idname = "viewport_benchmark.run" 
    bl_label = "Run Viewport Benchmark" 
        

    @classmethod
    def poll(cls, context):
        return context.selected_objects
        

    def set_view(self, view_3d, degrees, distance, angle, z):
        view_3d.view_location = (0.0 , 0.0 , z)
        view_3d.view_distance = distance
        eul = Euler((radians(angle), 0.0 , 0.0), 'XYZ')
        quat_ls = []
        
        for i in range(degrees):
            eul.z = radians(i)
            quat = eul.to_quaternion()
            quat_ls.append(list(quat))            
        return(quat_ls)


    def spin_view(self, view_3d, quat_ls1, step, angle):
        for i in range(step):
            view_3d.view_rotation = quat_ls1[i + angle]
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)


    def refresh(self, view_3d):
        view_3d.view_location = (0.0 , 0.0 , 1.0)
        view_3d.view_distance = 16
        for i in range(5):
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)  
            

    def bench(self, view_3d, degrees, distance, angle, z, timeout):    
        a = self.set_view(view_3d, degrees, distance, angle, z)
        t0 = t1 = time.time()
        degree_start = 0
        rotSteps = 15
        if degrees < rotSteps:
            step = degrees
        else:
            step = rotSteps
            
        for i in range(0, degrees, step):
            self.spin_view(view_3d, a, step, i)
            t1 = time.time()
            degree_start += step
            if t1 - t0 > timeout:
                break        
                        
        fps = 1 / ( (t1 - t0) / degree_start)
        return(round(fps, 2))

        
    def execute(self, context):        
        #create result file
        try:
            bpy.data.texts['Benchmark_Result']
        except:
            bpy.ops.text.new()
            bpy.data.texts['Text'].name = 'Benchmark_Result'
        result = bpy.data.texts['Benchmark_Result']

        #set 3d view as context to run benchmark
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'window': window, 'screen': screen, 'area': area}
                    bpy.ops.screen.screen_full_area(override)   

            objOp = bpy.ops.object
            meshOp = bpy.ops.mesh

            view_3d = bpy.context.screen.areas[0].spaces[0].region_3d
            #view_3d = bpy.context.screen.areas[0].spaces.active.region_3d
            
            width = bpy.context.area.width - 1
            height = bpy.context.area.height - 1
            scene = bpy.context.scene
            view = bpy.context.screen.areas[0].spaces.active
            bpy.context.preferences.view.show_object_info = False
            #bpy.context.preferences.view.show_gizmo = False
            bpy.context.preferences.view.show_view_name = False

            # specify benchmark target objects
            benchTarget =  bpy.data.objects[bpy.context.active_object.name]
            #body = bpy.data.objects['body']
            #robot = bpy.data.objects['robot']

            #view_parameters
            distance = 10.0
            angle = 80.0    
            z = 1.0       
            degrees = 360
            timeout = 10 
            mod_subdiv = 0
            timeov1 = time.time()
            #unlock fps
            user_fps = bpy.context.scene.render.fps
            bpy.data.scenes['Scene'].render.fps = 9999

            #set benchTarget scene
            bpy.context.window.scene = bpy.data.scenes['Scene']
            #scene.collection[0] = True
            objOp.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = benchTarget

            # benchmark: object mode 
            #self.refresh(view_3d)
            view.shading.type = 'WIREFRAME'
            benchTarget.modifiers.new(type='SUBSURF', name="subdiv")
            benchTarget.modifiers['subdiv'].levels = mod_subdiv
            self.refresh(view_3d)
            # view_3d, degrees, distance, angle, z, timeout): 
            fps10 = self.bench(view_3d, degrees, distance, angle, z, timeout)


            view.shading.type = 'SOLID'
            self.refresh(view_3d)
            fps11 = self.bench(view_3d, degrees, distance, angle, z, timeout)


            # benchmark: edit mode 
            benchTarget.modifiers['subdiv'].levels = mod_subdiv
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            view.shading.type = 'WIREFRAME'
            objOp.mode_set(mode='OBJECT', toggle=False)
            #objOp.modifier_apply(modifier="subdiv")
            objOp.mode_set(mode='EDIT', toggle=False)
            self.refresh(view_3d)
            fps12 = self.bench(view_3d, degrees, distance, angle, z, timeout)
            

            # benchmark: solid mode
            view.shading.type = 'MATERIAL'
            view.shading.type = 'SOLID'
            view.shading.show_xray_wireframe = True
            self.refresh(view_3d)
            fps13 = self.bench(view_3d, degrees, distance, angle, z, timeout)

            
            # benchmark: 
            view.shading.show_xray_wireframe = False
            meshOp.select_all(action='SELECT')
            self.refresh(view_3d)
            fps14 = self.bench(view_3d, degrees, distance, angle, z, timeout)

            
        
            benchTarget.modifiers.clear()
            
            #delete benchTarget scene
            view.shading.type = 'SOLID'
            #meshOp.delete(type='VERT')
            objOp.mode_set(mode='OBJECT', toggle=False)
            benchTarget.select_set(True)
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
            view_aa = system.viewport_aa
            #mip = system.use_mipmaps
            #mipgpu = system.use_gpu_mipmap

            result.clear()
            result.write("BLENDER VIEWPORT BENCHMARK\n=================\n")
            result.write("Blender version: %s\nRevision: %s , %s\nPlatform: %s\n\n" % (version, hash, build_date, build_plat))
            
            result.write("Graphics Card:\t%r\n" % bgl.glGetString(bgl.GL_RENDERER))
            result.write("Driver:\t%r\n" % (bgl.glGetString(bgl.GL_VERSION)))
            import platform

            result.write("CPU:\t%r\n%r\n\n" % (platform.processor(), platform.platform()))

            result.write("SCORES BENCHMARKS\n=================\n")
            #result.write("Object mode\n")
            #result.write("Wireframe\n (4150 polys with 5 levels subsurf*, 4.2mln polys, 8.5mln tris): %.2f fps\n (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps10, fps20, fps41))
            #result.write("Solid\n (5 levels subsurf*): %.2f fps\n (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps11, fps21, fps42))
            #result.write("Material\n (225k polys): %.2f fps\n (1.5mln polys*): %.2f fps\n\n\n" % (fps40, fps43))
        
            result.write("Edit mode\n")
            result.write("bench 1\n %.2f fps\n\n" % fps10)
            result.write("bench 1 \n %.2f fps\n\n" % fps11)
            result.write("Wireframe\n %.2f fps\n\n" % fps12)
            result.write("Hiddenwire\n %.2f fps\n\n" % fps13)
            result.write("Solid\n %.2f fps\n\n\n" % fps14)
            
            #result.write("Sculpt mode\n")
            #result.write("Solid matcap\n (25k polys with 4 levels multires, 6.5mln polys, 13mln tris): %.2f fps\n (5 levels multires, 26mln polys, 52mln tris): %.2f fps\n\n\n" % (fps30, fps31))
            #result.write("Screen resolution : %s x %s\nVBOs: %s\nAnisotropic filter: %s\nDraw method: %s\nMulti sample: %s\nMipmaps: %s\nGPU Mipmap: %s\n" % (width, height, vbos, af, draw_met, view_aa, mip, mipgpu))
        

            avg_fps = (fps10+ fps11 + fps12 + fps13 + fps14)/5
            total_fps = fps10+ fps11 + fps12 + fps13 + fps14
            result.write("SCORE TOTAL\n=================\n")
            result.write("FPS (avg/total): %.2f / %.2f\n" % (avg_fps, total_fps))
            result.write("Time: %i min %i sec\n" % (timeovmin, timeovsec))
            
            bpy.ops.screen.back_to_previous()
            #restore user render fps settings
            bpy.data.scenes['Scene'].render.fps = user_fps
            area.type = 'TEXT_EDITOR'
            
            return {'FINISHED'}


classes = (
    VPB_OT_RunBenchmark, 
    ) 


def register():
    for c in classes:
        bpy.utils.register_class(c)  
    bpy.types.TOPBAR_HT_upper_bar.prepend(draw_button)

def unregister():
    bpy.types.TOPBAR_HT_upper_bar.remove(draw_button)
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()

