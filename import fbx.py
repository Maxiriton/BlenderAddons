import fbx
import sys
import json
import os
from os import listdir
from os.path import isfile, join

import FbxCommon


def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__


def get_object_path_name(pObject):
    current_object = pObject
    result_array = []

    while current_object is not None:
        result_array.append(current_object.GetName())
        current_object = current_object.GetParent()

    string_result = ''
    for name in reversed(result_array):
        string_result += name
        string_result += '|'

    return string_result[len('RootNode|'):-1]


def check_instances(pNode, pAllObjects, pAllNodes):

    attribute = pNode.GetNodeAttribute()
    if attribute:
        if attribute.GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
            me = pNode.GetMesh().GetName()
            if me in pAllObjects:
                pAllObjects[me].append(get_object_path_name(pNode))
            else:
                links = [get_object_path_name(pNode)]
                pAllObjects[me] = links
                pAllNodes[me] = pNode

    for i in range(0, pNode.GetChildCount()):
        check_instances(pNode.GetChild(i), pAllObjects, pAllNodes)


def duplicate_node(pNewScene, pNode):

    lSceneFull = pNode.GetScene()

    # On store les src object
    sources = [pNode.GetSrcObject(x) for x in range(pNode.GetSrcObjectCount())]
    sourcesName = [pNode.GetSrcObject(x).GetName()
                                      for x in range(pNode.GetSrcObjectCount())]
    # print(sources)

    # on casse les liens entre le pNode original et ses enfants (Mais pourquoi on doit faire un truc pareil ??)
    pNode.DisconnectAllSrcObject()

    for obj in sources:
        obj.DisconnectAllDstObject()
        obj.ConnectDstObject(pNewScene)
        obj.ConnectDstObject(pNode)
        lSceneFull.DisconnectSrcObject(obj)

    # on doit deconnecter pNode de la scene originale
    lSceneFull.DisconnectSrcObject(pNode)
    pNewScene.GetRootNode().AddChild(pNode)

    return pNewScene


def export_node(pFbxManager, pNode, pPath, pUseBinaryFile):
    ios = fbx.FbxIOSettings.Create(pFbxManager, fbx.IOSROOT)
    ios.SetBoolProp(fbx.EXP_FBX_MATERIAL, False)
    ios.SetBoolProp(fbx.EXP_FBX_TEXTURE, True)
    ios.SetBoolProp(fbx.EXP_FBX_MODEL, True)
    ios.SetBoolProp(fbx.EXP_FBX_SHAPE, True)
    pFbxManager.SetIOSettings(ios)

    exporter = fbx.FbxExporter.Create(pFbxManager, "exporteur")
    export_status = exporter.Initialize(pPath, -1, pFbxManager.GetIOSettings())

    if not export_status:
        print('Call to FbxManager.Initialize() failed.')
        print('Last error returned: %s ' %
              exporter.GetStatus().GetLastErrorString())

    temp_scene = fbx.FbxScene.Create(pFbxManager, 'temp_scene')

    # new_node = duplicate_node(temp_scene,pNode)
    # temp_scene.GetRootNode().AddChild(new_node)

    duplicate_node(temp_scene,pNode)


    # print(temp_scene.GetRootNode().GetChild(0).GetMesh().GetLayer(0).GetNormals().GetDirectArray()[0])

    if pUseBinaryFile:
        status = FbxCommon.SaveScene(pFbxManager, temp_scene, pPath, -1,True)
    else:
        status = FbxCommon.SaveScene(pFbxManager, temp_scene, pPath)

    exporter.Destroy()
    temp_scene.Destroy()


def display_hierarchy(pNode, pDepth):
    lString = ''
    i = 0
    for i in range(0, pDepth):
        lString += '____'

    lString += pNode.GetName()
    lString += '\n'

    print(lString)
    for i in range(0, pNode.GetChildCount()):
        display_hierarchy(pNode.GetChild(i), pDepth + 1)


def dump_objects_on_files(pFbxManager, pDirectoryPath, pDictObjects, pDictNodes, pUseBinaryFile):
    file_number = 0
    print("Now working on %s ..." % pDirectoryPath)
    for name, paths in pDictObjects.items():
        current_object = {name: paths}
        current_node = pDictNodes[name]
        with open(join(pDirectoryPath, str(file_number) + '.json'), 'w') as outfile:
            json.dump(current_object, outfile)
        export_node(pFbxManager, current_node, join(
            pDirectoryPath, str(file_number) + '.fbx'), pUseBinaryFile)
        file_number += 1


def export_all_from_directory(pDirPath, pUseBinaryFile):
    manager = fbx.FbxManager.Create()

    export_dir = join(pDirPath, 'export')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    onlyfiles = [f for f in listdir(pDirPath) if isfile(join(pDirPath, f))]
    for file in onlyfiles:
        cur_file_path = join(pDirPath, file)

        importer = fbx.FbxImporter.Create(manager, "MyImporter")

        status = importer.Initialize(cur_file_path)
        if status == False:
            print('FbxImporter Initialize fail')
            print('Error %s : ' % importer.GetLastErrorString())
            sys.exit()

        scene = fbx.FbxScene.Create(manager, 'myscene')
        importer.Import(scene)
        importer.Destroy()

        lRoot = scene.GetRootNode()

        # display_hierarchy(lRoot,0)
        all_instances = {}
        all_nodes_to_export = {}

        check_instances(lRoot, all_instances, all_nodes_to_export)

        outdir = join(export_dir, file)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        dump_objects_on_files(manager, outdir, all_instances,
                              all_nodes_to_export, pUseBinaryFile)
        scene.Destroy()



dirpath = r'C:\Users\Holo\Documents\FBX Python tool\fbx_input\FBX_export_pixyz\\'
# dirpath = r'C:\Users\Holo\Documents\FBX Python tool\fbx_input\blend\\'
export_all_from_directory(dirpath, True)
