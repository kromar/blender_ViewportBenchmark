
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

if "bpy" in locals():
    import importlib
    importlib.reload(preferences)
else:
    from . import preferences
    
import bpy
import bgl
import time
from time import perf_counter 
import math
import mathutils
import importlib
from mathutils import Euler, Matrix
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


benchResults = {}


def draw_button(self, context):
    #pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences    
    
    #if pref.button_toggle:
    if context.region.alignment == 'RIGHT':
        layout = self.layout
        row = layout.row(align=True)  
               
        row.operator(operator="wm.modal_timer_operator", text="modal", icon='MONKEY', emboss=True, depress=False)
        row.operator(operator="viewport_benchmark.run", text="old", icon='MONKEY', emboss=True, depress=False)
        row.operator(operator="wm.benchmark", text="timer", icon='MEMORY', emboss=True, depress=False)
        


class BenchmarkOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"
    
    
    _view_3d = None
    _modal_timer = None
    _angle = 0 
    _bench_index = 0  

    _time_start = 0
    _report_bar_width = 60
    
    benchmarkList = ['WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED']

    """ @classmethod
    def poll(cls, context):
        return context.selected_objects   """
    
    def initializeView(self, context, pref):       
        view = bpy.context.screen.areas[0].spaces.active     
        self._view_3d.view_location = (0.0 , 0.0 , pref.view_z_pos)
        self._view_3d.view_distance = pref.view_distance 
        eul = Euler((math.radians(pref.view_angle), 0.0 , 0.0), 'XYZ')
        quat = eul.to_quaternion()         
        self._view_3d.view_rotation = quat

        #rendering configs
        print("benchamrk mode: ", self.benchmarkList[self._bench_index])
        view.shading.type = self.benchmarkList[self._bench_index]
        #start timer        
        self._time_start = time.time()
        return


    def restoreDefaults(self, context):
        #restore defaults
        """ bpy.context.space_data.show_gizmo = True
        bpy.context.space_data.overlay.show_overlays = True   
        if bpy.ops.screen.back_to_previous.poll():
        bpy.ops.screen.back_to_previous() """
        return


    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._modal_timer)
        bpy.ops.screen.back_to_previous()
        return {'CANCELED'}


    def execute(self, context):        
        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        wm = context.window_manager
        self._modal_timer = wm.event_timer_add(1/pref.max_render_fps, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def runBenchmark(self, context, pref):           
        #run rotation
        eul = self._view_3d.view_rotation.to_euler()            
        eul.z = eul.z + math.radians(pref.angle_steps)
        self._view_3d.view_rotation = eul.to_quaternion()

        #calculate fps
        if pref.is_benchmark:
            #print("angle: ", self._angle)
            self._angle += pref.angle_steps

            if self._angle == int(360 * pref.loops):
                time_stop = time.time() 
                #print(self._angle, "\n", self._time_start, "\n", time_stop, "\n", (time_stop-self._time_start))
                fps = round((1 / ( (time_stop-self._time_start)/int(360 * pref.loops))), 4)
                print("FPS: ", fps)                
                
                #context.window_manager.event_timer_remove(self._modal_timer) 
                self._time_start = 0
                self._angle = 0                
                self._bench_index += 1
                
                print(self._bench_index, len(self.benchmarkList))
                if self._bench_index == len(self.benchmarkList): 
                    bench_finish = True
                else:
                    bench_finish = False                 
                    
                return bench_finish
        else:            
            pass

    def modal(self, context, event):
        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        
        if event.type in {'ESC'}:
            self.cancel(context)
            context.window_manager.event_timer_remove(self._modal_timer)
            return {'CANCELLED'}


        if event.type == 'TIMER': 
            #preapre setting for benchmark
            if self._time_start == 0:
                self.initializeView(context, pref)

            #initialize benchmark
            bench_finish = self.runBenchmark(context, pref)
            if bench_finish:
                return {'FINISHED'}

        if pref.is_interactive:
            return {'PASS_THROUGH'}
        else:
            return {'RUNNING_MODAL'}




    def invoke(self, context, event): 

        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':             
                    self._view_3d = area.spaces.active.region_3d
                    override = {'window': window, 'screen': screen, 'area': area}                    
                    bpy.ops.screen.screen_full_area(override)       
                    """ bpy.context.space_data.show_gizmo = False
                    bpy.context.space_data.overlay.show_overlays = False   """
        
        bpy.data.scenes['Scene'].render.fps = pref.max_render_fps
                
        self.execute(context)
        return {'RUNNING_MODAL'}



class AppTimersOperator(bpy.types.Operator):
    """Run Benchmark"""
    bl_idname = "wm.benchmark"
    bl_label = "Run Benchmark"

    _counter = 0
    _modal_timer = None
    _view_3d = None
    
    _report_bar_width = 60
    #_angle_target = int(360 * 10)

    def runbenchmark(self):
        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        eul = self._view_3d.view_rotation.to_euler()
        eul.z = eul.z + math.radians(pref.angle_steps)
        quat = eul.to_quaternion()         
        self._view_3d.view_rotation = quat
        
        self._counter += pref.angle_steps
        #print(self._counter)

        if self._counter == int(360 * pref.loops):            
            bpy.ops.screen.back_to_previous()
            return None            
        return 1/pref.max_render_fps

        
    def execute(self,context):  
        bpy.app.timers.register(self.runbenchmark)          
        
        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        if pref.is_interactive:
            return {'PASS_THROUGH'}
        else:
            return {'RUNNING_MODAL'}


    def invoke(self, context, event):     
        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences  
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'window': window, 'screen': screen, 'area': area}
                    bpy.ops.screen.screen_full_area(override)                     

        self._view_3d = bpy.context.screen.areas[0].spaces[0].region_3d            
        bpy.data.scenes['Scene'].render.fps = pref.max_render_fps

        #initialize view
        self._view_3d.view_location = (0.0 , 0.0 , pref.view_z_pos)
        self._view_3d.view_distance = pref.view_distance 
        eul = Euler((math.radians(pref.view_angle), 0.0 , 0.0), 'XYZ')
        quat = eul.to_quaternion()         
        self._view_3d.view_rotation = quat

        self.execute(context)
        return {'RUNNING_MODAL'}
        


