from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive, Fixed2dLabel
from composed_objects.composed_objects import Vector

from simple_objects.custom_geometry import create_Triangle_Mesh_From_Vertices_and_Indices, createCircle, createColoredUnitQuadGeomNode

from simple_objects.primitives import ParametricLinePrimitive
from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special

import glm

from direct.showbase.ShowBase import ShowBase, DirectObject

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight

import networkx as nx

from simple_objects.simple_objects import Pinned2dLabel

from interactive_tools import cameraray

from functools import partial


def sayhi():
    print("heylo ------- ######")


def edges_equal_undirected(nx_graph_edge_tuple_1, nx_graph_edge_tuple_2):
    """ even in undirected graphs, edges are represented by tuples in nx, not by sets """
    e1 = nx_graph_edge_tuple_1
    e2 = nx_graph_edge_tuple_2

    return ((e1[0] == e2[0]) and (e1[1] == e2[1])) or ((e1[0] == e2[1]) and (e1[1] == e2[0]))

class Graph:
    # a graph, logically is a set of nodes and a set of edges, which are sets of nodes
    # it can be directed, then the sets of nodes are tuples
    # here, we make a directed graph, with the fastest way back to the root

    def __init__(self# , # P_arr
    ):
        self.logical_graph = nx.Graph()
        hd = "H" + chr(252) + "sker D" + chr(252)
        mh = "Mot" + chr(246) + "rhead"
        mc = "M" + chr(246) + "tley Cr" + chr(252) + "e"
        st = "Sp" + chr(305) + "n" + chr(776) + "al Tap"
        q = "Queensr" + chr(255) + "che"
        boc = "Blue " + chr(214) + "yster Cult"
        dt = "Deatht" + chr(246) + "ngue"

        self.logical_graph.add_edge(hd, mh)
        self.logical_graph.add_edge(mc, st)
        self.logical_graph.add_edge(boc, mc)
        self.logical_graph.add_edge(boc, dt)
        self.logical_graph.add_edge(st, dt)
        self.logical_graph.add_edge(q, st)
        self.logical_graph.add_edge(dt, mh)
        self.logical_graph.add_edge(st, mh)

        self.pos = nx.spring_layout(self.logical_graph)

        # get all their coordinates, and draw them
        self.coords = [*self.pos.values()]

        self.graph_points = []

        # get all the edges and draw them
        self.edges_list = [e for e in self.logical_graph.edges]

        self.graph_edges = []

        # -----------------

        # self.graph_points=P_arr

        # self.beziercurve=ParametricLinePrimitive(
        #     lambda t:
        #     np.array([
        #         Graph.calcGraph(t, self.graph_points)[0],
        #         Graph.calcGraph(t, self.graph_points)[1],
        #         Graph.calcGraph(t, self.graph_points)[2]
        #     ]),
        #     param_interv=np.array([0, 1]),
        #     thickness=1.,
        #     color=Vec4(1., 1., 0., 1.))


    def plot(self):
        # nodes
        for coord in self.coords:
            p = Point3d(
                pos=Vec3(coord[0], coord[1], 0.),
                scale=0.025)
            self.graph_points.append(p)

        # edges
        for edge in self.edges_list:
            point1 = self.pos[edge[0]]
            point2 = self.pos[edge[1]]

            # plot a line between point1 and point2
            edgeline = Line1dSolid()
            edgeline.setTailPoint(Vec3(point1[0], point1[1], 0.))
            edgeline.setTipPoint(Vec3(point2[0], point2[1], 0.))

    # @staticmethod
    # def calcGraph(t, P_arr):
    #     _sum = 0
    #     n = len(P_arr) - 1

    #     assert len(P_arr) >= 2  # at least a linear bezier curve
    #     assert t >= 0. and t <= 1.

    #     for i, P_i in enumerate(P_arr):
    #         _sum += (scipy.special.comb(n, i)
    #                  * (1. - t)**(n - np.float(i))
    #                  * t**np.float(i)
    #                  * P_i)
    #     return _sum

