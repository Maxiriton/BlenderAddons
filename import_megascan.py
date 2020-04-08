import bpy
from os import listdir,path
from os.path import isfile, join, splitext,basename


def make_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections: # Does the collection already exist?
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection) # Add the new collection under a parent
        return new_collection

folder_path = '/home/henri/Téléchargements/Brick_Rubble_rhlxZ_8K_3d_ms'
def import_lod(path,material):
    for f in sorted(listdir(path)):
        name, extension = splitext(f)
        if not extension == '.fbx':
            continue

        #we create a collection
        collection = make_collection(name,bpy.context.scene.collection)

        file_path = join(path, f)
        bpy.ops.import_scene.fbx(filepath=file_path)

        #collection linking
        for obj in bpy.context.selected_objects:
            collection.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
            obj.data.materials.append(material)


def create_material(path):


    mat = bpy.data.materials.new(name=basename(path))
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].select = True
    mat.node_tree.nodes['Material Output'].select = False
    mat.node_tree.nodes.active = mat.node_tree.nodes['Principled BSDF']

    texture_folder = join(path,'textures/')
    files = []
    for f in listdir(texture_folder):
        files.append({"name":f,"name":f})

    print(files)
    print(texture_folder)

    bpy.data.objects['Cube'].data.materials.append(mat)

    #save the current area
    area = bpy.context.area.type
    bpy.context.area.type = "NODE_EDITOR"
    bpy.ops.node.nw_add_textures_for_principled(filepath=texture_folder, directory=texture_folder, files=files, relative_path=True)
    bpy.context.area.type = area
    return mat

mat = create_material(folder_path)
#import_lod(folder_path,bpy.data.materials[0])
