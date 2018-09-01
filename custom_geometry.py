from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    Geom, GeomVertexWriter,
    GeomTriangles,
    GeomTrifans,
    GeomLinestrips,
    GeomNode, 
    Vec4)

from math import pi, cos

import numpy as np


def createTexturedUnitQuadGeomNode():
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3t2()
    vdata = GeomVertexData("textured_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    vertexPosWriter.addData3f(0, 0, 0)
    vertexPosWriter.addData3f(1, 0, 0)
    vertexPosWriter.addData3f(1, 0, 1)
    vertexPosWriter.addData3f(0, 0, 1)

    # let's also add color to each vertex
    # colorWriter = GeomVertexWriter(vdata, "color")
    # colorWriter.addData4f(0,0,1,1)
    # colorWriter.addData4f(0,0,1,1)
    # colorWriter.addData4f(0,0,1,1)
    # colorWriter.addData4f(0,0,1,1)

    # let's add texture coordinates (u,v)
    texcoordWriter = GeomVertexWriter(vdata, "texcoord")
    texcoordWriter.addData2f(0, 0)
    texcoordWriter.addData2f(1, 0)
    texcoordWriter.addData2f(1, 1)
    texcoordWriter.addData2f(0, 1)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # 1st triangle
    tris.addVertices(0, 1, 3)
    tris.closePrimitive()  # the 1st primitive is finished

    # 2nd triangle
    tris.addVertices(1, 2, 3)
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    quadGeom = Geom(vdata)
    quadGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    quadGN = GeomNode("quad")
    quadGN.addGeom(quadGeom)

    return quadGN


def createColoredUnitQuadGeomNode(color_vec4=Vec4(0., 0., 1., 1.)):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    vertexPosWriter.addData3f(0, 0, 0)
    vertexPosWriter.addData3f(1, 0, 0)
    vertexPosWriter.addData3f(1, 0, 1)
    vertexPosWriter.addData3f(0, 0, 1)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # 1st triangle
    tris.addVertices(0, 1, 3)
    tris.closePrimitive()  # the 1st primitive is finished

    # 2nd triangle
    tris.addVertices(1, 2, 3)
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    quadGeom = Geom(vdata)
    quadGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    quadGN = GeomNode("colored_quad_node")
    quadGN.addGeom(quadGeom)

    return quadGN


def createColoredArrowGeomNode(color_vec4=Vec4(0., 0., 1., 1.)):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    vertexPosWriter.addData3f(0, 0, 0)
    vertexPosWriter.addData3f(0, 0, 1)
    vertexPosWriter.addData3f(cos(pi / 6.), 0., .5)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # 1st triangle
    tris.addVertices(0, 2, 1)
    tris.closePrimitive()  # the 1st primitive is finished

    # make a Geom object to hold the primitives
    quadGeom = Geom(vdata)
    quadGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    quadGN = GeomNode("colored_quad_node")
    quadGN.addGeom(quadGeom)

    return quadGN


def create_colored_polygon2d_GeomNode_from_point_cloud(point_cloud, color_vec4=Vec4(0., 0., 1., 1.)):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)
    
    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    for point in point_cloud: 
        vertexPosWriter.addData3f(point[0], 0, point[1])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomLinestrips(Geom.UHStatic)

    tris.add_consecutive_vertices(0, len(point_cloud))
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    polygonGeom = Geom(vdata)
    polygonGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    polygonGN = GeomNode("colored_polygon_node")
    polygonGN.addGeom(polygonGeom)

    return polygonGN

def create_GeomNode_Simple_Polygon_with_Hole():

    color_vec4=Vec4(1., 1., 1., 1.)
    outerpolygon_contour_points = (
        np.array([(0, 1), (-1, 0), (0, -1), (1, 0)], dtype=np.float64))
    inner_hole_contour_points = 0.5 * (
        np.array([(0, 1), (-1, 0), (0, -1), (1, 0)], dtype=np.float64))

    from panda3d.core import Triangulator, LPoint2d
    
    tr = Triangulator()

    for vertex in outerpolygon_contour_points: 
        vi = tr.addVertex(vertex[0], vertex[1])
        tr.addPolygonVertex(vi)

    tr.beginHole()
    for vertex in inner_hole_contour_points:
        vi = tr.addVertex(vertex[0], vertex[1])
        tr.addHoleVertex(vi)

    tr.triangulate()
    
    vertices = tr.getVertices()

    indices = []
    num_triangles = tr.getNumTriangles()
    for i in range(num_triangles):
        indices.append([tr.getTriangleV0(i), tr.getTriangleV1(i), tr.getTriangleV2(i)])

    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)
    
    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    for v in vertices: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic) 
    
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    for index_triple in indices: 
        tris.addVertices(index_triple[0], index_triple[1], index_triple[2])

    tris.closePrimitive()

    # make a Geom object to hold the primitives
    polygonGeom = Geom(vdata)  # vdata contains the vertex position/color/... buffers
    polygonGeom.addPrimitive(tris)  # tris contains the index buffer

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    polygonGN = GeomNode("colored_polygon_node")
    polygonGN.addGeom(polygonGeom)

    return polygonGN

def create_GeomNode_Simple_Polygon_with_Hole_LineStrips():

    color_vec4=Vec4(1., 1., 1., 1.)
    outerpolygon_contour_points = (
        np.array([(0, 1), (-1, 0), (0, -1), (1, 0)], dtype=np.float64))
    inner_hole_contour_points = 0.5 * (
        np.array([(0, 1), (-1, 0), (0, -1), (1, 0)], dtype=np.float64))

    from panda3d.core import Triangulator, LPoint2d
    
    # tr = Triangulator()

    # for vertex in outerpolygon_contour_points: 
    #     vi = tr.addVertex(vertex[0], vertex[1])
    #     tr.addPolygonVertex(vi)

    # tr.beginHole()
    # for vertex in inner_hole_contour_points:
    #     vi = tr.addVertex(vertex[0], vertex[1])
    #     tr.addHoleVertex(vi)

    # tr.triangulate()
    
    # vertices = tr.getVertices()

    # indices = []
    # num_triangles = tr.getNumTriangles()
    # for i in range(num_triangles):
    #     indices.append([tr.getTriangleV0(i), tr.getTriangleV1(i), tr.getTriangleV2(i)])

    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)
    
    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    for v in outerpolygon_contour_points: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)
    
    for v in inner_hole_contour_points: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    # tris = GeomTriangles(Geom.UHStatic) 
    
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    tris = GeomLinestrips(Geom.UHStatic)

    # for index_triple in indices: 
    #     tris.addVertices(index_triple[0], index_triple[1], index_triple[2])
    tris.add_consecutive_vertices(0, len(outerpolygon_contour_points))
    tris.closePrimitive()

    tris.add_consecutive_vertices(len(outerpolygon_contour_points), len(inner_hole_contour_points))
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    polygonGeom = Geom(vdata)  # vdata contains the vertex position/color/... buffers
    polygonGeom.addPrimitive(tris)  # tris contains the index buffer

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    polygonGN = GeomNode("colored_polygon_node")
    polygonGN.addGeom(polygonGeom)

    return polygonGN