class GraphPoint:
    """ when a graphical graph node is dragged, you need to know it's associated logical graph node,
    in order to update the graphics of the edges appropriately """

    def __init__(self, nx_graph, nx_graph_node):
        self.nx_graph = nx_graph
        self.nx_graph_node = nx_graph_node


class GraphPickablePoint(GraphPoint, PickablePoint):
    def __init__(self, nx_graph, nx_graph_node, pickableObjectManager, pos):
        GraphPoint.__init__(self, nx_graph, nx_graph_node)
        PickablePoint.__init__(self, pickableObjectManager, pos=pos)


class GraphEdge(Vector):
    """ when dragging a graph node, the graph edge also needs to update, so you need to know it's associated logical graph nodes """
    def __init__(self, nx_graph, nx_graph_edge, point1_vec3, point2_vec3):
        self.nx_graph = nx_graph
        self.nx_graph_edge = nx_graph_edge

        # plot a line between point1 and point2
        Vector.__init__(self, tail_point_logical=point1_vec3, tip_point_logical=point2_vec3)
        # self.setTailPoint(point1_vec3)
        # self.setTipPoint(point2_vec3)


class DraggableGraph(Graph):
    def __init__(self, camera_gear):
        Graph.__init__(self)

        self.camera_gear = camera_gear
        # self.camera_gear.set_view_to_yz_plane()

        # --- plot draggable bezier curve together with points
        # for dragging the points and updating the bezier curve,
        # the points have to stay instantiated (objects that are dragged), while the bezier curve
        # can be regenerated from the new point positions at every drag event

        # -- add picking utilities
        self.pickableObjectManager = PickableObjectManager()
        self.dragAndDropObjectsManager = DragAndDropObjectsManager()
        self.collisionPicker = CollisionPicker(
            self.camera_gear, render, base.mouseWatcherNode, base, self.dragAndDropObjectsManager)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept('mouse1', self.collisionPicker.onMouseTask)

        self.plot()

        self.updateAfterPointCoordsChanged()

        # # -- add the update dragging tasks for each of the PickablePoints' draggers
        # for pp in self.graph_points:
        #     dragger = self.dragAndDropObjectsManager.get_dragger_from_nodePath(pp.nodePath):
        #     dragger.add_on_state_change_function(self.updateAfterPointCoordsChanged)

        # TODO: improve the design by letting DraggableGraph inherit from DragAndDropObjectsManager,
        # it can be easily thought of as holding the dragger objects themselves


    def plot(self):
        # ---- go through the nodes
        for nx_node in (list) (self.logical_graph):
            auto_coord = self.pos[nx_node]  # the coordinate which is automatically generated, i.e. by a layout algorithm

            pt = GraphPickablePoint(self.logical_graph,
                                    nx_node,
                                    self.pickableObjectManager,
                                    pos=Vec3(auto_coord[0], auto_coord[1], 0.))

            pt.nodePath.setScale(*(0.9*np.array([0.02, 0.02, 0.02])))

            pt_dragger = Dragger(pt, self.camera_gear)
            pt_dragger.add_on_state_change_function(sayhi)

            # use 'optional parameters' to store the current value (at 'save time', vs at call time) (elisp is much better at that)
            mylambda = lambda pt=pt: self.updateAfterPointCoordsChanged(dragged_graphpickablepoint=pt)

            pt_dragger.add_on_state_change_function(mylambda)  # will this actually work?

            self.dragAndDropObjectsManager.add_dragger(pt_dragger)

            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            # pt.nodePath.showBounds()

            self.graph_points.append(pt)

        # edges
        for edge in self.edges_list:
            point1 = self.pos[edge[0]]
            point2 = self.pos[edge[1]]

            e = GraphEdge(self.logical_graph,
                          edge,
                          Vec3(point1[0], point1[1], 0.),
                          Vec3(point2[0], point2[1], 0.))

            self.graph_edges.append(e)


    def updateAfterPointCoordsChanged(self, dragged_graphpickablepoint=None):
        """ once a PickablePoint has been dragged, you need to update it's edges """

        # first of all find the dragged object (PickablePoint)
        # self.dragAndDropObjectsManager.get_dragger_from_nodePath()
        if dragged_graphpickablepoint:
            connected_edges = (list) (self.logical_graph.edges([dragged_graphpickablepoint.nx_graph_node]))

            # what is happening here is that the
            for ge in self.graph_edges:
                mycond = any([edges_equal_undirected(ge.nx_graph_edge, conn_edge) for conn_edge in connected_edges])
                if mycond:
                    # find out which node is the dragged node, number 1 or number 2
                    dp_pos = dragged_graphpickablepoint.getPos()  # new position of dragged point
                    if dragged_graphpickablepoint.nx_graph_node == ge.nx_graph_edge[0]:
                        print(dragged_graphpickablepoint.nx_graph_node, " is node 1 of ", ge.nx_graph_edge)
                        ge.setTailPoint(dp_pos)
                    else:
                        print(dragged_graphpickablepoint.nx_graph_node, " is node 2 of ", ge.nx_graph_edge)
                        ge.setTipPoint(dp_pos)

        # extract the new coordinates from the pickable points
        new_point_coords = []
        for pp in self.graph_points:
            new_point_coords.append(pp.getPos())

        self.coords = new_point_coords


