bl_info = {
    "name": "Apogee Tools",
    "author": "Henri Hebeisen",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "View3D >T Menu",
    "description": "Various tools to help production of Apogee short film",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Operator,AddonPreferences
from bpy.props import StringProperty
from os import listdir,mkdir,path
from os.path import isfile, join,basename,dirname,exists
import json


class ApogeeAddonPreferences(AddonPreferences):
    bl_idname = __name__

    half_res: StringProperty(
        name="Half Resolution name",
        default='half_res'
    )

    quarter_res: StringProperty(
        name="Quarter Resolution name",
        default='quarter_res'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "half_res")
        layout.prop(self, "quarter_res")

# Utilities

def dump_dict_to_json(slots_status):
    file_name = bpy.context.blend_data.filepath[:-6]
    with open('{}.json'.format(file_name), 'w') as file:
        file.write(json.dumps(slots_status))

def read_dict_from_json():
    file_name = bpy.context.blend_data.filepath[:-6]
    with open('{}.json'.format(file_name)) as json_file:
        return json.load(json_file)

#Methods
def get_slots_in_selection(self,context):
    slots = read_dict_from_json()
    for object in context.selected_objects:
        if object.type == 'EMPTY' and object.instance_collection is not None:
            for obj in bpy.data.collections[object.instance_collection.name].all_objects:
                if obj.name in slots and 'overriden' in slots[obj.name]:
                    continue
                slots.update(get_initial_material_slots_as_dict(obj))
        elif object.material_slots is not None and len(object.material_slots) > 0:
            if object.name in slots and 'overriden' in slots[object.name]:
                continue
            slots.update(get_initial_material_slots_as_dict(object))
    return slots

def override_selection_materials(self,context,mat_override):
    slots = read_dict_from_json()
    for object in context.selected_objects:
        if object.type == 'EMPTY' and object.instance_collection is not None:
            for obj in bpy.data.collections[object.instance_collection.name].all_objects:
                overriden = override_object_materials(obj,mat_override)
                slots[obj.name].update(overriden)
        elif object.material_slots is not None and len(object.material_slots) > 0:
            overriden = override_object_materials(object,mat_override)
            slots[object.name].update(overriden)
    return slots

def remove_override_selection(self,context):
    slots = read_dict_from_json()
    for object in context.selected_objects:
        if object.type == 'EMPTY' and object.instance_collection is not None:
            for obj in bpy.data.collections[object.instance_collection.name].all_objects:
                remove_object_override_materials(obj.name,slots[obj.name]['original'])
                slots[obj.name].pop('overriden',None)
        elif object.material_slots is not None and len(object.material_slots) > 0:
            remove_object_override_materials(object.name,slots[object.name]['original'])
            slots[object.name].pop('overriden',None)
    return slots

def reset_path_to_default(context,path):
    '''We reset the path to its default, i.e. the path links to folder names Textures'''

    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    if path.endswith(addon_prefs.half_res):
        return path[:-len(addon_prefs.half_res)-1] #we remove the name and the _
    elif path.endswith(addon_prefs.quarter_res):
        return path[:-len(addon_prefs.quarter_res)-1] #idem
    else:
        return path


def change_images_path(self,context,resolution=None):
    results = { 'success':[],'fail':[]}

    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    for image in bpy.data.images:
        current_path = bpy.path.abspath(image.filepath)
        if not current_path:
            continue
        new_path = reset_path_to_default(context,dirname(current_path))
        if resolution is not None:
            new_path = "{}_{}".format(new_path, resolution)
        new_path = join(new_path, basename(current_path))
        if exists(new_path):
            image.filepath = new_path
            results['success'].append(image)
        else:
            results['fail'].append(image)
            self.report({'WARNING'}, 'Could not change image for %s' %new_path)
    self.report({'INFO'}, 'Success : {} | Fail : {}'.format(len(results['success']),len(results['fail'])))



class OBJECT_OT_OVERRIDE_SELECTION_MATERIAL(Operator):
    """Override all the materials in the current selection and store original materials in a json"""
    bl_idname = "apogee.override_materials"
    bl_label = "Override selected object materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        get_slots_in_selection(self,context)
        override_selection_materials(self,context,bpy.data.materials[0])

class OBJECT_OT_images_half_res(Operator):
    """Change the path of all the textures in file to half of their resolution"""
    bl_idname = "apogee.textures_half_size"
    bl_label = "half size textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        change_images_path(self, context,resolution=addon_prefs.half_res)
        return {'FINISHED'}

class OBJECT_OT_images_full_res(Operator):
    """Change the path of all the textures in file to their full resolution"""
    bl_idname = "apogee.textures_full_size"
    bl_label = "full size textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        change_images_path(self, context)
        return {'FINISHED'}

class OBJECT_OT_images_quarter_res(Operator):
    """Change the path of all the textures in file to quarter of their resolution"""
    bl_idname = "apogee.textures_quarter_size"
    bl_label = "quarter size textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        change_images_path(self, context,resolution=addon_prefs.quarter_res)
        return {'FINISHED'}

# User Interface
class VIEW3D_PT_apogee_tools_panel(bpy.types.Panel):
    """Panel for all Apogee Tools"""
    bl_label = "Apogee Tools"
    bl_category = "Apogee"
    bl_idname = "VIEW3D_PT_apogee_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Change textures sizes:")
        row = layout.row(align=True)
        row.operator("apogee.textures_full_size",text="Full Size")
        row.operator("apogee.textures_half_size",text="Half Size")
        row.operator("apogee.textures_quarter_size",text="Quarter Size")


# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_images_half_res)
    bpy.utils.register_class(OBJECT_OT_images_full_res)
    bpy.utils.register_class(OBJECT_OT_images_quarter_res)
    bpy.utils.register_class(VIEW3D_PT_apogee_tools_panel)
    bpy.utils.register_class(ApogeeAddonPreferences)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_images_half_res)
    bpy.utils.unregister_class(OBJECT_OT_images_full_res)
    bpy.utils.unregister_class(OBJECT_OT_images_quarter_res)
    bpy.utils.unregister_class(VIEW3D_PT_apogee_tools_panel)
    bpy.utils.unregister_class(ApogeeAddonPreferences)


if __name__ == "__main__":
    register()
