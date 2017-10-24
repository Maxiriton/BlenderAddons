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

bl_info = {
    "name": "Curve Generator",
    "author": "Henri Hebeisen",
    "version": (0, 5),
    "blender": (2, 78, 0),
    "location": "3D View, ",
    "description": "Custom and artist friendly curve generation",
    "warning": "",
    "wiki_url": "",
    "category": "Add Curve",
    }

import bpy
import random 
from mathutils import Vector

###### Class Definition ######

class Curve_GeneratorProperties(bpy.types.PropertyGroup):
    NbCurve =  bpy.props.IntProperty(
        name="NbCurves",
        description="Number of curves",
        default=50,
        min=1,
        soft_max =500)
        
    RandomFactor = bpy.props.FloatProperty(
        name="RndFactor",
        description="Random Factor",
        default=0.5,
        soft_min=0.0,
        soft_max = 1.0)
        
    CurveDiameter = bpy.props.FloatProperty(
        name="CurveDiameter",
        description="Curve Diameter",
        default=0.05,
        soft_min=0.0,
        soft_max = 1.0)
        
    UseRandomDiameter = bpy.props.BoolProperty(
        name="UseRandomDiameter",
        description="Generate random diameter",
        default=True)
        
    UseAnimation = bpy.props.BoolProperty(
        name="UseAnimation",
        description="Generate keyframes for each curve",
        default=True)
        
    UseRandomAnimation = bpy.props.BoolProperty(
        name="UseRandomAnimation",
        description=" Randomize keys for a more natural effect",
        default=True)
        
    UseRootRadius = bpy.props.BoolProperty(
        name="UseRootRadius",
        description="Use each root radius' value to influence the random factor",
        default=True)
        
    RandomAnimOffset =  bpy.props.IntProperty(
        name="RandomAnimOffset",
        description="Random animation offset (in frames)",
        default=20)
        
    AnimationStartFrame =  bpy.props.IntProperty(
        name="AnimationStartFrame",
        description="Start Frame",
        default=0)
        
    AnimationUseSpline = bpy.props.BoolProperty(
        name="AnimationUseSpline",
        description="Use Spline instead  of segment for animation timing",
        default=True)
        
    AnimationStartDuration =  bpy.props.IntProperty(
        name="AnimationStartDuration",
        description="Start Parameter Duration",
        default=50)
        
    AnimationEndFrame =  bpy.props.IntProperty(
        name="AnimationEndFrame",
        description="End Frame",
        default=0)
        
    AnimationEndDuration =  bpy.props.IntProperty(
        name="AnimationEndDuration",
        description="End Parameter Duration",
        default=50)
        
    Seed =  bpy.props.IntProperty(
        name="Seed",
        description="Random Seed",
        default=0)
        
    
        
###### Utils Functions Definition ######

def deselect_all_bezier_point(curveObj):
    for bezier_pt in curveObj.data.splines[0].bezier_points:
        bezier_pt.select_control_point = False
        bezier_pt.select_left_handle = False
        bezier_pt.select_right_handle = False


###### Functions Definition ######

def AddHookToPoint(hookObj, curveObj,index):
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    hookObj.select = True
    
    bpy.context.scene.objects.active = hookObj
    
    curveObj.select = True
    bpy.context.scene.objects.active = curveObj
    deselect_all_bezier_point(curveObj)
    curveObj.data.splines[0].bezier_points[index].select_control_point = True
    curveObj.data.splines[0].bezier_points[index].select_left_handle = True
    curveObj.data.splines[0].bezier_points[index].select_right_handle = True
    
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.object.hook_add_selob(use_bone=False)
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    
def initHook(context,root):
    hooks = []
    context.scene.objects.active = root
    deselect_all_bezier_point(root)
    bpy.ops.object.mode_set( mode = 'EDIT' )
    
    for bpoint in root.data.splines[0].bezier_points:
        deselect_all_bezier_point(root)
        bpoint.select_control_point = True
        bpoint.select_left_handle = True
        bpoint.select_right_handle = True
        bpy.ops.object.hook_add_newob()
        hooks.append(root.modifiers[len(root.modifiers)-1].object)
    
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    return hooks

