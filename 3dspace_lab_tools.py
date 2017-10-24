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
    "name": "3D Space Lab Tool",
    "author": "Airbus Defence and Space, 3D Space Lab",
    "version": (0, 4),
    "blender": (2, 78, 0),
    "location": "3D View, ",
    "description": "Set of tools dedicaded to help artists with models from the CAD Workd",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
    }
    
import bpy
import random 
from mathutils import Vector

###### Class Definition ######

class SpaceLab_Properties(bpy.types.PropertyGroup):
    """Store properties in the active scene"""

    spc_NbrPoints = bpy.props.IntProperty(
        name="Number of Points",
        description="Number of generated points",
        default=23,
        min=1)
        
    spc_SearchName = bpy.props.StringProperty(
        name="Name to match",
        description="Find all objects with this name",
        default="")
        
    spc_UseActiveObject = bpy.props.BoolProperty(
        name="Use active object",
        description="Use active object's volume as reference volume for objects detection",
        default=True)
        
    spc_SmallObjTolerance = bpy.props.IntProperty(
        name="volume tolerance",
        description="percentage of volume tolerance used for object detection",
        default= 20,
        min=0,
        max=100)
        
    spc_GroupName = bpy.props.StringProperty(
        name="Group Target",
        description="Group Target to select",
        default="")
        
    spc_ConfPath = bpy.props.StringProperty(
      name = "File Path",
      default = "",
      description = "Define the root path of the project",
      subtype = 'FILE_PATH')
      
    spc_SelectionVolume = bpy.props.FloatVectorProperty(
        name ="Volume Dimension",
        unit = 'AREA',
        precision = 3,
        default=(0.2, 0.2, 0.2))

        
###### ______Utils Functions Definition______ ######

def area_of_type(type_name):
    for area in bpy.context.screen.areas:
        if area.type == type_name:
            return area

def get_3d_view():
    return area_of_type('VIEW_3D').spaces[0]
    
def get_material_index(pObject, pMat):
    i = 0
    found = False
    while not found:
        if pObject.material_slots[i].material == pMat:
            print('Trouve %s at index %i' %(pMat.name, i))
            found = True
        else: 
            i += 1
            
    return i


###### ______Functions Definition______ ######

def SelectObjectsByExactName(context):
    bpy.ops.object.select_pattern(pattern=context.scene.SearchName)
    
def SelectObjectsByName(context) :
    pat = "*"+context.scene.SearchName+"*"
    bpy.ops.object.select_pattern(pattern=pat)
    
def SelectSimilarObjects(context):
    """Select similar objects in scene"""
    tol = context.scene.spc_lab.spc_SmallObjTolerance
    C = context.selected_objects
    if context.scene.UseActiveObject:
        actif = bpy.context.scene.objects.active    
        #calcul du volume de la bounding box de l'objet actif
        dim = actif.dimensions
        volume_actif = dim.x*dim.y*dim.z
    else:
        dim = context.scene.spc_lab.spc_SelectionVolume
        volume_actif = dim[0]*dim[1]*dim[2]
        
    min = volume_actif - (volume_actif*tol/100)
    max = volume_actif + (volume_actif*tol/100)

    bpy.ops.object.select_all(action='DESELECT')

    for obj in C:
        dim_cur = obj.dimensions
        volume_cur = dim_cur.x*dim_cur.y*dim_cur.z
        if (volume_cur >= min and volume_cur <= max):
            obj.select = True
            
def RegroupMaterialByColor(context):
    C = context.selected_objects
    currentMats = {}
    for obj in C:
        if obj.type == 'MESH':
            context.scene.objects.active = obj
            mats = obj.data.materials.values()
            mat_index = 0
            for cur_mat in mats:
                cur_color = cur_mat.diffuse_color
                value =currentMats.get(str(cur_color))
                if value is None:
                    currentMats[str(cur_color)] = cur_mat
                else:
                    #on change le slot du materiau
                    obj.data.materials[mat_index] = value
                mat_index = mat_index +1
            
    print("La taille de la liste apres traitement est : " + str(len(currentMats)))
    
def MergeMaterialSlots(context):
    C = context.selected_objects
    for obj in C:
        if obj.type != 'MESH':
            continue

        mats = {}
        obj.active_material_index = 0
        mat_len = len(obj.data.materials)
        i=0
        while i < mat_len:
            cur_mat = obj.data.materials[i]
            if cur_mat is None:
                i +=1
                continue

            if cur_mat.name in mats:
                if i == mats[cur_mat.name]:
                    i +=1
                    continue
                else:
                    last_mat_index = mats[cur_mat.name]
                    obj.active_material_index = i
                    #TODO switch material slots with material to merge
                    bpy.ops.object.material_slot_remove()
                    mat_len = mat_len -1
            else: 
                mats[cur_mat.name] = i
                i +=1   
                
  
def RemoveAllMaterial(context): 
    C = context.selected_objects
    for obj in C:
        if  obj.type != 'MESH':
            continue
        
        nb_mats = len(obj.data.materials)
        for mat in range(nb_mats):
            bpy.ops.object.material_slot_remove()
            
    try:
        bpy.ops.outliner.orphans_purge()
    except:
        print('could not purge')

