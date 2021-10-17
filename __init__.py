
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
from bl_operators.presets import AddPresetBase
from bpy.types import AddonPreferences, Menu, PropertyGroup, UIList, Operator, Panel 
from bpy.props import ( StringProperty, 
                        BoolProperty, 
                        FloatProperty,
                        IntProperty,
                        EnumProperty,
                        CollectionProperty,
                        )


bl_info = {
    "name": "Viewport Benchmark",
    "description": "Viewport Benchmark",
    "author": "Daniel Grauer",
    "version": (1, 0, 5),
    "blender": (2, 93, 0),
    "location": "Header",
    "category": "System",
    "wiki_url": "https://github.com/kromar/blender_ViewportBenchmark",
    "tracker_url": "https://github.com/kromar/blender_ViewportBenchmark/issues/new",
}


def prefs():
    user_preferences = bpy.context.preferences
    return user_preferences.addons[__package__].preferences 


def draw_button(self, context):
    #if prefs().button_toggle:
    if context.region.alignment == 'RIGHT':
        layout = self.layout
        row = layout.row(align=True)                 
        row.operator(operator="view3d.benchmark_run", text="This File", icon='FUND', emboss=True, depress=False)
        #row.operator(operator="view3d.benchmark_run", text="Benchy", icon='MONKEY', emboss=True, depress=False)
        


class BenchmarkModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "view3d.benchmark_run"
    bl_label = "Modal Timer Operator"
    _view_3d = None
    _rotation = 360
                                
    benchmark_config = {
        'shading_type': {
            'WIREFRAME': {
                'Enabled': True, 
                'object_mode': { 
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
            'SOLID': {
                'Enabled': True, 
                'object_mode': {
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
            'MATERIAL': {
                'Enabled': True, 
                'object_mode': {
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
            'RENDERED': {
                'Enabled': True, 
                'object_mode': {
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
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

    def invoke(self, context, event):  
        #prepare for benchmark
        self.view3d_fullscreen(context)   
        bpy.ops.screen.animation_cancel()
        #bpy.context.space_data.show_gizmo = False
        #bpy.context.space_data.overlay.show_overlays = False 
        
        wm = context.window_manager        
        wm.modal_handler_add(self)
        self._modal_timer = wm.event_timer_add(0.1, window=context.window)
        return {'RUNNING_MODAL'}
   

    def modal(self, context, event):  
        if event.type in {'ESC'}:
            return {'CANCELLED'}        
        
        if event.type == 'TIMER':   
            self.runBenchmark(context, event)
            self.finishBenchmark(context)
            return{'FINISHED'}

        if prefs().is_interactive:
            return {'PASS_THROUGH'}
        else:
            return {'RUNNING_MODAL'}

    
    def initializeView(self, context, shading, mode):    
        #view = bpy.context.screen.areas[0].spaces.active     
        self._view_3d.view_location = (0.0 , 0.0 , prefs().view_z_pos)
        self._view_3d.view_distance = prefs().view_distance 
        eul = Euler((math.radians(prefs().view_angle), 0.0 , 0.0), 'XYZ')
        quat = eul.to_quaternion()         
        self._view_3d.view_rotation = quat

        #rendering configs
        print("Init mode: ", shading)
        for area in bpy.context.screen.areas: 
            if area.type == 'VIEW_3D':
                for space in area.spaces: 
                    if space.type == 'VIEW_3D':
                        space.shading.type = shading  
                        bpy.ops.object.mode_set(mode=mode)
        

    def runBenchmark(self, context, event):
        for key, shading in enumerate(self.benchmark_config['shading_type']):  
            print(key, shading, self.benchmark_config['shading_type'][shading]['Enabled'])
            if self.benchmark_config['shading_type'][shading]['Enabled']:
                print(shading)
                for key, mode in enumerate(self.benchmark_config['shading_type'][shading]['object_mode']):         
                    self._angle = 0  
                    self._time_start = 0
                    print(shading, mode, self._time_start)
                    if self.benchmark_config['shading_type'][shading]['object_mode'][mode]['Enabled']:
                        if self._time_start == 0:
                            self.initializeView(context, shading, mode)

                        while self._angle <= (self._rotation * prefs().loops):               
                            eul = self._view_3d.view_rotation.to_euler()     
                            eul.z = eul.z + math.radians(prefs().angle_steps)
                            self._view_3d.view_rotation = eul.to_quaternion()

                            # Update the viewport
                            self._time_start = time.perf_counter()
                            if bpy.ops.wm.redraw_timer.poll():     
                                #['DRAW', 'DRAW_SWAP', 'DRAW_WIN', 'DRAW_WIN_SWAP', 'ANIM_STEP', 'ANIM_PLAY', 'UNDO']   
                                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=prefs().iterations) 


                            frame_time = (time.perf_counter() - self._time_start)
                            self.benchmark_config['shading_type'][shading]['object_mode'][mode]['score'].append(1/frame_time)

                            if prefs().debug_mode:
                                print(shading, mode, int(self._angle), "frame_time: ", frame_time * 1000, "ms", "fps: ", 1 / frame_time, "fps\n")
                            
                            self._angle += prefs().angle_steps
                                        
            
        return {'FINISHED'} 


    def finishBenchmark(self, context, value='WIREFRAME'):
        #restore defaults
        #self.view3d_fullscreen(context)        

        """ bpy.context.space_data.show_gizmo = True
        bpy.context.space_data.overlay.show_overlays = True    """

        print("="*80, end="\n")
        
        #calcualte scores
        report = []
        for key, shading in enumerate(self.benchmark_config['shading_type']):  
            if self.benchmark_config['shading_type'][shading]['Enabled']:
                for key, mode in enumerate(self.benchmark_config['shading_type'][shading]['object_mode']):
                    if self.benchmark_config['shading_type'][shading]['object_mode'][mode]['Enabled']:
                        score = sum(self.benchmark_config['shading_type'][shading]['object_mode'][mode]['score'])
                        if not prefs().debug_mode:
                            print("Report FPS: ", shading, mode, round(score / self._rotation * prefs().angle_steps / prefs().loops, 2))
                        report.append([shading, mode, round(score / self._rotation * prefs().angle_steps, 2)])
                        self.benchmark_config['shading_type'][shading]['object_mode'][mode]['score'].clear()

        import platform
        platformProcessor = platform.processor()
        cpu = str("CPU: %r" % (platformProcessor))
        gpu = str("GPU: %r" % bgl.glGetString(bgl.GL_RENDERER))
        gpu_driver = str("GPU Driver: %r" % (bgl.glGetString(bgl.GL_VERSION)))
                
        def draw(self, context):
            self.layout.label(text=cpu)
            self.layout.label(text=gpu)
            self.layout.label(text=gpu_driver)
             
            for fps in report:                
                bar = int(fps[2] / prefs().loops * prefs().report_bar_width)
                self.layout.label(text=str(fps[0] + " " + fps[1]))
                self.layout.label(text="    |" + (bar * "=") + "| " + str(round((fps[2] / prefs().loops), 2)))
        bpy.context.window_manager.popup_menu(draw, title = "Benchmark Results", icon = 'SHADING_RENDERED') 
                
        return {'FINISHED'}


    # Press CTRL + ALT + SPACE to leave fullscreen mode 
    def view3d_fullscreen(self, context):                
        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':             
                    self._view_3d = area.spaces.active.region_3d
                    override = {'window': window, 'screen': screen, 'area': area}
                    #bpy.ops.screen.screen_full_area(override, use_hide_panels=True)                    
       

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
