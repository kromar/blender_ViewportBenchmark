
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
    "version": (1, 0, 1),
    "blender": (2, 93, 0),
    "location": "Header",
    "category": "System",
    "wiki_url": "https://github.com/kromar/blender_ViewportBenchmark",
    "tracker_url": "https://github.com/kromar/blender_ViewportBenchmark/issues/new",
}


benchResults = {}


def prefs():
    user_preferences = bpy.context.preferences
    return user_preferences.addons[__package__].preferences 

def draw_button(self, context):
    #if prefs().button_toggle:
    if context.region.alignment == 'RIGHT':
        layout = self.layout
        row = layout.row(align=True)                 
        row.operator(operator="benchmark_modal.run", text="This File", icon='FUND', emboss=True, depress=False)
        row.operator(operator="benchmark_modal.run", text="Benchy", icon='MONKEY', emboss=True, depress=False)
        


class BenchmarkModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "benchmark_modal.run"
    bl_label = "Modal Timer Operator"  
    _view_3d = None
    _modal_timer = None
    _angle = 0  
    _time_start = 0
    _report_bar_width = 60
    _rotation = 360
    _benchmark_score = []
      
    _bench_shading_type = 0 
    benchmarkList = [
                    'WIREFRAME', 
                    'SOLID', 
                    'MATERIAL', 
                    'RENDERED',
                    ]
                                
    benchmark_config = {
        'shading_type': {
            'WIREFRAME': {'Enabled': True, 'score':[]},
            'SOLID': {'Enabled': True, 'score':[]},
            'MATERIAL': {'Enabled': True, 'score':[]},
            'RENDERED': {'Enabled': True, 'score':[]},
        },

        'object_mode': {    #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            'EDIT': {'Enabled': True, 'score':[]},
            'OBJECT': {
                'Enabled': True, 
                'light': {
                    'STUDIO': True, 'score':[],
                    'MATCAP': True, 'score':[],
                    'FLAT': True, 'score':[],
                },                 
                'color_type': {
                    'MATERIAL': True, 'score':[],
                    'SINGLE': True, 'score':[],
                    'OBJECT': True, 'score':[],
                    'RANDOM': True, 'score':[],
                    'VERTEX': True, 'score':[],
                    'TEXTURE': True, 'score':[],
                },
            },
            'SCULPT': {'Enabled': True, 'score':[]},
            'VERTEX_PAINT': {'Enabled': False, 'score':[]},
            'WEIGHT_PAINT': {'Enabled': False, 'score':[]},
            'TEXTURE_PAINT': {'Enabled': False, 'score':[]},
        }, 

        'modifiers': [
            'ARRAY', 
            'BEVEL', 
            'BOOLEAN', 
            'MULTIRES', 
            'SUBSURF', 
        ],
              
        'show_wireframe': False,

    }

    """ @classmethod
    def poll(cls, context):
        return context.selected_objects   """
    
    def initializeView(self, context):       
        view = bpy.context.screen.areas[0].spaces.active     
        self._view_3d.view_location = (0.0 , 0.0 , prefs().view_z_pos)
        self._view_3d.view_distance = prefs().view_distance 
        eul = Euler((math.radians(prefs().view_angle), 0.0 , 0.0), 'XYZ')
        quat = eul.to_quaternion()         
        self._view_3d.view_rotation = quat

        #rendering configs
        print("benchamrk mode: ", self.benchmarkList[self._bench_shading_type])
        view.shading.type = self.benchmarkList[self._bench_shading_type]     
        self._time_start = time.perf_counter()
        return


    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._modal_timer)
        bpy.ops.screen.back_to_previous()
        return {'CANCELED'}


    def execute(self, context):   
        self._benchmark_score = [] 
        wm = context.window_manager        
        self._modal_timer = wm.event_timer_add(1/prefs().max_render_fps, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def runBenchmark(self, context): 
        eul = self._view_3d.view_rotation.to_euler()            
        eul.z = eul.z + math.radians(prefs().angle_steps)
        self._view_3d.view_rotation = eul.to_quaternion()
        
        if prefs().is_benchmark: 
            # run benchmark            
            self._time_start = time.perf_counter()
            self._angle += prefs().angle_steps            
            # measure draw time
            if bpy.ops.wm.redraw_timer.poll():          
                bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
            frame_time = (time.perf_counter() - self._time_start)
            #self._benchmark_score = {self.benchmarkList[self._bench_shading_type]}
            #self._benchmark_score[self._bench_shading_type] = self.benchmarkList[self._bench_shading_type]
            self._benchmark_score.append(1/frame_time)
            #print(self.benchmarkList[self._bench_shading_type])
            
            if prefs().debug_mode:
                print("angle: ", int(self._angle))
                print("frame_time: ", frame_time*1000, "ms")
                print("fps: ", 1/frame_time, "fps\n")             

            if self._angle == int(self._rotation * prefs().loops):
                #print(self._angle, "\n", self._time_start, "\n", time_stop, "\n", (time_stop-self._time_start))
                 
                self._time_start = 0
                self._angle = 0                
                self._bench_shading_type += 1
                if prefs().debug_mode:
                    print(self._bench_shading_type, len(self.benchmarkList))

                if self._bench_shading_type == len(self.benchmarkList): 
                    bench_finish = True 
                    #bpy.ops.screen.back_to_previous()     # this crashes blender https://developer.blender.org/T82552
                    context.window_manager.event_timer_remove(self._modal_timer) 
                else:
                    bench_finish = False  

                #calcualte scores
                score = sum(self._benchmark_score)
                print("Average FPS: ", round(score/self._rotation,2))
                print("Score: ", round(score,2)) 
                self.ShowReport(["Average FPS: " + str(round(score/self._rotation,2)), "Score: " + str(round(score,2))], self.benchmarkList[self._bench_shading_type-1], 'SHADING_RENDERED')   
                
                self._benchmark_score = []     
                        
                
                return bench_finish
            
           

        else:   #run stress-test   (could be a predefined time or amount of loops)   
            pass
        



    def ShowReport(self, message = [], title = "Message Box", icon = 'INFO'):
        import platform
        platformProcessor = platform.processor()
        cpu = str("CPU: %r" % (platformProcessor))
        gpu = str("GPU: %r" % bgl.glGetString(bgl.GL_RENDERER))
        gpu_driver = str("GPU Driver: %r" % (bgl.glGetString(bgl.GL_VERSION)))
        
       
        def draw(self, context):
            self.layout.label(text=cpu)
            self.layout.label(text=gpu)
            self.layout.label(text=gpu_driver)
            layout = self.layout  
            for i in message:
                self.layout.label(text=i)
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)  

    def modal(self, context, event):  
        if event.type in {'ESC'}:
            self.cancel(context)
            context.window_manager.event_timer_remove(self._modal_timer)
            return {'CANCELLED'}

        if event.type == 'TIMER': 
            #preapre setting for benchmark
            if self._time_start == 0:
                self.initializeView(context)

            #initialize benchmark
            bench_finish = self.runBenchmark(context)
            if bench_finish:     
                self.finishBenchmark(context)           
                return {'FINISHED'}

        if prefs().is_interactive:
            return {'PASS_THROUGH'}
        else:
            return {'RUNNING_MODAL'}


    def finishBenchmark(self, context):
        #restore defaults
        if bpy.ops.screen.back_to_previous.poll():
            bpy.ops.screen.back_to_previous()
        #context.window_manager.event_timer_remove(self._modal_timer)
        #bpy.context.space_data.show_gizmo = True
        #bpy.context.space_data.overlay.show_overlays = True 
        # Example to find avearge of list

        print("="*80, end="\n")
        
        #calcualte scores
        score = sum(self._benchmark_score)
        #print("Average FPS: ", round(score/self._rotation,2))
        #print("Score: ", round(score,2)) 
        print(self.benchmark_config['shading_type'])
        #total_score = fps10+ fps11 + fps12 + fps13 + fps14                 
        self.ShowReport(["test", "report", "items"], "Benchmark Results", 'SHADING_RENDERED')   
        return {'FINISHED'}


    def invoke(self, context, event):         
        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':             
                    self._view_3d = area.spaces.active.region_3d
                    override = {'window': window, 'screen': screen, 'area': area}                    
                    bpy.ops.screen.screen_full_area(override)       
                    """ bpy.context.space_data.show_gizmo = False
                    bpy.context.space_data.overlay.show_overlays = False   """
        
        bpy.data.scenes['Scene'].render.fps = prefs().max_render_fps
                
        self.execute(context)
        return {'RUNNING_MODAL'}





classes = (
    BenchmarkModal,
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