class VPB_OT_RunBenchmark(Operator): 
    """Run Viewport Benchmark""" 
    bl_idname = "viewport_benchmark.run" 
    bl_label = "Run Viewport Benchmark" 
        

    @classmethod
    def poll(cls, context):
        return context.selected_objects        

    def set_view(self, view_3d, deg, distance, angle, z_pos):
        view_3d.view_location = (0.0 , 0.0 , z_pos)
        view_3d.view_distance = distance
        eul = Euler((math.radians(angle), 0.0 , 0.0), 'XYZ')
        quat_ls = []        
        for i in range(deg):
            print("\n",eul, eul.z)
            eul.z = math.radians(i)
            quat = eul.to_quaternion()
            print(eul, eul.z, quat)
            quat_ls.append(list(quat))            
        return(quat_ls)

    def spin_view(self, view_3d, quat_ls1, step, angle):
        for i in range(step):
            #print((i + angle), step, quat_ls1[i + angle])
            view_3d.view_rotation = quat_ls1[i + angle]
            if bpy.ops.wm.redraw_timer.poll():                
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)      

    def bench(self, view_3d, deg, distance, angle, z_pos):    
        a = self.set_view(view_3d, deg, distance, angle, z_pos)
        time_start = time_stop = time.time()
        degree_start = 0
        rotSteps = 15
        if deg < rotSteps:
            step = deg
        else:
            step = rotSteps
            
        for i in range(0, deg, step):
            self.spin_view(view_3d, a, step, i)
            time_stop = time.time()
            degree_start += step
                        
        fps = 1 / ( (time_stop - time_start) / degree_start)
        return(round(fps, 2))

        
    def execute(self, context):       
        pref = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
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
            distance = 15.0
            angle = 80.0    
            z_pos = 4.0      
            deg = int(360 * pref.loops)

            mod_subdiv = 0
            benchtime = time.time()
            #unlock fps
            user_fps = bpy.context.scene.render.fps
            bpy.data.scenes['Scene'].render.fps = 9999

            #set benchTarget scene
            bpy.context.window.scene = bpy.data.scenes['Scene']
            #scene.collection[0] = True
            #objOp.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = benchTarget

            # benchmark: wireframe
            #benchTarget.modifiers.new(type='SUBSURF', name="subdiv")
            #benchTarget.modifiers['subdiv'].levels = mod_subdiv
            # view_3d, deg, distance, angle, z_pos): 
            view.shading.type = 'WIREFRAME'
            view.shading.show_xray_wireframe = True
            fps10 = self.bench(view_3d, deg, distance, angle, z_pos)

            # benchmark xray: 
            view.shading.type = 'WIREFRAME'
            #meshOp.select_all(action='SELECT')
            view.shading.show_xray_wireframe = False
            fps14 = self.bench(view_3d, deg, distance, angle, z_pos)

            # benchmark: solid 
            view.shading.type = 'SOLID'
            fps11 = self.bench(view_3d, deg, distance, angle, z_pos)


            # benchmark: material 
            #benchTarget.modifiers['subdiv'].levels = mod_subdiv
            #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            view.shading.type = 'MATERIAL'
            view.shading.use_scene_lights_render = True
            view.shading.use_scene_world_render = True
            #objOp.mode_set(mode='OBJECT', toggle=False)
            #objOp.modifier_apply(modifier="subdiv")
            #objOp.mode_set(mode='EDIT', toggle=False)
            fps12 = self.bench(view_3d, deg, distance, angle, z_pos)
            

            # benchmark: rendered
            view.shading.type = 'RENDERED'
            view.shading.use_scene_lights_render = True
            view.shading.use_scene_world_render = True
            #view.shading.type = 'SOLID'
            #view.shading.show_xray_wireframe = True
            fps13 = self.bench(view_3d, deg, distance, angle, z_pos)

                   
            #benchTarget.modifiers.clear()
            
            #delete benchTarget scene
            view.shading.type = 'SOLID'
            #meshOp.delete(type='VERT')
            #objOp.mode_set(mode='OBJECT', toggle=False)
            benchTarget.select_set(True)
            #objOp.delete()


            writeReport(self, benchtime, fps10, fps11, fps12, fps13, fps14)
            
            bpy.ops.screen.back_to_previous()
            #restore user render fps settings
            bpy.data.scenes['Scene'].render.fps = user_fps
            area.type = 'TEXT_EDITOR'

            return {'FINISHED'}


