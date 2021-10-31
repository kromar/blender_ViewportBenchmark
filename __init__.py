
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
    importlib.reload(config)
else:
    from . import preferences
    from . import config
    
import bpy
import bgl
import time
import random
from time import perf_counter 
import importlib
import math
import mathutils
from mathutils import Euler
from bl_operators.presets import AddPresetBase
from bpy.types import Menu, Operator, Panel 
from bpy.props import IntProperty


bl_info = {
    "name": "Viewport Benchmark",
    "description": "Viewport Benchmark",
    "author": "Daniel Grauer",
    "version": (1, 1, ),
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
        row.operator(operator="view3d.benchmark_run", text="Benchmark", icon='FUND', emboss=True, depress=False)
        #row.operator(operator="view3d.benchmark_run", text="Benchy", icon='MONKEY', emboss=True, depress=False)
        

class BenchmarkModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "view3d.benchmark_run"
    bl_label = "Modal Timer Operator"
    _view_3d = None
    _modal_timer = None
    _benchEnd = False
    _width = None
    _height = None
    start_angle : IntProperty(default=0) 
    shading_runs : IntProperty(default=0) 
    mode_runs : IntProperty(default=0) 
    full_rotation : IntProperty(default=360)  

    """ @classmethod
    def poll(cls, context):
        return context.selected_objects   """

    def invoke(self, context, event):  
        #prepare for benchmark
        #bpy.ops.wm.window_new()
        #bpy.ops.render.view_show()
        #bpy.ops.render.view_cancel()  
        # blender 3.0 --> bpy.ops.screen.area_close({"area": bpy.context.screen.areas[0]}).
        bpy.ops.screen.animation_cancel()
        self.view3d_fullscreen(context) 
        #bpy.context.space_data.show_gizmo = False
        #bpy.context.space_data.overlay.show_overlays = False 
        #         
        wm = context.window_manager 
        self._modal_timer = wm.event_timer_add(1/prefs().benchmark_refresh, window=context.window)     
        wm.modal_handler_add(self)          
        return {'RUNNING_MODAL'}
   
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._modal_timer)

    def modal(self, context, event):  
        if event.type in {'ESC'}:
            self.cancel(context)    
            return{'FINISHED'} 
        
        if event.type == 'TIMER':
            self._benchEnd = self.rotationMark(context, event)  

            if self._benchEnd:     
                self.finishBenchmark(context)  
                print("finished")          
                self.start_angle = 0    
                self.shading_runs = 0  
                self.mode_runs = 0 
                self.cancel(context)           
                return{'FINISHED'}
            
            #self.spawnMark(context, event)            
            #return{'FINISHED'}
        
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
                self._width = area.width
                self._height = area.height                
                for space in area.spaces: 
                    if space.type == 'VIEW_3D':
                        space.shading.type = shading                          
                        try:
                            bpy.ops.object.mode_set(mode=mode)
                        except:
                            pass
        

    def rotationMark(self, context, event):
        if self.shading_runs < len(config.benchmark_config['shading_type']):
            for shader_key, shading in enumerate(config.benchmark_config['shading_type']):  
                #only run for active shading                   
                if shader_key == self.shading_runs:  
                    if config.benchmark_config['shading_type'][shading]['Enabled']:                              
                        if self.mode_runs < len(config.benchmark_config['shading_type'][shading]['object_mode']):                            
                            for mode_key, mode in enumerate(config.benchmark_config['shading_type'][shading]['object_mode']):                                     
                                #only run for active mode
                                if mode_key == self.mode_runs:   
                                    if prefs().debug_mode:
                                        print("\nrun: ", shading, mode, self.start_angle)                                        
                                        print("shader_key: ",
                                                "run: ", self.shading_runs, "/", len(config.benchmark_config['shading_type'])) 
                                        print("mode_key: ",
                                                "run: ", self.mode_runs, "/", len(config.benchmark_config['shading_type'][shading]['object_mode']))  
                                                           
                                    if config.benchmark_config['shading_type'][shading]['object_mode'][mode]['Enabled']:
                                        # load view after full rotation
                                        if self.start_angle == 0:
                                            self.initializeView(context, shading, mode)

                                        time_start = time.perf_counter()             
                                        eul = self._view_3d.view_rotation.to_euler()     
                                        eul.z = eul.z + math.radians(prefs().angle_steps)
                                        self._view_3d.view_rotation = eul.to_quaternion() 
                                        # Update the viewport    
                                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=prefs().iterations)
                                        frame_time = (time.perf_counter() - time_start)                                          
                                        if prefs().debug_mode:  
                                            print(frame_time * 1000,  1 / frame_time)                              
                                        config.benchmark_config['shading_type'][shading]['object_mode'][mode]['score'].append(1/frame_time)
                    
                                        self.start_angle += prefs().angle_steps
                                    else:
                                        self.mode_runs += 1
                                        self.start_angle = 0  
                                # skip non active modes       
                                else:                                    
                                    pass
                                
                                #next mark if modes have been reached
                                if self.mode_runs == len(config.benchmark_config['shading_type'][shading]['object_mode']):
                                    self.shading_runs += 1
                                    self.mode_runs = 0
                                    self.start_angle = 0  

                                # step to next benchmark
                                if self.start_angle >= self.full_rotation:
                                    self.mode_runs += 1
                                    self.start_angle = 0 
                                    if prefs().debug_mode:
                                        print("MODE: ", self.shading_runs, self.mode_runs, len(config.benchmark_config['shading_type'][shading]['object_mode']) )
                                    
                                    #go to next shading run when all modes have been run
                                    if self.mode_runs == len(config.benchmark_config['shading_type'][shading]['object_mode']):
                                        print()
                                        self.shading_runs += 1
                                        self.mode_runs = 0
                                        self.start_angle = 0     
                    else:
                        self.shading_runs += 1
                        self.mode_runs = 0
                        self.start_angle = 0
        
        # finish benchmark
        if self.shading_runs == len(config.benchmark_config['shading_type']):
            self._benchEnd = True
            self.cancel(context)
            return self._benchEnd   


    def spawnMark(self, context, event):
        time_start = time.perf_counter()             
        XYZcoord = (random.random()*100, random.random()*100, random.random()*100) 
        bpy.ops.mesh.primitive_uv_sphere_add(location=XYZcoord)    
        
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=prefs().iterations)  
        frame_time = (time.perf_counter() - time_start)   
        print(frame_time * 1000,  1 / frame_time)                              

        self.start_angle += prefs().angle_steps
        

    def finishBenchmark(self, context):
        #restore defaults      
        #
        #self.view3d_fullscreen(context)
        #bpy.context.space_data.show_gizmo = True
        #bpy.context.space_data.overlay.show_overlays = True

        print("="*80, end="\n")
        
        #calcualte scores
        report = []
        total_score = []
        for key, shading in enumerate(config.benchmark_config['shading_type']):         
            if config.benchmark_config['shading_type'][shading]['Enabled']:     
                #report.append([shading])
                for key, mode in enumerate(config.benchmark_config['shading_type'][shading]['object_mode']):
                    if config.benchmark_config['shading_type'][shading]['object_mode'][mode]['Enabled']:
                        score = sum(config.benchmark_config['shading_type'][shading]['object_mode'][mode]['score'])
                        if not prefs().debug_mode:
                            print("Report FPS: ", shading, mode, round(score / self.full_rotation * prefs().angle_steps / prefs().loops, 2))
                        report.append([shading, mode, round(score / self.full_rotation * prefs().angle_steps, 2)])
                        total_score.append(score)
                        config.benchmark_config['shading_type'][shading]['object_mode'][mode]['score'].clear()
                        
            #report.append([""])

        import platform
        platformProcessor = platform.processor()
        cpu = str("CPU: %r" % (platformProcessor))
        gpu = str("GPU: %r" % bgl.glGetString(bgl.GL_RENDERER))
        gpu_driver = str("GPU Driver: %r" % (bgl.glGetString(bgl.GL_VERSION)))
        resolution = str(self._width) + "x" + str(self._height)                
        resx, resy = 1920, 1080
        normal_resolution = resx * resy
        current_resolution = self._width * self._height
        fps_score = round(sum(total_score)/ self.full_rotation * prefs().angle_steps / len(report))
        normalized_score = round(sum(total_score) / normal_resolution * current_resolution / self.full_rotation * prefs().angle_steps /len(report))
 
        def report_bar(score=0):                       
            bar_width = prefs().report_bar_width
            bar_max_fps = prefs().report_bar_max_fps
            bar_fps_score = int(bar_width / bar_max_fps * score)
            bar_score = int(bar_width / bar_max_fps * normalized_score)
            bar = str((bar_fps_score * "|")  + (bar_width - bar_fps_score) * "-" + "| " + str(score))
            return bar

        def draw(self, context):
            layout = self.layout
            layout.label(text=cpu)
            layout.label(text=gpu)
            layout.label(text=gpu_driver)  

            layout.separator(factor=2)  
            layout.label(text="Resolution Score (" + str(resx) + "x" + str(resy) + ")")
            self.layout.label(text = report_bar(normalized_score))
            
            layout.label(text="Resolution Score (" + resolution + ")")
            self.layout.label(text = report_bar(fps_score))

            layout.separator(factor=2)
            for fps in report:
                print(fps[2])
                self.layout.label(text=str(fps[0] + " - " + fps[1]))
                self.layout.label(text="    " + str(round((fps[2] / prefs().loops), 2)))
                bar = report_bar(fps[2])
                self.layout.label(text = bar)


        bpy.context.window_manager.popup_menu(draw, title = "Benchmark Results", icon = 'SHADING_RENDERED')                       
        self.cancel(context) 
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
