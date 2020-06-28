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
from os import listdir,mkdir,path
from os.path import isfile, join,basename,dirname,exists
import json


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

#Methods
def export_selected_collection(self,context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    godot_folder = addon_prefs.godot_project_folder
    godot_cat = addon_prefs.categories

    folder_name = bpy.path.basename(bpy.context.blend_data.filepath)[:-6]
    file_name = f"{folder_name}.glb"

    export_path = join(godot_folder,godot_cat,folder_name,file_name)

    to_export = context.scene.godot_collection_export
    self.report({'WARNING'}, f'The collection to export is {export_path}')

    to_export = context.scene.godot_collection_export
    #on recupère la selection courante

    # bpy.ops.export_scene.gltf(export_format='GLB',
    #                           ui_tab='GENERAL',
    #                           export_copyright="RGba",
    #                           export_image_format='AUTO',
    #                           export_texture_dir="",
    #                           export_texcoords=True,
    #                           export_normals=True,
    #                           export_draco_mesh_compression_enable=False,
    #                           export_tangents=False,
    #                           export_materials=True,
    #                           export_colors=True,
    #                           export_cameras=False,
    #                           export_selected=False,
    #                           use_selection=False,
    #                           export_extras=False,
    #                           export_yup=True,
    #                           export_apply=False,
    #                           export_animations=True,
    #                           export_frame_range=True,
    #                           export_frame_step=1,
    #                           export_force_sampling=True,
    #                           export_nla_strips=True,
    #                           export_def_bones=False,
    #                           export_current_frame=False,
    #                           export_skins=True,
    #                           export_all_influences=False,
    #                           export_morph=True,
    #                           export_morph_normal=True,
    #                           export_morph_tangent=False,
    #                           export_lights=False,
    #                           export_displacement=False,
    #                           will_save_settings=False,
    #                           filepath="",
    #                           check_existing=True)




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
        if not bpy.data.is_saved:
            row.label(text='Please save the file before exporting it !',
                      icon='FILE_BLEND')
        else:
            # TODO check that the godot path is setuped
            filename = bpy.path.basename(bpy.context.blend_data.filepath)[:-6]
            row = layout.row(align=True)
            row.operator("rgba.export_collection",icon="EXPORT")
            row = layout.row(align=True)
            row.label(text=f"Your model will be exported at : {filename}.glb")


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
