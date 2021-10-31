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
                        IntProperty,
                        PointerProperty,
                        EnumProperty)


class ViewportBenchmarkPreferences(AddonPreferences):
    bl_idname = __package__

    # debug mode
    debug_mode: BoolProperty(
        name="debug_mode",
        description="debug_mode",
        default=False)

    wireframe_shading: BoolProperty(
        name="wireframe_shading",
        description="wireframe_shading",
        default=True)
        
    solid_shading: BoolProperty(
        name="solid_shading",
        description="solid_shading",
        default=True)
        
    material_shading: BoolProperty(
        name="material_shading",
        description="material_shading",
        default=True)
        
    rendered_shading: BoolProperty(
        name="rendered_shading",
        description="rendered_shading",
        default=True)

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
        default=50.0,
        min = 0.0,
        soft_max=100.0,
        step=0.1,
        precision=1,
        subtype='FACTOR') 

    view_z_pos: FloatProperty(
        name="view_z_pos",
        description="view_z_pos",
        default=6.0,
        min = 0,
        soft_max=10.0,
        step=0.1,
        precision=1,
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
        default=60,
        min = 1,
        soft_max=100,
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
    
    is_interactive: BoolProperty(
        name="is_interactive",
        description="is_interactive",
        default=False)    
  
    def draw(self, context):
        layout = self.layout        
        layout.use_property_split = True

        col = layout.column(align=True)        
        col.prop(self, 'wireframe_shading') 
        col.prop(self, 'solid_shading') 
        col.prop(self, 'material_shading') 
        col.prop(self, 'rendered_shading') 
        col.separator()
        
        col.prop(self, 'loops') 
        col.prop(self, 'angle_steps') 
        col.prop(self, 'iterations') 
        col.prop(self, 'report_bar_width') 
        col.separator()

        col.prop(self, 'view_angle') 
        col.prop(self, 'view_distance') 
        col.prop(self, 'view_z_pos') 


        # debug mode
        # col.separator()
        col.prop(self, 'benchmark_refresh') 
        #col.prop(self, 'is_interactive') 
        col.prop(self, 'debug_mode') 
        
        row = layout.row(align=True)
        col = row.column(align=True)

        #template_list(listtype_name, list_id, dataptr, propname, active_dataptr, active_propname, item_dyntip_propname='', rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)



        


 