###### ______UI Definition______ ######

class VIEW3D_PT_SearchByNamePanel(bpy.types.Panel):
    """UI for selection by name"""
    bl_label = "Find by name"
    bl_idname = "VIEW3D_PT_SpaceLabSearchName"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "3DSpaceLab"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "SearchName")
        
        row = layout.row()
        split = row.split(percentage=0.5)
        col_left = split.column() 
        col_right = split.column() 
        col_left.operator("object.textmatch_exact", icon='VIEWZOOM')
        col_right.operator("object.textmatch", icon='BORDERMOVE')
        
class VIEW3D_PT_SelectSimilarObjectPanel(bpy.types.Panel):
    """UI for selection of similar object"""
    bl_label = "Select similar objects"
    bl_idname = "VIEW3D_PT_SpaceLabSimilarObject"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "3DSpaceLab"
    
    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
        row.prop(scene.spc_lab, "spc_UseActiveObject")
        if not context.scene.UseActiveObject:
            row = layout.row()
            row.prop(scene.spc_lab, "spc_SelectionVolume")
            
        row = layout.row()
        row.prop(scene.spc_lab, "spc_SmallObjTolerance",slider = True)
        
        row = layout.row()
        row.operator("object.selectsimilarobject", icon='GROUP')
        
class VIEW3D_PT_VariousOperationsPanel(bpy.types.Panel):
    """UI for accessing all various speed up workflows"""
    bl_label = "Various operations"
    bl_idname = "VIEW3D_PT_SpaceLabvariousOp"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "3DSpaceLab"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.operator("object.reassign_material", icon='MATERIAL')
        row = layout.row()
        row.operator("object.merge_material", icon='POTATO')
        row = layout.row()
        row.operator("object.remove_all_materials", icon='CANCEL')



 
###### ______Operator Definition______ ######

class TextExactSearchOperator(bpy.types.Operator):
    """Select Objects by name"""
    bl_idname = "object.textmatch_exact"
    bl_label = "Match exact Name"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        SelectObjectsByExactName(context)
        return {'FINISHED'}
        
class TextSearchOperator(bpy.types.Operator):
    """Select Objects by name"""
    bl_idname = "object.textmatch"
    bl_label = "Contains name"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        SelectObjectsByName(context)
        return {'FINISHED'}
        
class SelectSimilarObjectsOperator(bpy.types.Operator):
    """Select Objects with similar volume"""
    bl_idname = "object.selectsimilarobject"
    bl_label = "Select Similar Objects"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        SelectSimilarObjects(context)
        return {'FINISHED'}

class ReassignMaterialOperator(bpy.types.Operator):
    """Regroup materials by name"""
    bl_idname = "object.reassign_material"
    bl_label = "Merge material with same color"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        RegroupMaterialByColor(context)
        return {'FINISHED'}
        
class MergeMaterialSlotsOPerator(bpy.types.Operator):
    """Merge all similar slots for current objects"""
    bl_idname = "object.merge_material"
    bl_label = "Merge material slots"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        MergeMaterialSlots(context)
        return {'FINISHED'}
        
class RemoveAllMaterialsOPerator(bpy.types.Operator):
    """Remove all materials in scene"""
    bl_idname = "object.remove_all_materials"
    bl_label = "Max's Slot Eraser"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        RemoveAllMaterial(context)
        return {'FINISHED'}
        
        RemoveAllMaterial
        
def register():
    bpy.utils.register_class(SpaceLab_Properties)
    bpy.utils.register_class(TextSearchOperator)
    bpy.utils.register_class(TextExactSearchOperator)
    bpy.utils.register_class(SelectSimilarObjectsOperator)
    bpy.utils.register_class(ReassignMaterialOperator)
    bpy.utils.register_class(MergeMaterialSlotsOPerator)
    bpy.utils.register_class(RemoveAllMaterialsOPerator)
    
    bpy.utils.register_class(VIEW3D_PT_SearchByNamePanel)
    bpy.utils.register_class(VIEW3D_PT_SelectSimilarObjectPanel)
    bpy.utils.register_class(VIEW3D_PT_VariousOperationsPanel)
    
    bpy.types.Scene.spc_lab = bpy.props.PointerProperty(type=SpaceLab_Properties)



def unregister():
    bpy.utils.unregister_class(SpaceLab_Properties)
    bpy.utils.unregister_class(TextSearchOperator)
    bpy.utils.unregister_class(TextExactSearchOperator)
    bpy.utils.unregister_class(SelectSimilarObjectsOperator)
    bpy.utils.unregister_class(ReassignMaterialOperator)
    bpy.utils.unregister_class(MergeMaterialSlotsOPerator)
    bpy.utils.unregister_class(RemoveAllMaterialsOPerator)
    
    bpy.utils.unregister_class(VIEW3D_PT_SearchByNamePanel)
    bpy.utils.unregister_class(VIEW3D_PT_SelectSimilarObjectPanel)
    bpy.utils.unregister_class(VIEW3D_PT_VariousOperationsPanel)
    
    del bpy.types.Scene.spc_lab


if __name__ == "__main__":
    register()