def GenerateCurves(context,root,rootPoints,allCurves):
    rndfactor = context.scene.gen_curves.RandomFactor
    seed = context.scene.gen_curves.Seed
    for i in range(0,context.scene.gen_curves.NbCurve-1):
        curvedata = bpy.data.curves.new(name='Curve', type='CURVE')
        objectdata = bpy.data.objects.new("ObjCurve", curvedata)
        objectdata.location = root.location
        objectdata.data.dimensions = '3D'
        objectdata.data.fill_mode = 'FULL'
        if context.scene.gen_curves.UseRandomDiameter:
            random.seed(seed+i)
            objectdata.data.bevel_depth = random.uniform(-context.scene.gen_curves.CurveDiameter,context.scene.gen_curves.CurveDiameter)
        else:
            objectdata.data.bevel_depth = context.scene.gen_curves.CurveDiameter
        
        objectdata.data.bevel_resolution = 4
        
        bpy.context.scene.objects.link(objectdata)
        
        polyline = curvedata.splines.new('BEZIER')
        polyline.bezier_points.add(len(rootPoints)-1)
        for num in range(len(rootPoints)):
            random.seed(seed+num+i)
            mulfactor = 1.0
            if context.scene.gen_curves.UseRootRadius:
                mulfactor = rootPoints[num].radius

            polyline.bezier_points[num].co.x = random.uniform(rootPoints[num].co.x-(rndfactor*mulfactor), rootPoints[num].co.x+(rndfactor*mulfactor))
            polyline.bezier_points[num].co.y = random.uniform(rootPoints[num].co.y-(rndfactor*mulfactor), rootPoints[num].co.y+(rndfactor*mulfactor))
            polyline.bezier_points[num].co.z = random.uniform(rootPoints[num].co.z-(rndfactor*mulfactor), rootPoints[num].co.z+(rndfactor*mulfactor))
            
            polyline.bezier_points[num].handle_left_type = rootPoints[num].handle_left_type
            polyline.bezier_points[num].handle_right_type = rootPoints[num].handle_right_type
            polyline.bezier_points[num].handle_left = rootPoints[num].handle_left
            polyline.bezier_points[num].handle_right = rootPoints[num].handle_right
     
            
        polyline.order_u = len(polyline.bezier_points)-1
        polyline.use_endpoint_u = True
        allCurves.append(objectdata)
        
def AttachHooksToCurve(hooks,allCurves):
    for curve in allCurves:
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        bpy.ops.object.select_all(action='DESELECT')
        curve.select = True
        bpy.context.scene.objects.active = curve
        for i in range(0,len(curve.data.splines[0].bezier_points)):
            AddHookToPoint(hooks[i],curve,i);
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
def GenerateAnimationData(context,allCurves):
    for curve in allCurves:
        curve.data.bevel_factor_start = 0.0
        begin_start_value= context.scene.gen_curves.AnimationStartFrame
        if context.scene.gen_curves.UseRandomAnimation:
            rnd = random.uniform(0,context.scene.gen_curves.RandomAnimOffset)
            begin_start_value += rnd
        curve.data.keyframe_insert(data_path="bevel_factor_start",frame=begin_start_value)
        
        curve.data.bevel_factor_start = 1.0
        end_start_value= context.scene.gen_curves.AnimationStartFrame + context.scene.gen_curves.AnimationStartDuration
        if context.scene.gen_curves.UseRandomAnimation:
            new_frame = end_start_value
            while (new_frame <= begin_start_value):
                new_frame = end_start_value
                rnd = random.uniform(0,context.scene.gen_curves.RandomAnimOffset)
                new_frame += rnd
            end_start_value = new_frame
        curve.data.keyframe_insert(data_path="bevel_factor_start",frame=end_start_value)

        curve.data.bevel_factor_end = 0.0
        begin_end_value= context.scene.gen_curves.AnimationEndFrame
        if context.scene.gen_curves.UseRandomAnimation:
            rnd = random.uniform(0,context.scene.gen_curves.RandomAnimOffset)
            begin_end_value += rnd
        curve.data.keyframe_insert(data_path="bevel_factor_end",frame=begin_end_value)
        
        curve.data.bevel_factor_end = 1.0
        end_end_value= context.scene.gen_curves.AnimationEndFrame + context.scene.gen_curves.AnimationEndDuration
        if context.scene.gen_curves.UseRandomAnimation:
            new_frame = end_end_value
            while (new_frame <= begin_end_value):
                new_frame = end_end_value
                rnd = random.uniform(0,context.scene.gen_curves.RandomAnimOffset)
                new_frame += rnd
            end_end_value = new_frame
        curve.data.keyframe_insert(data_path="bevel_factor_end",frame= end_end_value)
        
        if context.scene.gen_curves.AnimationUseSpline:
            curve.data.bevel_factor_mapping_start = 'SPLINE'
            curve.data.bevel_factor_mapping_end = 'SPLINE'

    
def generate_new_curves(context):
    root = context.scene.objects.active
    hooks = initHook(context,root)
    context.scene.objects.active = root
    rootPoints = root.data.splines[0].bezier_points
    allCurves = []

    GenerateCurves(context,root,rootPoints,allCurves)
    if context.scene.gen_curves.UseAnimation:     
        GenerateAnimationData(context,allCurves)
    
    AttachHooksToCurve(hooks,allCurves)
    
def animate_selected_curves(context):
    allCurves = []
    for obj in context.selected_objects:
        if obj.type =='CURVE':
            obj.data.animation_data_clear()
            allCurves.append(obj)
    GenerateAnimationData(context,allCurves)

###### ______UI Definition______ ######

