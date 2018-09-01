import sys
sys.path.append("..")

import triangulator.main

import svgpathtools
import sys
import numpy as np

class IndexedGeometry:
    vertices = []
    triangle_indices = []


class Polygon: 
    def __init__(self, points=np.array([])):
        self.points = points
        self.indexed_geometry = IndexedGeometry()

    def addVertex(self, x, y):
        self.points = np.append(self.points, [x, y])

    def getVertices(self):
        return self.points


class OuterPolygon(Polygon):
    def __init__(self, points): 
        Polygon.__init__(self, points)


class InnerHolePolygon(Polygon):
    def __init__(self, points): 
        Polygon.__init__(self, points)

# and 8 has 1 outer polygon and 2 inner holes
# a large Theta has an outer polygon, an inner hole, and within that again an
# outer polygon
# I need to figure out if their svg paths look different (they must!)
# and then accordingly categorize them within these classes

class OuterPolygonWithInnerHolePolygons:  # e.g. an 8
    def __init__(self): 
        self.inner_hole_polygons = []
        self.outer_polygon = None
        self.indexed_geometry = IndexedGeometry()

    def addInnerHolePolygon(self, inner_hole_polygon):
        self.inner_hole_polygons.append(inner_hole_polygon)

    def setOuterPolygon(self, outer_polygon):
        self.outer_polygon = outer_polygon

        
def get_points_continuous_path_part(parsed_path):
    num_intermediate_points = 10.

    xs = []
    ys = []
    for segment in parsed_path: 
        xs.append(segment.start.real)
        ys.append(segment.start.imag)
        if type(segment) is svgpathtools.CubicBezier: 
            for i in np.arange(1., num_intermediate_points):  # This probably needs adjustment
                point = segment.point(i/num_intermediate_points)
                xs.append(point.real)
                ys.append(point.imag)

        xs.append(segment.end.real)
        ys.append(segment.end.imag)
    
    points = np.transpose([np.array(xs), np.array(ys)])
    return points


def get_OuterPolygonWithInnerHolePolygonss_from_svg_paths(svg_paths):
    outerPolygonWithInnerHolePolygonss = []

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    for svg_path in svg_paths:
        # split: without the M's in front, cut the first one off because it's ""
        pathSegs_strs = svg_path.d().split("M")[1:]
        # with the M's in front
        pathSegs_strs = ["M " + s for s in pathSegs_strs]
        # parse the individual segment of that one path
        parsed_continuous_path_parts = [svgpathtools.parse_path(x) for x in pathSegs_strs]
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        # categorize them into outer polygons with inner holes
        owip = OuterPolygonWithInnerHolePolygons()

        # if there's two moveto commands within a path, it has one hole
        points = get_points_continuous_path_part(parsed_continuous_path_parts[0])
        outerpolygon = OuterPolygon(points)
        owip.setOuterPolygon(outerpolygon)

        if len(parsed_continuous_path_parts) is 2:  # one hole
            points_inner = get_points_continuous_path_part(parsed_continuous_path_parts[1])
            innerpolygon = InnerHolePolygon(points_inner)
            owip.addInnerHolePolygon(innerpolygon)

        elif len(parsed_continuous_path_parts) > 2: 
            print("This case of nested polygons isn't handled yet")
            continue

        outerPolygonWithInnerHolePolygonss.append(owip)
        
    return outerPolygonWithInnerHolePolygonss


if __name__ == "__main__": 

    file = None
    if len(sys.argv) is 2: 
        file = sys.argv[1]
    else: 
        file = "main_simplified__customcleaned_.svg"

    # only need paths
    paths, _ = svgpathtools.svg2paths(file)

    # order them into the datastructures
    outerPolygonWithInnerHolePolygonss = get_OuterPolygonWithInnerHolePolygonss_from_svg_paths(paths)

    # now they are ready for the panda3d triangulator
    for owip in outerPolygonWithInnerHolePolygonss:
        import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        # TODO: remove inner hole polygons, and it works, with them it
        # doesn't work yet.
        vertices, triangle_indices = triangulator.main.triangulate_outer_polygon_with_hole_polygons(owip)

    print("end")

