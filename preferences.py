# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


if "bpy" in locals():
    import importlib
    importlib.reload(config)
else:
    from . import config

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, IntProperty


class ViewportBenchmarkPreferences(AddonPreferences):
    bl_idname = __package__

    # debug mode
    debug_mode: BoolProperty(
        name="Debug Mode",
        description="Debug Mode",
        default=False)

    is_benchmark: BoolProperty(
        name="is_benchmark",
        description="Chose wether to run a benchmark or a stress test",
        default=True)

    view_angle: IntProperty(
        name="view_angle",
        description="view_angle",
        default=80,
        min = 0,
        max=180,
        step=1,
        subtype='FACTOR') 
    
    view_distance: IntProperty(
        name="view_distance",
        description="view_distance",
        default=10,
        min = 1,
        soft_max=100,
        step=1,
        subtype='FACTOR') 

    view_z_pos: IntProperty(
        name="view_z_pos",
        description="view_z_pos",
        default=2,
        min = 0,
        soft_max=10,
        step=1,
        subtype='FACTOR') 
    
    iterations: IntProperty(
        name="iterations",
        description="iterations",
        default=1,
        min = 1,
        soft_max=10,
        step=1,
        subtype='FACTOR')

    loops: IntProperty(
        name="loops",
        description="loops",
        default=1,
        min = 1,
        soft_max=100,
        step=1,
        subtype='FACTOR') 

    benchmark_refresh: IntProperty(
        name="benchmark_refresh",
        description="benchmark_refresh",
        default=120,
        min = 10,
        soft_max=120,
        step=1,
        subtype='FACTOR')

    angle_steps: IntProperty(
        name="angle_steps",
        description="angle_steps",
        default=5,
        min = 1,
        soft_max=10,
        step=1,
        subtype='FACTOR') 
    
    report_bar_width: IntProperty(
        name="report_bar_width",
        description="report_bar_width",
        default=100,
        min = 10,
        soft_max=100,
        step=1,
        subtype='FACTOR') 
        
    report_bar_max_fps: IntProperty(
        name="report_bar_max_fps",
        description="report_bar_max_fps",
        default=500,
        min = 100,
        soft_max=1000,
        step=1,
        subtype='FACTOR') 
    
    is_interactive: BoolProperty(
        name="is_interactive",
        description="is_interactive",
        default=False)    
        

        
    benchmark_options: BoolProperty(
        name="Benchmark Configuration",
        description="Benchmark Configuration",
        default=False)

    shading_mark: BoolProperty(
        name="shading_mark",
        description="shading_mark",
        default=False)  
    
    mode_mark: BoolProperty(
        name="mode_mark",
        description="mode_mark",
        default=False)  
               
    def draw(self, context):
        layout = self.layout        

        layout.use_property_split = False
        col = layout.column(align=True)        
        
        col.prop(self, 'debug_mode') 
        #col.prop(self, 'iterations')
        #col.prop(self, 'is_interactive') 
        col.prop(self, 'benchmark_refresh') 
        #col.prop(self, 'report_bar_width') 
        col.separator(factor=2)

        col.prop(self, 'loops') 
        col.prop(self, 'angle_steps')  

        col.separator(factor=2)
        col.prop(self, 'view_angle') 
        col.prop(self, 'view_distance') 
        col.prop(self, 'view_z_pos') 
        
        col.separator(factor=2)
        
        col.prop(self, 'benchmark_options') 
        if self.benchmark_options:
            for key, shading in enumerate(config.benchmark_config['shading_type']):   
                box = col.box()
                row = box.row()
                #row.label(text=shading + ": " + str(config.benchmark_config['shading_type'][shading]['Enabled'])) 
                row.prop(self, 'shading_mark', text=shading)  

                box = row.box()
                for key, mode in enumerate(config.benchmark_config['shading_type'][shading]['object_mode']):
                    #box.label(text=mode + ": " + str(config.benchmark_config['shading_type'][shading]['object_mode'][mode]['Enabled'])) 
                    box.prop(self, 'mode_mark', text=mode)  
                    #col.prop(self, 'mode') 

        
        row = layout.row(align=True)
        col = row.column(align=True)

        #template_list(listtype_name, list_id, dataptr, propname, active_dataptr, active_propname, item_dyntip_propname='', rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)



        


 
