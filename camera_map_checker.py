bl_info = {
    "name": "Camera Map Checker",
    "author": "Henri Hebeisen",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "TBD",
    "description": "Replace image texture with a checker to evaluate distortion",
    "warning": "",
    "wiki_url": "",
    "category": "Material",
}

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
import mathutils

CHECKER_MAP = "checker_map"
CHECKER_NAME = "__checker_preview__"

def find_next_node(node):
    return node.outputs[0].links[0].to_node

def find_image_node(material,uv_map_name):
    nodes = bpy.data.materials[material].node_tree.nodes

    uv_node = None
    for node in nodes:
        if node.type == 'UVMAP' and node.uv_map == uv_map_name:
            uv_node = node

    if uv_node is None:
        return None

    to_find = uv_node
    while to_find.type != 'TEX_IMAGE':
        to_find = find_next_node(to_find)

    return to_find


def get_or_create_checker(size):
    try :
        image = bpy.data.images[CHECKER_MAP]
    except :
        image = bpy.data.images.new(CHECKER_MAP, width=size, height=size)
        image.generated_type = 'UV_GRID'


    return image

def create_checker_image_node(material,img_node):
    node  = bpy.data.materials[material].node_tree.nodes.new('ShaderNodeTexImage')
    links = bpy.data.materials[material].node_tree.links

    node.location = img_node.location + mathutils.Vector((0,-250))
    node.name = img_node.name + CHECKER_NAME

    #input reconnection
    if len(img_node.inputs[0].links) > 0 :
        links.new(img_node.inputs[0].links[0].from_socket,node.inputs[0])

    #output reconnection
    for output in img_node.outputs:
        for link in output.links:
            links.new(node.outputs[output.identifier],link.to_socket)

    #image setup
    image = get_or_create_checker(2048)
    node.image = image
    node.interpolation = img_node.interpolation
    node.projection = img_node.projection
    node.use_custom_color = True
    node.color = (0.553794, 0.451944, 0.608)


def delete_checker_image_node(material):
    checker_nodes = [node for node in bpy.data.materials[material].node_tree.nodes if node.name.endswith(CHECKER_NAME)]
    links = bpy.data.materials[material].node_tree.links

    for checker_node in checker_nodes:
        img_node = bpy.data.materials[material].node_tree.nodes[checker_node.name[:-len(CHECKER_NAME)]]

        #input reconnection
        links.new(checker_node.inputs[0].links[0].from_socket,img_node.inputs[0])

        #output reconnection
        for output in checker_node.outputs:
            for link in output.links:
                links.new(img_node.outputs[output.identifier],link.to_socket)

        #we delete the checker node
        bpy.data.materials[material].node_tree.nodes.remove(checker_node)

def get_all_UV_MAP_from_modifier(object):
    result = []
    for modifier in object.modifiers:
        if modifier.type !='UV_PROJECT':
            continue

        if modifier.uv_layer:
            result.append(modifier.uv_layer)

    return result

def get_image_nodes(mat,uv_maps):
    nodes = []
    for uv_map in uv_maps:
        nodes.append(find_image_node(mat.name,uv_map))

    return nodes

def set_checker(self,context):
    obj = context.active_object
    UV_maps = get_all_UV_MAP_from_modifier(obj)
    for mat in obj.data.materials:
        nodes = get_image_nodes(mat,UV_maps)
        for img_node in nodes:
            create_checker_image_node(mat.name,img_node)

    bpy.context.scene["IsCheckerEnabled"] = True

def remove_checker(self,context):
    obj = context.active_object
    for mat in obj.data.materials:
        delete_checker_image_node(mat.name)
    bpy.context.scene["IsCheckerEnabled"] = False


class OBJECT_OT_set_checker(Operator):
    """Set checker"""
    bl_idname = "material.set_checker"
    bl_label = "Set Checker"
    bl_options = {'REGISTER', 'UNDO'}

    IsCheckerEnabled: bpy.props.BoolProperty(name="Enabled", default=False)

    def execute(self, context):
        if not self.IsCheckerEnabled :
            set_checker(self, context)
            self.IsCheckerEnabled = True
        else :
            remove_checker(self,context)
            self.IsCheckerEnabled = False
        return {'FINISHED'}


# Registration

class SetCheckerPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Camera Map Tool"
    bl_idname = "SCENE_PT_set_checker"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"



    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Create a simple row.
        row = layout.row()

        row.operator("material.set_checker",text="Set checker",
        icon='PLUGIN')

# This allows you to right click on a button and link to the manual
def set_checker_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.material.set_checker", "editors/properties/object"),
    )
    return url_manual_prefix, url_manual_mapping

def register():
    bpy.utils.register_class(OBJECT_OT_set_checker)
    bpy.utils.register_manual_map(set_checker_manual_map)
    bpy.utils.register_class(SetCheckerPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_set_checker)
    bpy.utils.unregister_manual_map(set_checker_manual_map)
    bpy.utils.unregister_class(SetCheckerPanel)

if __name__ == "__main__":
    register()