class GraphHoverer:
    """ give it a graph, it will register the necessary hover event and on each
        mouse shift recalculate the new situation, i.e. go through all lines, find the nearest one
        and plot a connecting line """

    def __init__(self, draggablegraph, cameragear):
        # register event for onmousemove
        self.draggablegraph = draggablegraph
        self.cameragear = cameragear
        # self.mouse = mouse

        taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        base.accept('mouse1', self.onPress)

        self.hoverindicatorpoint = Point3d()

        # self.c1point = Point3d()

        # self.c2point = Point3d()

        self.shortest_distance_line = Line1dSolid(thickness=5, color=Vec4(1., 0., 1., 0.5))

        self.init_time_label()


    def mouseMoverTask(self, task):
        self.render_hints()
        return task.cont

    def onPress(self):
        self.render_hints()
        print("onPress")

    def render_hints(self):
        """ render various on-hover things:
            - cursors
            - time labels """
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()

            ray_direction, ray_aufpunkt = cameraray.getCameraMouseRay(
                self.cameragear.camera, base.mouseWatcherNode.getMouse())
            r1 = ray_aufpunkt
            e1 = ray_direction


            closestedge = None
            d_min = float('inf')

            # points of shortest edge_length
            c1_min = None
            c2_min = None

            for edge in self.draggablegraph.graph_edges:
                # find closest line (infinite straight)
                r2 = edge.getTailPoint()
                edge_p1 = r2
                edge_p2 = edge.getTipPoint()

                e2 = edge_p2 - edge_p1  # direction vector for edge infinite straight line

                d = np.abs(math_utils.shortestDistanceBetweenTwoStraightInfiniteLines(r1, r2, e1, e2))
                c1, c2 = math_utils.getPointsOfShortestDistanceBetweenTwoStraightInfiniteLines(
                    r1, r2, e1, e2)

                # only count this edge if the vector of shortest edge_length lies in-between the
                # start and end points of the line
                # if d is not None:
                # if d_min is None:
                #     d_min = d
                # if closestedge is None:
                #     closestedge = edge
                if c1_min is None:
                    c1_min = c1
                if c2_min is None:
                    c2_min = c2

                # conditions for closest edge
                # -    d < d_min
                # -    the line segment of shortest edge_length touches the edge's line within the
                #      two node points of the edge:
                #

                if d < d_min and math_utils.isPointBetweenTwoPoints(edge_p1, edge_p2, c1):
                    d_min = d
                    closestedge = edge

                    c1_min = c1
                    c2_min = c2

                    self.shortest_distance_line.setTipPoint(math_utils.np_to_p3d_Vec3(c1))
                    self.shortest_distance_line.setTailPoint(math_utils.np_to_p3d_Vec3(c2))
                    self.shortest_distance_line.nodePath.show()

                    # -- set the time label
                    # ---- set the position of the label to the position of the mouse cursor, but a bit higher
                    if closestedge is not None:
                        self.time_label.textNodePath.show()
                        self.time_label.setPos(*(ray_aufpunkt + ray_direction * 1.))

                        # figure out the parameter t
                        t = np.linalg.norm(closestedge.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(closestedge.getTailPoint() - closestedge.getTipPoint())

                        # print("t = np.linalg.norm(closestedge.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(closestedge.getTailPoint() - closestedge.getTipPoint())")
                        # print(t, "np.linalg.norm(", closestedge.getTailPoint(), " - ", math_utils.np_to_p3d_Vec3(c2), ")/, np.linalg.norm(", closestedge.getTailPoint(), " - ", closestedge.getTipPoint(), ")")

                        self.time_label.setText("t = {0:.2f}".format(t))
                        self.time_label.update()
                        self.time_label.textNodePath.setScale(0.04)

                    else:
                        self.time_label.textNodePath.hide()

            # -- color edges
            if closestedge is not None:
                for edge in self.draggablegraph.graph_edges:
                    # color all
                    edge.setColor((1., 1., 1., 1.), 1)
                    if edge is closestedge:
                        edge.setColor((1., 0., 0., 1.), 1)
            else:
                # hide the connection line
                self.shortest_distance_line.nodePath.hide()

                # make all the same color
                for edge in self.draggablegraph.graph_edges:
                    edge.setColor((1., 1., 1., 1.), 1)

            self.hoverindicatorpoint.nodePath.setPos(math_utils.np_to_p3d_Vec3(
                ray_aufpunkt + ray_direction * 1.))

            # -- color point
            # ---- find closest point,
            # within a certain radius (FIXME: automatically calculate that radius based on the
            # sorroundings)

            d_min_point = None
            closestpoint = None
            for point in self.draggablegraph.graph_points:
                d = np.linalg.norm(math_utils.p3d_to_np(point.getPos())
                                   - math_utils.p3d_to_np(ray_aufpunkt))
                if d_min_point is not None:
                    if d < d_min_point:
                        d_min_point = d
                        closestpoint = point
                else:
                    d_min_point = d
                    closestpoint = point

            # ---- color in point
            for point in self.draggablegraph.graph_points:
                point.nodePath.setColor((1., 0., 1., 1.), 1)

                if point is closestpoint:
                    point.nodePath.setColor((1., 0., 0., 1.), 1)
                else:
                    point.nodePath.setColor((1., 1., 1., 1.), 1)

    def init_time_label(self):
        """ show a text label at the position of the cursor:
            - set an event to trigger updating of the text on-hover
            - check if the active edge has changed """

        # init the textNode (there is one text node)
        pos_rel_to_world_x = Point3(1., 0., 0.)

        self.time_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="mytext",
                                        xshift=0.02, yshift=0.02, font="fonts/arial.egg")

        self.time_label.textNode.setTransform(
            math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))


