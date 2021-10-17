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

    
"""Addon preferences"""
import bpy
from bpy.types import AddonPreferences
from bpy.props import ( StringProperty, 
                        BoolProperty, 
                        FloatProperty,
                        PointerProperty,
                        EnumProperty)


class ViewportBenchmarkPreferences(AddonPreferences):
    bl_idname = __package__

    is_benchmark: BoolProperty(
        name="is_benchmark",
        description="Chose wether to run a benchmark or a stress test",
        default=True)

    view_angle: FloatProperty(
        name="view_angle",
        description="view_angle",
        default=80,
        min = 0,
        max=180,
        step=1,
        precision=0,
        subtype='FACTOR') 
    
    view_distance: FloatProperty(
        name="view_distance",
        description="view_distance",
        default=15.0,
        min = 0.0,
        soft_max=100.0,
        step=0.1,
        precision=1,
        subtype='FACTOR') 

    view_z_pos: FloatProperty(
        name="view_z_pos",
        description="view_z_pos",
        default=2.0,
        min = 0,
        soft_max=10.0,
        step=0.1,
        precision=1,
        subtype='FACTOR') 

    max_render_fps: FloatProperty(
        name="max_render_fps",
        description="max_render_fps",
        default=60,
        min = 1,
        soft_max=240,
        step=1,
        precision=0,
        subtype='FACTOR') 

    loops: FloatProperty(
        name="loops",
        description="loops",
        default=1,
        min = 1,
        soft_max=100,
        step=1,
        precision=0,
        subtype='FACTOR') 

    angle_steps: FloatProperty(
        name="angle_steps",
        description="angle_steps",
        default=10,
        min = 0.01,
        soft_max=4,
        step=1,
        precision=2,
        subtype='FACTOR') 

    
    report_bar_width: FloatProperty(
        name="report_bar_width",
        description="report_bar_width",
        default=0.5,
        min = 0.1,
        soft_max=2,
        step=0.1,
        precision=2,
        subtype='FACTOR') 

    # debug mode
    debug_mode: BoolProperty(
        name="debug_mode",
        description="debug_mode",
        default=True)
    
    is_interactive: BoolProperty(
        name="is_interactive",
        description="is_interactive",
        default=False)    
  
    def draw(self, context):
        layout = self.layout        
        layout.use_property_split = True
        
        col = layout.column(align=True)
        col.prop(self, 'max_render_fps') 
        col.prop(self, 'loops') 
        col.prop(self, 'angle_steps') 

        col = layout.column(align=True)
        col.prop(self, 'view_angle') 
        col.prop(self, 'view_distance') 
        col.prop(self, 'view_z_pos') 


        # debug mode
        layout = self.layout  
        col = layout.column(align=True)
        col.prop(self, 'debug_mode') 
        if self.debug_mode:  
            layout = self.layout  
            col = layout.column(align=True)
            col.prop(self, 'is_interactive') 
            col.prop(self, 'is_benchmark') 


        


 
