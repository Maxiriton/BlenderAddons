import bpy
from mathutils import Vector
from os import listdir,path
from os.path import isfile, join, splitext,basename


def make_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections: # Does the collection already exist?
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection) # Add the new collection under a parent
        return new_collection

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

def get_texture_from_folder(texture_folder, texture_name):
    for f in listdir(texture_folder):
        if texture_name in f:
            return join(texture_folder,f)
    return None



def create_material(path):
    mat = bpy.data.materials.new(name=basename(path))
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].select = True
    principled = mat.node_tree.nodes['Principled BSDF']
    mat.node_tree.nodes['Material Output'].select = False
    mat.node_tree.nodes.active = mat.node_tree.nodes['Principled BSDF']

    coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    coord.location = Vector((-1000,0))


    texture_folder = join(path,'textures/')

    #albedo_map
    albedo_path = get_texture_from_folder(texture_folder,'Albedo')
    if albedo_path:
        albedo = mat.node_tree.nodes.new('ShaderNodeTexImage')
        albedo_image = bpy.data.images.load(filepath=albedo_path)
        #albedo_image.colorspace_settings.name = 'Non-Color'
        albedo.location = Vector((-500,350))
        albedo.image = albedo_image
        mat.node_tree.links.new(albedo.outputs['Color'], principled.inputs['Base Color'])
        mat.node_tree.links.new(coord.outputs['UV'], albedo.inputs['Vector'])

    #roughness
    roughness_path = get_texture_from_folder(texture_folder,'Roughness')
    if roughness_path:
        roughness = mat.node_tree.nodes.new('ShaderNodeTexImage')
        roughness_image = bpy.data.images.load(filepath=roughness_path)
        roughness_image.colorspace_settings.name = 'Non-Color'
        roughness.location = Vector((-500,50))
        roughness.image = roughness_image
        mat.node_tree.links.new(roughness.outputs['Color'], principled.inputs['Roughness'])
        mat.node_tree.links.new(coord.outputs['UV'], roughness.inputs['Vector'])

    #normal
    normal_path = get_texture_from_folder(texture_folder,'Normal_')
    if normal_path:
        normal = mat.node_tree.nodes.new('ShaderNodeTexImage')
        normal_image = bpy.data.images.load(filepath=normal_path)
        normal_image.colorspace_settings.name = 'Non-Color'
        normal.location = Vector((-500,-250))
        normal.image = normal_image
        normal_map_node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
        normal_map_node.location = Vector((-200,-250))
        mat.node_tree.links.new(normal.outputs['Color'], normal_map_node.inputs['Color'])
        mat.node_tree.links.new(normal_map_node.outputs['Normal'], principled.inputs['Normal'])
        mat.node_tree.links.new(coord.outputs['UV'], normal.inputs['Vector'])

    return mat

def clean_scene():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj,do_unlink = True)

    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection, do_unlink=True)

def save_scene(folder_path):
    file_name ='imported_{}.blend'.format(basename(folder_path))
    file_path = join(folder_path,file_name)
    print("Le path est :" + file_path)

    bpy.ops.wm.save_as_mainfile(filepath=file_path)

def get_folder_path():
    argv = sys.argv
    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    #the first argument must be the folder file_path
    return argv[0]

def main():
    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    folder_path = argv[0]
    if folder_path.endswith('/'):
        folder_path = folder_path[:-1]
    print(folder_path)
    clean_scene()
    print('Creating Material...')
    mat = create_material(folder_path)
    if mat:
        print('Material Successfully created')
    else:
        print('Material creation failed')
    import_lod(folder_path,mat)
    save_scene(folder_path)

    print("batch job finished, exiting")

if __name__ == "__main__":
    main()