from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval


class EdgePlayerState:
    """ You have an edge, and the states are
        1. stopped at beginning
        2. playing
        3. paused
        4. stopped at end
    This class is just for checking and changing the state.
    TODO: A class derived from EdgePlayerState will call it's functions and
    add the specific sequence commands after executing the state change functions. """
    def __init__(self):
        # TODO: set predefined initial state
        self.set_stopped_at_beginning()


    def set_stopped_at_beginning(self):
        self.a = 0.
        self.stopped = True
        self.paused = False  # undefined

    def is_stopped_at_beginning(self):
        return (self.a == 0. and self.stopped == True
                # self.paused = False  # undefined
        )


    def set_stopped_at_end(self):
        self.a = 1.
        self.stopped = True
        self.paused = False  # undefined

    def is_stopped_at_end(self):
        return (self.a == 1. and self.stopped == True
                # self.paused = False  # undefined
        )


    def set_playing(self, a_to_start_from=None):
        if a_to_start_from is None:
            a_to_start_from = self.a

        assert (a_to_start_from >= 0. and a_to_start_from <= 1.)
        self.a = a_to_start_from

        self.stopped = False
        self.paused = False

    def is_playing(self):
        return (a >= 0. and a <= 1. and self.stopped == False and self.paused == False)


    def set_paused(self, a_to_set_paused_at=None):
        if a_to_set_paused_at is None:
            a_to_set_paused_at = self.a

        assert (a_to_set_paused_at >= 0. and a_to_set_paused_at <= 1.)
        self.a = a_to_set_paused_at

        self.stopped = False  # in a stopped state, you can't pause
        self.paused = True


    def is_paused(self):
        return (a >= 0. and a <= 1. and self.stopped == False and self.paused == True)