class AnimateCurvesPanel(bpy.types.Panel):
    """UI for adding animation to selected curves"""
    bl_label = "Animate Curves"
    bl_idname = "VIEW3D_PT_Animate_Curve_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "3DSpaceLab"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        split = row.split(percentage=0.5)
        c =split.column()
        c.label("Frame : ")
        
        c =split.column()
        c.label("Duration : ")
         
        row = layout.row()
        split = row.split(percentage=0.5)
        c =split.column()
        c.prop(scene.gen_curves,"AnimationStartFrame", text="Bevel Start Frame")
        c =split.column()
        c.prop(scene.gen_curves,"AnimationStartDuration", text="Bevel Start Duration")
        
        row = layout.row()
        split = row.split(percentage=0.5)
        c =split.column()
        c.prop(scene.gen_curves,"AnimationEndFrame", text="Bevel End Frame")
        c =split.column()
        c.prop(scene.gen_curves,"AnimationEndDuration", text="Bevel End Duration")
        
        row = layout.row()
        split = row.split(percentage=0.5)
        c =split.column()
        c.prop(scene.gen_curves,"UseRandomAnimation", text="Randomize Anim")
        if scene.gen_curves.UseRandomAnimation:
            c =split.column()
            c.prop(scene.gen_curves,"RandomAnimOffset","Random Range")
            
        row = layout.row()
        row.prop(scene.gen_curves,"AnimationUseSpline", text="Use Spline for Animation Timing")
            
        row = layout.row()
        row.operator("object.animate_selected_curves", text="Animate Selected Curves", icon='FORCE_CURVE')

class GenerateCurvesPanel(bpy.types.Panel):
    """Addon UI """
    bl_label = "Generate Curves"
    bl_idname = "VIEW3D_PT_Generate_Curve_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "3DSpaceLab"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.prop(scene.gen_curves,"NbCurve")
        
        row = layout.row()
        split = row.split(percentage=0.5)
        c = split.column()
        c.prop(scene.gen_curves,"RandomFactor")
        
        c = split.column()
        c.prop(scene.gen_curves,"UseRootRadius",text=" Use root radius")
        
        row = layout.row()
        row.prop(scene.gen_curves,"Seed")      

        row = layout.row()
        split = row.split(percentage=0.5)
        c =split.column()
        c.prop(scene.gen_curves,"CurveDiameter")        
        
        c =split.column()
        c.prop(scene.gen_curves,"UseRandomDiameter")
        
        
        row = layout.row()
        row.prop(scene.gen_curves,"UseAnimation", text="Generate Animation")   
        
        if scene.gen_curves.UseAnimation:
            row = layout.row()
            split = row.split(percentage=0.5)
            c =split.column()
            c.prop(scene.gen_curves,"AnimationStartFrame", text="Bevel Start Frame")
            c =split.column()
            c.prop(scene.gen_curves,"AnimationStartDuration", text="Bevel Start Duration")
            
            row = layout.row()
            split = row.split(percentage=0.5)
            c =split.column()
            c.prop(scene.gen_curves,"AnimationEndFrame", text="Bevel End Frame")
            c =split.column()
            c.prop(scene.gen_curves,"AnimationEndDuration", text="Bevel End Duration")
            
            row = layout.row()
            split = row.split(percentage=0.5)
            c =split.column()
            c.prop(scene.gen_curves,"UseRandomAnimation", text="Randomize Anim")
            if scene.gen_curves.UseRandomAnimation:
                c =split.column()
                c.prop(scene.gen_curves,"RandomAnimOffset","Random Range")
                
            row = layout.row()
            row.prop(scene.gen_curves,"AnimationUseSpline", text="Use Spline for Animation Timing")
            
        row = layout.row()
        row.operator("object.generate_random_curves", text="Generate Curves", icon='FORCE_CURVE')
        
        
###### ______Operator Definition______ ######

class CURVE_OT_generateCurves(bpy.types.Operator):
    """Generate Curve"""
    bl_idname = "object.generate_random_curves"
    bl_label = "Generate Random Curves"
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        generate_new_curves(context)
        return {'FINISHED'}
        
class CURVE_OT_animateSelectedCurves(bpy.types.Operator):
    """Generate Curve"""
    bl_idname = "object.animate_selected_curves"
    bl_label = "Animate Selected Curve"
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        animate_selected_curves(context)
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(GenerateCurvesPanel)
    bpy.utils.register_class(AnimateCurvesPanel)
    bpy.utils.register_class(Curve_GeneratorProperties)
    bpy.utils.register_class(CURVE_OT_generateCurves)
    bpy.utils.register_class(CURVE_OT_animateSelectedCurves)
    bpy.types.Scene.gen_curves = bpy.props.PointerProperty(type=Curve_GeneratorProperties)



def unregister():
    bpy.utils.unregister_class(GenerateCurvesPanel)
    bpy.utils.unregister_class(AnimateCurvesPanel)
    bpy.utils.unregister_class(Curve_GeneratorProperties)
    bpy.utils.unregister_class(CURVE_OT_generateCurves)
    bpy.utils.unregister_class(CURVE_OT_animateSelectedCurves)
    del bpy.types.Scene.gen_curves


if __name__ == "__main__":
    register()