from conventions import conventions

from simple_objects import custom_geometry
from local_utils import texture_utils
from simple_objects.animator import Animator

from latex_objects.latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np

from simple_objects.custom_geometry import createColoredParametricDashedCurveGeomNode


class IndicatorPrimitive(Animator):
    def __init__(self):
        Animator.__init__(self)

    # a makeobject is pointless to define here, since it will get overridden anyway
    # for a specific object

    def setColor(self, color):
        self.color = color
        self.nodePath.setColor(*self.color)


class Box2dCentered(IndicatorPrimitive):
    def __init__(self):
        super(Box2dCentered, self).__init__()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
        self.nodePath = render.attachNewNode(self.node)


class ParametricLinePrimitive(Animator):
    def __init__(self, func, param_interv=np.array([0, 1]),
                 thickness=1., color=Vec4(1., 1., 1., 1.), howmany_points=50):
        Animator.__init__(self)
        self.thickness = thickness
        self.color = color
        self.howmany_points = howmany_points
        self.func = func
        self.makeObject(func, param_interv, thickness, color, howmany_points)

    def makeObject(self, func, param_interv, thickness, color, howmany_points):
        # draw a parametric curve
        from simple_objects.custom_geometry import createColoredParametricCurveGeomNode
        self.node = createColoredParametricCurveGeomNode(
            func=func,
            param_interv=param_interv, thickness=thickness, color=color, howmany_points=howmany_points)
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)


class ParametricDashedLinePrimitive(Animator):
    def __init__(self,
                 func,
                 param_interv=np.array([0,
                                        1]),
                 thickness=1.,
                 color=Vec4(1., 1., 1., 1.),
                 howmany_points=50):
        Animator.__init__(self)
        self.makeObject(
            func,
            param_interv,
            thickness,
            color,
            howmany_points,
        )

    def makeObject(self, func, param_interv, thickness, color, howmany_points):
        self.node = createColoredParametricDashedCurveGeomNode(
            func=func,
            param_interv=param_interv,
            thickness=thickness,
            color=color,
            howmany_points=howmany_points)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)


class ConePrimitive(Animator):
    def __init__(self):
        super(ConePrimitive, self).__init__()

    def makeObject(self):
        self.node = custom_geometry.create_GeomNode_Cone(
            color_vec4=Vec4(1., 1., 1., 1.))

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setTwoSided(True)
