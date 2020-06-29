bl_info = {
    "name": "RGBa Tools",
    "author": "Henri Hebeisen, RGBa",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "View3D >T Menu",
    "description": "Various tools to help production of RGba's project",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Operator,AddonPreferences,Panel,PropertyGroup
from bpy.props import StringProperty,PointerProperty,EnumProperty
from os import listdir,mkdir,path,stat
from os.path import isfile, join,basename,dirname,exists
import json
import datetime


class RGBaAddonPreferences(AddonPreferences):
    bl_idname = __name__

    godot_project_folder: StringProperty(
        name="Godot source folder",
        default='',
        subtype='DIR_PATH'
    )

    user_export_categories: StringProperty(
        name="Export Categories (separated by a coma)",
        default='props, chars, set'
    )

    def get_items(self, context):
        l = [];
        # for cat in user_export_categories.split(','):
        #     cat = cat.strip()
        #     l.append((cat, cat, cat))
        l.append(('props','Props',""))
        l.append(('chars','Chars',""))
        l.append(('set','Set',""))
        return l;

    categories :EnumProperty( items = get_items)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "godot_project_folder")
        #layout.prop(self, "export_categories")


def get_full_path(self,context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    godot_folder = bpy.path.abspath(addon_prefs.godot_project_folder)
    godot_cat = addon_prefs.categories

    folder_name = bpy.path.basename(bpy.context.blend_data.filepath)[:-6]
    file_name = f"{folder_name}.glb"

    return godot_folder,godot_cat,folder_name,file_name


#Methods
def export_selected_collection(self,context):
    godot_folder,godot_cat,folder_name,file_name = get_full_path(self,context)

    if not exists(join(godot_folder,godot_cat)):
        mkdir(join(godot_folder,godot_cat))
        print(f"The folder {godot_cat} was created")

    if not exists(join(godot_folder,godot_cat,folder_name)):
        mkdir(join(godot_folder,godot_cat,folder_name))
        print(f"The folder {folder_name} was created")

    export_path = join(godot_folder,godot_cat,folder_name,file_name)

    to_export = context.scene.godot_collection_export
    self.report({'WARNING'}, f'The collection to export is {export_path}')

    collection_to_export = context.scene.godot_collection_export

    current_selection = context.selected_objects #we store the current selection
    bpy.ops.object.select_all(action='DESELECT')

    col  = context.scene.collection.children[collection_to_export]
    for obj in col.objects:
     obj.select_set(True)

    bpy.ops.export_scene.gltf(export_format='GLB',
                              ui_tab='GENERAL',
                              export_copyright="RGba",
                              export_image_format='AUTO',
                              export_texture_dir="",
                              export_texcoords=True,
                              export_normals=True,
                              export_draco_mesh_compression_enable=False,
                              export_tangents=False,
                              export_materials=True,
                              export_colors=True,
                              export_cameras=False,
                              export_selected=False,
                              use_selection=False,
                              export_extras=False,
                              export_yup=True,
                              export_apply=False,
                              export_animations=True,
                              export_frame_range=True,
                              export_frame_step=1,
                              export_force_sampling=True,
                              export_nla_strips=True,
                              export_def_bones=False,
                              export_current_frame=False,
                              export_skins=True,
                              export_all_influences=False,
                              export_morph=False,
                              export_lights=False,
                              export_displacement=False,
                              will_save_settings=False,
                              filepath=export_path,
                              check_existing=False)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in current_selection:
        obj.select_set(True)


class RGBA_PT_export_collection_operator(Operator):
    """Export the chosen collection to godot folder"""
    bl_idname = "rgba.export_collection"
    bl_label = "Export Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        export_selected_collection(self,context)
        return {'FINISHED'}

# User Interface
class RGBA_PT_export_to_godot(Panel):
    """Export a whole collection as a glb file to godot"""
    bl_label = "Export to Godot"
    bl_category = "RGBa"
    bl_idname = "RGBA_PT_export_to_godot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        layout.prop_search(scene, "godot_collection_export",
                           bpy.data,
                           "collections",
                           text="Collection to export")
        row = layout.row(align=True)
        layout.prop(addon_prefs,"categories")
        row = layout.row(align=True)
        godot_folder,godot_cat,folder_name,file_name = get_full_path(self,context)
        if not bpy.data.is_saved:
            row.label(text='Please save the file before exporting it !',
                      icon='FILE_BLEND')
        elif not godot_folder:
            row.label(text="Please setup the godot folder in the addon preferences.",
                icon="ERROR")
        else:
            filename = bpy.path.basename(bpy.context.blend_data.filepath)[:-6]

            row = layout.row(align=True)
            row.operator("rgba.export_collection",icon="EXPORT")
            row = layout.row(align=True)
            full_path = join(godot_folder,godot_cat,folder_name,file_name)
            if exists(full_path):
                info = stat(full_path)
                row.label(text=f"File {full_path} already exists and will overwritten !",
                          icon="INFO")
                row = layout.row(align=True)
                row.label(text=f"File was last modified on :{datetime.datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d-%H:%M')}")
            else:
                row.label(text=f"File will be saved at {full_path}.")



# Registration
def register():
    bpy.utils.register_class(RGBA_PT_export_collection_operator)
    bpy.utils.register_class(RGBA_PT_export_to_godot)
    bpy.utils.register_class(RGBaAddonPreferences)
    bpy.types.Scene.godot_collection_export = StringProperty()


def unregister():
    bpy.utils.unregister_class(RGBA_PT_export_collection_operator)
    bpy.utils.unregister_class(RGBA_PT_export_to_godot)
    bpy.utils.unregister_class(RGBaAddonPreferences)
    del bpy.types.Scene.godot_collection_export


if __name__ == "__main__":
    register()
