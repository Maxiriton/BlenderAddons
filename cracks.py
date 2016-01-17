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

# <pep8 compliant>

# copyright (c) 2015 urchn.org,
# Henri hebeisen

import bpy
import random
import uuid
import mathutils
import math


class CrackPoint:
    """ Define a Crack Point, with its location, radius, position in its \
        branch and collection of children"""

    def ___init___(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.position = 0
        self.hasChildren = False
        self.radius = 1.0
        self.children = []

    # def PositionNormalised(pPointsTot):
    #     if self.position > pPointsTot:
    #         raise "Error in point position,should be greater than the" + \
    #             "total number of points"
    #     else:
    #         return self.position/pPointsTot
    #
    # def StartFrameChildren(pStartFrame, pEndFrame, pPointsTot):
    #     lAnimDur = pEndFrame - pStartFrame
    #     return pStartFrame + lAnimDur*PositionNormalised(pPointsTot)


class CrackCurve:
    """ Define a crack Curve """

    def ___init___(self):
        self.parentid = 0
        self.parentPosition = 0.0
        self.curve
        self.id


def initSceneProperties(scn):
    """Store properties in the active scene"""

    bpy.types.Scene.NbrPoints = bpy.props.IntProperty(
        name="Number of Points",
        description="Number of generated points",
        default=23,
        min=1)

    bpy.types.Scene.XPos = bpy.props.FloatProperty(
        name="X position of direction Vector",
        description="X position of direction Vector",
        default=1.0)

    bpy.types.Scene.YPos = bpy.props.FloatProperty(
        name="Y position of direction Vector",
        description="Y position of direction Vector",
        default=0.0)

    bpy.types.Scene.BranchProba = bpy.props.FloatProperty(
        name="Branching Probability",
        description="Probability of branching at each point",
        default=0.1,
        min=0.01,
        max=1.0)

    bpy.types.Scene.RotAngle = bpy.props.IntProperty(
        name="Rotation Angle",
        description="Rotation angle for big angles",
        default=5,
        min=0,
        max=90)

    bpy.types.Scene.RotShortAngle = bpy.props.IntProperty(
        name=" Small Rotation Angle",
        description="Rotation angle for small angles",
        default=1,
        min=0,
        max=10)

    bpy.types.Scene.SpeedVaria = bpy.props.FloatProperty(
        name="Speed Variation",
        description="Variation of speed for each branch",
        default=0.2,
        min=0.0,
        max=1.0)

    bpy.types.Scene.FirstFrame = bpy.props.IntProperty(
        name="First Frame",
        description="First Frame for animation",
        default=1,
        min=0)

    bpy.types.Scene.Duration = bpy.props.IntProperty(
        name="Duration",
        description="Duration of growing per branch (in Frames)",
        default=100,
        min=1)

    bpy.types.Scene.IsAnimated = bpy.props.BoolProperty(
        name="IsAnimated",
        description="Animate Growing",
        default=True)

    bpy.types.Scene.UseDisp = bpy.props.BoolProperty(
        name="Displacement on cracks",
        description="Subdivise each branch and displace them randomly",
        default=False)

    bpy.types.Scene.SubdiviseLevel = bpy.props.IntProperty(
        name="Subdivision Level",
        description="Number of Subdivision per branch",
        min=1,
        soft_max=5,
        max=7,
        default=2)

    bpy.types.Scene.Delta = bpy.props.FloatProperty(
        name="Translate Delta",
        description="Translation distance for micro Cracks",
        soft_min=-1.0,
        soft_max=1.0,
        default=0.2)

    bpy.types.Scene.IterDisp = bpy.props.IntProperty(
        name="Iterations",
        description="Number of iteration of the algorthim, \
                    higher means more disp",
        default=1,
        min=1,
        soft_max=5)

    bpy.types.Scene.UseGrow = bpy.props.BoolProperty(
        name="Grow Radius",
        description="Animate the growth of the radius",
        default=False)

    bpy.types.Scene.GrowFactor = bpy.props.FloatProperty(
        name="Grow Factor",
        description="Multiplication Factor for radius animation",
        default=1.5,
        soft_min=1.0,
        min=0.0)

    bpy.types.Scene.RadDelay = bpy.props.IntProperty(
        name="Growth delay",
        description="Number of frame before radius starts to grow",
        default=0,
        min=0)

    bpy.types.Scene.UseAttenuation = bpy.props.BoolProperty(
        name="Use custom attenuation",
        description="Use customized attenuation parameters for branch length" +
                    "and children probabilty",
        default=False)

    bpy.types.Scene.LengthAtt = bpy.props.FloatProperty(
        name="Branch Length attenuation",
        description="Division Factor for each generation of branch children",
        default=1.0,
        min=1.0)

    bpy.types.Scene.ProbaAtt = bpy.props.FloatProperty(
        name="Children probabilty attenuation",
        description="Division Factor for the probabilty of each generation " +
                    "of branch children",
        default=10.0,
        soft_min=2.0,
        min=1.0)

    bpy.types.Scene.UseSpeedVariation = bpy.props.BoolProperty(
        name="Generate Speed Variation",
        description="Instead of linear Growth, each branch will grow with" +
                    "speed variation, giving more natural results",
        default=True)

    bpy.types.Scene.FCurveSubdiv = bpy.props.IntProperty(
        name="F-Curve Subdivision",
        description="Number of subdivision for each F-Curve animation",
        default=5,
        min=0,
        soft_max=10)

initSceneProperties(bpy.context.scene)


def GeneratePointCloud(pObjectName, pVertPos):
    """Generate a point Cloud Object, each point is represented by a vertex"""
    lCursorPosition = bpy.context.scene.cursor_location

    # Create mesh and object
    me = bpy.data.meshes.new(pObjectName+'Mesh')
    ob = bpy.data.objects.new(pObjectName, me)
    ob.location = lCursorPosition
    ob.show_name = True
    # Link object to scene
    bpy.context.scene.objects.link(ob)
    me.from_pydata(pVertPos, [], [])
    # Update mesh with new data
    me.update()
    return ob


def DefineCurveRadius(pCurrentPosition, pTotalPoints, pHasChildren, pRadius):
    lStep = pRadius/pTotalPoints
    lRadius = pRadius - pCurrentPosition*lStep

    # if pCurrentPosition == 0:
    #     lRadius = lRadius/2
    # if pHasChildren:
    #     lRadius = lRadius*2
    if lRadius < 0.1:
        lRadius = 0.1

    return lRadius


def GenerateSplineCurve(lCrackPointList):
    # On récupère la postion du curseur 3D, pour y ajouter la courbe.
    lCursorPosition = bpy.context.scene.cursor_location

    # add a curve to link them together
    curvedata = bpy.data.curves.new(name='Curve', type='CURVE')
    curvedata.dimensions = '3D'
    objectdata = bpy.data.objects.new("ObjCurve", curvedata)
    objectdata.location = lCursorPosition
    objectdata.data.dimensions = '3D'
    objectdata.data.fill_mode = 'FULL'
    objectdata.data.bevel_depth = 0.1
    objectdata.data.bevel_resolution = 4
    bpy.context.scene.objects.link(objectdata)

    polyline = curvedata.splines.new('NURBS')
    polyline.points.add(len(lCrackPointList)-1)
    for num in range(len(lCrackPointList)):
        lCurCrack = lCrackPointList[num]
        if lCurCrack.hasChildren:
            weight = 100
        else:
            weight = 1
        polyline.points[num].co = (lCurCrack.x, lCurCrack.y, lCurCrack.z,
                                   weight)
        polyline.points[num].radius = lCurCrack.radius

    polyline.order_u = len(polyline.points)-1
    polyline.use_endpoint_u = True

    return objectdata


def DefineProba(pProbability):
    if random.uniform(0, 1) < pProbability:
        return True
    else:
        return False


def GenerateCracks(pPointNumber, pChildProba, pX, pY, pVector, pAngle,
                   pShortAngle, pLengthAtt, pProbaAtt, pBaseRadius):
    lCrackPointList = []
    x = pX
    y = pY
    z = 0
    vec = pVector

    for lCurrentPoint in range(pPointNumber):
        lNewPointCrack = CrackPoint()
        lNewPointCrack.x = x
        lNewPointCrack.y = y
        lNewPointCrack.z = z
        lNewPointCrack.position = lCurrentPoint
        lNewPointCrack.hasChildren = DefineProba(pChildProba)
        lRadius = DefineCurveRadius(lCurrentPoint, pPointNumber,
                                    lNewPointCrack.hasChildren,
                                    pBaseRadius)
        if lNewPointCrack.hasChildren:
            lLen = int(pPointNumber / pLengthAtt)
            lNewProba = pChildProba / pProbaAtt
            lNewPointCrack.children = GenerateCracks(lLen, lNewProba,
                                                     x, y, pVector, pAngle,
                                                     pShortAngle,
                                                     pLengthAtt, pProbaAtt,
                                                     lRadius)
        lNewPointCrack.radius = lRadius
        lCrackPointList.append(lNewPointCrack)

        if lCurrentPoint % 5:
            angle = random.uniform(-pShortAngle, pShortAngle)
        else:
            angle = random.uniform(-pAngle, pAngle)
        eul = mathutils.Euler((0.0, 0.0, math.radians(angle)), 'XYZ')
        vec.rotate(eul)
        x = x + vec.x
        y = y + vec.y
        z = z + vec.z

    return lCrackPointList


def FillCracks(pCrackPointList, pCurveDict, pParentID, pPosition, pIsChildren):
    """Generate a curve for each path and its children"""
    lPointList = []
    curveId = uuid.uuid4()
    for num in range(len(pCrackPointList)):
        lCurCrack = pCrackPointList[num]
        lPointList.append(lCurCrack)
        if lCurCrack.hasChildren:
            lPercentage = num/len(pCrackPointList)
            FillCracks(lCurCrack.children, pCurveDict, curveId, lPercentage,
                       True)

    lNewCrackCurve = CrackCurve()
    lNewCrackCurve.id = curveId
    if pIsChildren:
        lNewCrackCurve.parentid = pParentID
        lNewCrackCurve.parentPosition = pPosition
    else:
        lNewCrackCurve.parentid = 0
        lNewCrackCurve.parentPosition = 0.0

    lNewCrackCurve.curve = GenerateSplineCurve(lPointList)
    pCurveDict[curveId] = lNewCrackCurve
    return pCurveDict


def GenerateAnimation(pListOrdered,
                      pStartFrame,
                      pDuration,
                      pContext,
                      pRandomFactor):
    lDictFrames = {}

    for crack in pListOrdered:
        if crack.parentid == 0:
            # on commence l'animation à la premiere frame
            lParentCurve = crack.curve
            lStartFrame = pStartFrame
        else:
            # on va chercher la première frame du parent
            try:
                lParentCurve = lDictFrames[crack.parentid]
            except:
                lParentCurve = crack.curve
            lStartFrame = getFrameFromPercentagePosition(pContext,
                                                         lParentCurve,
                                                         crack.parentPosition)
        AnimateGrow(crack.curve, lStartFrame, pDuration, pContext,
                    pRandomFactor)
        lDictFrames[crack.id] = crack.curve

    return lDictFrames


def AnimateGrow(pCurveObject, pStartFrame, pDuration, pContext, pRandomFactor):
    # Go to first frame
    pCurveObject.data.bevel_factor_end = 0.0
    pCurveObject.data.keyframe_insert(data_path="bevel_factor_end",
                                      frame=pStartFrame)
    # insert in last Frame
    pCurveObject.data.bevel_factor_end = 1.0
    pCurveObject.data.keyframe_insert(data_path="bevel_factor_end",
                                      frame=pStartFrame + pDuration - 1)

    kf = pCurveObject.data.animation_data.action.fcurves[0].keyframe_points[0]
    kf.interpolation = 'BEZIER'

    if pContext.scene.UseSpeedVariation:
        lSubdiv = pContext.scene.FCurveSubdiv
        lPas = int(pDuration/lSubdiv)
        lLastValue = 0
        for i in range(1, lSubdiv):  # on  divise en 6
            lCurrentFrame = pStartFrame + lPas*i
            lCurrentValue = (lPas*i)/pDuration
            lBorneHaute = lCurrentValue + pRandomFactor
            if lBorneHaute > 1.0:
                lBorneHaute = 1.0
            lCurrentValue = random.uniform(lLastValue, lBorneHaute)

            pCurveObject.data.bevel_factor_end = lCurrentValue
            pCurveObject.data.keyframe_insert(data_path="bevel_factor_end",
                                              frame=lCurrentFrame)
            lLastValue = lCurrentValue


def AnimateRadius(pCurveObject, pDelay, pFactor):
    lAnimData = pCurveObject.data.animation_data
    lFirstFrame, lLastFrame = lAnimData.action.frame_range
    pCurveObject.data.keyframe_insert(data_path="bevel_depth",
                                      frame=lFirstFrame + pDelay)
    pCurveObject.data.bevel_depth *= pFactor
    pCurveObject.data.keyframe_insert(data_path="bevel_depth",
                                      frame=lLastFrame + pDelay)


def getChildrenInDic(pDict, plistUid):
    lResult = []
    for i in plistUid:
        for x in pDict:
            pCurEntry = pDict[x]
            if pCurEntry.parentid == i:
                lResult.append(pCurEntry)
    return lResult


def getFrameFromPercentagePosition(context, pCurveObject, pPercentagePosition):
    f = 1
    context.scene.frame_set(f)
    context.scene.objects.active = pCurveObject
    bevel = pCurveObject.data.bevel_factor_end
    while bevel < pPercentagePosition:
        f += 1
        context.scene.frame_set(f)
        bevel = pCurveObject.data.bevel_factor_end

    return f


def main(context):
    lVec = mathutils.Vector()
    lVec.x = context.scene.XPos
    lVec.y = context.scene.YPos

    lAngle = context.scene.RotAngle
    lShortAngle = context.scene.RotShortAngle

    lLengthAtt = 1.2
    lProbaAtt = 10.0
    if(context.scene.UseAttenuation):
        lLengthAtt = context.scene.LengthAtt
        lProbaAtt = context.scene.ProbaAtt

    lPointsList = GenerateCracks(context.scene.NbrPoints,
                                 context.scene.BranchProba,
                                 0.0, 0.0, lVec, lAngle, lShortAngle,
                                 lLengthAtt, lProbaAtt, 1.0)
    lCurvesDict = dict()
    lCurvesDict = FillCracks(lPointsList, lCurvesDict, 0, 0.0, False)

    if context.scene.IsAnimated:
        lStartFrame = context.scene.FirstFrame
        lDuration = context.scene.Duration
        lSpeedVaria = context.scene.SpeedVaria

        # on fait une liste dans le bon ordre
        lListOrdered = []
        lInitialID = [0]
        lCount = len(lCurvesDict)

        while lCount > 0:
            lListofchildren = getChildrenInDic(lCurvesDict, lInitialID)
            lInitialID = []
            for i in lListofchildren:
                lListOrdered.append(i)
                lInitialID.append(i.id)
                lCount = lCount - 1

        lAnimInfoDict = GenerateAnimation(lListOrdered,
                                          lStartFrame,
                                          lDuration,
                                          context,
                                          lSpeedVaria)

        if context.scene.UseGrow:
            for key in lAnimInfoDict:
                lDelay = context.scene.RadDelay
                lFactor = context.scene.GrowFactor
                AnimateRadius(lCurvesDict[key].curve, lDelay, lFactor)

    if context.scene.UseDisp:
        for i in lCurvesDict:
            context.scene.objects.active = \
                bpy.data.objects[lCurvesDict[i].curve.name]
            bpy.ops.object.mode_set(mode='EDIT')

            bpy.ops.curve.select_all(action='TOGGLE')
            bpy.ops.curve.subdivide(number_cuts=context.scene.SubdiviseLevel)
            for i in range(context.scene.IterDisp):
                bpy.ops.curve.select_all(action='TOGGLE')
                bpy.ops.curve.select_random()
                bpy.ops.curve.select_less()

                delta = context.scene.Delta
                deltaX = random.uniform(-delta, delta)
                deltaY = random.uniform(-delta, delta)
                bpy.ops.transform.translate(value=(deltaX, deltaY, 0.0),
                                            proportional='ENABLED',
                                            proportional_edit_falloff='RANDOM',
                                            proportional_size=1.2)

            bpy.ops.object.mode_set(mode='OBJECT')
            ctx = bpy.context
            ctx.scene.tool_settings.proportional_edit_falloff = 'SMOOTH'


class CracksOperator(bpy.types.Operator):
    """Generate Cracks and ability to animate them in time"""
    bl_idname = "object.generate_cracks"
    bl_label = "Generate Cracks"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        main(context)
        return {'FINISHED'}


class SetVectUP(bpy.types.Operator):
    """ Define the direction to (0,1)"""
    bl_idname = "object.setvector_up"
    bl_label = "up"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        bpy.types.Scene.XPos = 0.0
        bpy.types.Scene.YPos = 1.0
        return {'FINISHED'}


class SetVectDOWN(bpy.types.Operator):
    """ Define the direction to (0,-1)"""
    bl_idname = "object.setvector_down"
    bl_label = "down"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        bpy.types.Scene.XPos = 0.0
        bpy.types.Scene.YPos = -1.0
        return {'FINISHED'}


class SetVectLEFT(bpy.types.Operator):
    """ Define the direction to (1,0)"""
    bl_idname = "object.setvector_left"
    bl_label = "left"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        bpy.types.Scene.XPos = -1.0
        bpy.types.Scene.YPos = 0.0
        return {'FINISHED'}


class SetVectRIGHT(bpy.types.Operator):
    """ Define the direction to (0,-1)"""
    bl_idname = "object.setvector_right"
    bl_label = "right"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        bpy.types.Scene.XPos = 1.0
        bpy.types.Scene.YPos = 0.0
        return {'FINISHED'}


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Cracks Generator"
    bl_idname = "VIEW3D_PT_Cracks_Gen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "Cracks Gen"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        # Create a simple row.

        layout.label(text=" Growing Direction:")

        row = layout.row()
        split = row.split(percentage=0.5)
        col_left = split.column()
        col_right = split.column()
        col_left.operator("object.setvector_up", icon='TRIA_UP')
        col_right.operator("object.setvector_down", icon='TRIA_DOWN')

        row = layout.row()
        split = row.split(percentage=0.5)
        col_left = split.column()
        col_right = split.column()
        col_left.operator("object.setvector_left", icon='TRIA_LEFT')
        col_right.operator("object.setvector_right", icon='TRIA_RIGHT')

        row = layout.row()
        row.label("Vector direction is (" + str(scene.XPos) + ", " +
                  str(scene.YPos) + ")")

        row = layout.row()
        row.prop(scene, "NbrPoints")

        row2 = layout.row()
        row2.prop(scene, "BranchProba")

        row = layout.row()
        row.prop(scene, "RotAngle")

        row = layout.row()
        row.prop(scene, "RotShortAngle")

        row = layout.row()
        row.prop(scene, "UseAttenuation")
        if scene.UseAttenuation:
            layout.prop(scene, "LengthAtt")
            layout.prop(scene, "ProbaAtt")

        row = layout.row()
        row.prop(scene, "UseDisp")
        if scene.UseDisp:
            layout.prop(scene, "SubdiviseLevel")
            layout.prop(scene, "Delta")
            layout.prop(scene, "IterDisp")

        row = layout.row()
        row = row.prop(scene, "IsAnimated")
        if scene.IsAnimated:
            row = layout.row(align=True)
            row.prop(scene, "FirstFrame")
            row.prop(scene, "Duration")
            row = layout.row()
            row.prop(scene, "UseSpeedVariation")
            if scene.UseSpeedVariation:
                row = layout.row(align=True)
                row.prop(scene, "SpeedVaria", slider=True)
                row = layout.row(align=True)
                row.prop(scene, "FCurveSubdiv")

        row = layout.row()
        row.prop(scene, "UseGrow")
        if scene.UseGrow:
            layout.prop(scene, "RadDelay")
            layout.prop(scene, "GrowFactor")

        # Big button
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.generate_cracks", icon='RNDCURVE')


def register():
    bpy.utils.register_class(CracksOperator)
    bpy.utils.register_class(SetVectUP)
    bpy.utils.register_class(SetVectDOWN)
    bpy.utils.register_class(SetVectLEFT)
    bpy.utils.register_class(SetVectRIGHT)
    bpy.utils.register_class(LayoutDemoPanel)


def unregister():
    bpy.utils.unregister_class(CracksOperator)
    bpy.utils.unregister_class(SetVectUP)
    bpy.utils.unregister_class(SetVectDOWN)
    bpy.utils.unregister_class(SetVectLEFT)
    bpy.utils.unregister_class(SetVectRIGHT)
    bpy.utils.unregister_class(LayoutDemoPanel)

if __name__ == "__main__":
    register()