def writeReport(self, benchtime, fps10, fps11, fps12, fps13, fps14):
    timeov = round(time.time() - benchtime)
    timeovmin = int(timeov / 60)
    timeovsec = timeov - (timeovmin * 60)

    score_max = 60
    fps_highscore = 512   
     
    #create result file
    try:
        bpy.data.texts['Benchmark_Result']
    except:
        bpy.ops.text.new()
        bpy.data.texts['Text'].name = 'Benchmark_Result'
    result = bpy.data.texts['Benchmark_Result']


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

    #report System specs
    result.clear()
    result.write("BLENDER VIEWPORT BENCHMARK\n%s\n" % ("="*score_max))
    result.write("Blender version: %s\nRevision: %s , %s\nPlatform: %s\n\n" % (version, hash, build_date, build_plat))

    import platform
    platformProcessor = platform.processor()
    result.write("CPU:\t%r\n" % (platformProcessor))
    result.write("GPU:\t%r\n" % bgl.glGetString(bgl.GL_RENDERER))
    result.write("GPU Driver:\t%r\n\n" % (bgl.glGetString(bgl.GL_VERSION)))
    
    result.write("test %s %s" % (bpy.app.debug_gpumem, bpy.app.build_system))
    #cpu = cpuinfo.get_cpu_info()['brand']
    #result.write("CPU:\t%r\n%r\n\n" % (cpu))
    #import _cycles
    #print(_cycles.get_device_types())
    result.write("SCORES BENCHMARKS\n%s\n" % ("="*score_max))
    #result.write("Object mode\n")
    #result.write("Wireframe\n (4150 polys with 5 levels subsurf*, 4.2mln polys, 8.5mln tris): %.2f fps\n (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps10, fps20, fps41))
    #result.write("Solid\n (5 levels subsurf*): %.2f fps\n (8.3mln polys, 16.6mln tris): %.2f fps\n-robot (1.5mln polys*): %.2f fps\n\n" % (fps11, fps21, fps42))
    #result.write("Material\n (225k polys): %.2f fps\n (1.5mln polys*): %.2f fps\n\n\n" % (fps40, fps43))

            

    result.write("Edit mode\n")
    result.write("bench 1\n %.2f fps\n" % fps10)
    bench_score = int(score_max/fps_highscore*fps10)
    result.write("%s%s|\n\n" % (("#"*bench_score),("-"*(score_max-bench_score))))

    result.write("bench 1 \n %.2f fps\n" % fps11)
    bench_score = int(score_max/fps_highscore*fps11)
    result.write("%s%s|\n\n" % (("#"*bench_score),("-"*(score_max-bench_score))))

    result.write("Wireframe\n %.2f fps\n" % fps12)
    bench_score = int(score_max/fps_highscore*fps12)
    result.write("%s%s|\n\n" % (("#"*bench_score),("-"*(score_max-bench_score))))

    result.write("Hiddenwire\n %.2f fps\n" % fps13)
    bench_score = int(score_max/fps_highscore*fps13)
    result.write("%s%s|\n\n" % (("#"*bench_score),("-"*(score_max-bench_score))))

    result.write("Solid\n %.2f fps\n" % fps14)
    bench_score = int(score_max/fps_highscore*fps14)
    result.write("%s%s|\n\n" % (("#"*bench_score),("-"*(score_max-bench_score))))

    
    #result.write("Sculpt mode\n")
    #result.write("Solid matcap\n (25k polys with 4 levels multires, 6.5mln polys, 13mln tris): %.2f fps\n (5 levels multires, 26mln polys, 52mln tris): %.2f fps\n\n\n" % (fps30, fps31))
    #result.write("Screen resolution : %s x %s\nVBOs: %s\nAnisotropic filter: %s\nDraw method: %s\nMulti sample: %s\nMipmaps: %s\nGPU Mipmap: %s\n" % (width, height, vbos, af, draw_met, view_aa, mip, mipgpu))


    avg_fps = (fps10+ fps11 + fps12 + fps13 + fps14)/5
    total_fps = fps10+ fps11 + fps12 + fps13 + fps14
    result.write("SCORE TOTAL\n%s\n" % ("="*score_max))
    result.write("FPS (avg/total): %.2f / %.2f\n" % (avg_fps, total_fps))
    result.write("Time: %i min %i sec\n" % (timeovmin, timeovsec))
    


classes = (
    VPB_OT_RunBenchmark, 
    BenchmarkOperator,
    AppTimersOperator,
    preferences.ViewportBenchmarkPreferences,
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