class GraphPlayer:
    """
        - Plot a play/pause text and toggle it with space
        - give it a graph and call playfrom(edge, t between 0 and 1).
        - Show a cursor (thicker, smaller)
    """

    def __init__(self, draggablegraph, cameragear):
        # self.play_p = False  # play is true, pause is false

        # register event for onmousemove
        self.draggablegraph = draggablegraph
        self.cameragear = cameragear
        # self.mouse = mouse

        # taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        # base.accept('mouse1', self.onPress)

        # self.hoverindicatorpoint = Point3d()

        # self.shortest_distance_line = Line1dSolid(thickness=5, color=Vec4(1., 0., 1., 0.5))

        self.v1 = Vec3(0., 0., 0.)
        self.v2 = Vec3(2., 0., 0.)
        self.duration = 3.  # a relatively high number
        self.a = 0.  # a parameter between 0 and 1
        self.delay = 0.

        self.v_c = self.v1  # initially

        self.p1 = Point3d(scale=0.01, pos=self.v1)
        self.p2 = Point3d(scale=0.01, pos=self.v2)

        self.p_c = Point3d(scale=0.0125, pos=self.v1)
        self.p_c.setColor(((1., 0., 0., 1.), 1))

        self.l = Line1dSolid()
        self.l.setTailPoint(self.v1)
        self.l.setTipPoint(self.v2)

        self.extraArgs = [# self.duration,
                     self.v1, self.v2, self.v_c, # self.p1, self.p2,
            self.p_c]

        # self.p3d_interval = LerpFunc(
        #     GraphPlayer.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
        # self.play_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval)
        self.play_cursor_sequence = None

        self.stopped_at_end = False
        self.stopped_at_beginning = True

        # self.starting_edge = list(self.draggablegraph.graph_edges)[3]
        # self.active_edge = self.starting_edge

        # self.starting_time = 0.
        # self.a = self.starting_time

        self.paused_cursor_color = ((1., 0., 0., 1.), 1)
        self.playing_cursor_color = ((0., 1., 0., 1.), 1)

        # -- init play/pause actions
        # register space key to toggle play/pause
        play_pause_toggle_direct_object = DirectObject.DirectObject()
        play_pause_toggle_direct_object.accept('space', self.toggle_play_pause)

        # init the textNode (there is one text node)
        self.play_pause_label = (
            Fixed2dLabel(text="paused", font="fonts/arial.egg", xshift=0.1, yshift=0.1))

        self.pause_cursor()
        # self.init_cursor()


    # def get_cursor_data_from_edge(self, edge, t):
    #     """ t in [0, 1] """
    #     # t = 0.0

    #     # get the coordinates of the points of the edge
    #     edge_start_point = self.active_edge.getTailPoint()
    #     edge_end_point = self.active_edge.getTipPoint()

    #     assert edge_start_point != edge_end_point

    #     # calculate position at t
    #     pos_t = edge_start_point + (edge_end_point - edge_start_point) * t

    #     direction_vec = (edge_end_point - edge_start_point)/np.linalg.norm(edge_end_point - edge_start_point)

    #     edge_length = np.linalg.norm(math_utils.p3d_to_np(edge_end_point - edge_start_point))

    #     return edge_start_point, edge_end_point, pos_t, direction_vec, edge_length


    def toggle_play_pause(self):
        """ toggle or set the play/pause state, val=True for play, False for pause """

        if self.play_p is True:
            self.play_p = False
            self.play_pause_label.setText("paused")
            self.pause_cursor()

        elif self.play_p is False:
            self.play_p = True
            self.play_pause_label.setText("playing")
            self.play_cursor()
        else:
            print("Error: play_p has invalid value")


    # def init_cursor(self):
    #     """ render:
    #         - cursor of current time (disk perpendicular to edge)
    #         - current time label """

    #     edge_start_point, edge_end_point, pos_t, direction_vec, edge_length = (
    #         self.get_cursor_data_from_edge(self.active_edge, self.a))

    #     self.p_c = OrientedCircle(
    #         origin_point=pos_t,
    #         normal_vector_vec3=Vec3(*direction_vec),
    #         radius=0.035,
    #         num_of_verts=30,
    #         with_hole=False,
    #         thickness=3.)

    #     self.p_c.setColor(self.paused_cursor_color)

        # self.play_cursor()


    def play_cursor(self):
        self.play_p = True
        if self.a == 1.0:
            self.play_cursor_sequence.finish()
            return
        # assert self.play_p is True

        # edge_start_point, edge_end_point, pos_t, direction_vec, edge_length = (
        #     self.get_cursor_data_from_edge(self.active_edge, self.a))

        self.p_c.setColor(self.playing_cursor_color)

        # start or continue the sequence
        if self.play_cursor_sequence is None:
            # create it
            self.p3d_interval = LerpFunc(
                GraphPlayer.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
            self.play_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval, Func(self.finish_cursor))

            self.a = 0.
        else:
            if self.play_p is False:
                self.play_cursor_sequence.start(playRate=1.)
            else:
                self.play_cursor_sequence.resume()

            # assumption: returns value between 0 and 1
            self.a = self.play_cursor_sequence.get_t()/self.duration

            assert (self.a >= 0.0 and self.a <= 1.0)

    def pause_cursor(self):
        self.play_p = False
        if self.a == 1.0:
            self.play_cursor_sequence.finish()
            return
        # assert self.play_p is False

        self.p_c.setColor(self.paused_cursor_color)

        if self.play_cursor_sequence is None:
            # create the cursor
            self.p3d_interval = LerpFunc(
                GraphPlayer.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
            self.play_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval, Func(self.finish_cursor))
            self.a = 0.
            # print("this should never occurr")
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            # print("")
        else:
            self.a = self.play_cursor_sequence.get_t()/self.duration
            print("get_t(): ", self.a)
            print("paused at ", self.a)
            self.play_cursor_sequence.pause()

    def finish_cursor(self):
        if self.stopped_at_end is True:
            return

        self.play_p = False
        self.pause_cursor()

        self.p_c.setColor(self.paused_cursor_color)

        self.stopped_at_end = True
        # self.a = self.play_cursor_sequence.get_t()/self.duration
        self.a = self.play_cursor_sequence.set_t(self.duration)
        # print("get_t(): ", self.a)
        print("stopped at end: ", self.a)
        # self.play_cursor_sequence.pause()
        self.play_cursor_sequence.finish()

        self.play_cursor_sequence = None


# self.stopped_at_end = False
# self.stopped_at_beginning = True

    # def init_time_label(self):
    #     """ show a text label at the position of the cursor:
    #         - set an event to trigger updating of the text on-hover
    #         - check if the active edge has changed """

    #     # init the textNode (there is one text node)
    #     pos_rel_to_world_x = Point3(1., 0., 0.)

    #     self.time_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="mytext",
    #                                     xshift=0.02, yshift=0.02, font="fonts/arial.egg")

    #     self.time_label.textNode.hide()

    #     self.time_label.textNode.setTransform(
    #         math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))

    @staticmethod
    def update_position_func(a, # duration,
                             v1, v2, v_c, # p1, p2,
                             p_c):
            # assumption: t is a parameter between 0 and self.duration
            v21 = v2 - v1
            # a = t# /self.duration
            v_c = v1 + v21 * a
            p_c.nodePath.setPos(v_c)
            print(# "t = ", t,
                  # "; duration = ", duration,
                  "; a = ", a)

    # def mouseMoverTask(self, task):
    #     self.render_hints()
    #     return task.cont

    # def onPress(self):
    #     self.render_hints()
    #     print("onPress")
