from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4

import numpy as np
import math


# ---- active euler rotation matrices
def get_R_x(angle):
    return np.array([[1, 0, 0],
                     [0, math.cos(angle), -math.sin(angle)],
                     [0, math.sin(angle), math.cos(angle)]])

def get_R_y(angle):
    return np.array([[math.cos(angle), 0, math.sin(angle)],
                     [0, 1, 0],
                     [-math.sin(angle), 0, math.cos(angle)]])

def get_R_z(angle):
    return np.array([[math.cos(angle), -math.sin(angle), 0],
                     [math.sin(angle), math.cos(angle), 0],
                     [0, 0, 1]])


def get_R_x_forrowvecs(angle):
    return to_forrowvecs(make_3x3_matrix_affine(get_R_x(angle)))

def get_R_y_forrowvecs(angle):
    return to_forrowvecs(make_3x3_matrix_affine(get_R_y(angle)))

def get_R_z_forrowvecs(angle):
    return to_forrowvecs(make_3x3_matrix_affine(get_R_z(angle)))


def make_3x3_matrix_affine(m):
    """
    m is a 3x3 matrix
    just append the fourth column and row
    of the 4x4 identity matrix
    """

    return np.array(
        [[m[0][0], m[0][1], m[0][2], 0.],
         [m[1][0], m[1][1], m[1][2], 0.],
         [m[2][0], m[2][1], m[2][2], 0.],
         [0,       0,       0, 1.]])

def to_forrowvecs(m4x4):
    """
    p3d uses internally a different matrix multiplication style
    than is traditionally used in math. This function converts the
    traditional format of a matrix into the p3d format.

    Parameters:
    - m4x4 is a 4x4 matrix in the not-forrowvecs (normal) format
    """
    return Mat4(*tuple(np.transpose(m4x4).flatten()))

def getScalingMatrix4x4(vx, vy, vz):
    """ in usual math notation convention, not in p3d hardware-optimized convention """
    return np.array([[vx,  0,  0, 0],
                     [0,  vy,  0, 0],
                     [0,   0, vz, 0],
                     [0,   0,  0, 1]])

def getTranslationMatrix3d_forrowvecs(bx, by, bz):
    # bx = 0.5
    # by = 0
    # bz = 0
    translation_to_xhat = np.array(
        [[1, 0, 0, bx],
         [0, 1, 0, by],
         [0, 0, 1, bz],
         [0, 0, 0,  1]])
    translation_forrowvecs = Mat4(
        *tuple(np.transpose(translation_to_xhat).flatten()))
    return translation_forrowvecs


def getNormFromP3dVector(p3dvec3):
    return np.linalg.norm([p3dvec3.getX(), p3dvec3.getY(), p3dvec3.getZ()])


def LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
    """
    quickly taken from https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python
    Returns the intersection point
    """

    ndotu = planeNormal.dot(rayDirection)
    if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")

    w = rayPoint - planePoint
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si * rayDirection + planePoint
    return Psi


def p3d_to_np(p3d_3f):
    return np.array([p3d_3f[0], p3d_3f[1], p3d_3f[2]])


def getMat4by4_to_rotate_xhat_to_vector(target_position_vector, a=np.array([1., 0., 0.], dtype=np.float)):
    """ Apply the rodriguez formula to get the rotation matrix to rotate [1., 0., 0.] to an arbitrary position vector """

    # --- Rodriguez rotation formula ---
    # apply rodriguez formula to rotate the geometrie's given
    # a e.g. = [1, 0, 0] vector to the destination vector v

    target_position_vector = np.array([target_position_vector[0], target_position_vector[1], target_position_vector[2]], dtype=np.float)
    b = target_position_vector

    theta = np.arccos(
        np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    R = None
    epsilon = 0.0000001
    if theta < epsilon:  # edge case: parallel
        # in this case, you can't divide by zero to get the rotation axis x
        R = np.identity(3, dtype=np.float)
    elif np.pi - theta < epsilon:  # edge case: antiparallel
        # find a vector orthogonal to a,
        # for this, e.g. first find the component of least magnitude
        # of a, then calculate the cross product of the
        # corresponding standard
        # unit vector with a, which cannot be zero in magnitude

        i = min(np.where(a == np.min(a))[0])

        # chop up identity matrix to get the standard unit vector
        e_i = np.identity(3)[i]

        x = np.cross(a, e_i) / np.linalg.norm(np.cross(a, e_i))

        A = np.array([
            [0.,    -x[2],  x[1]],
            [x[2],  0.,    -x[0]],
            [-x[1], x[0],   0.]
        ], dtype=np.float)

        R = (np.identity(3, dtype=np.float) + np.sin(theta) * A
         + (1. - np.cos(theta)) * np.matmul(A, A))
    else:
        x = np.cross(a, b) / np.linalg.norm(np.cross(a, b))

        A = np.array([
            [0.,    -x[2],  x[1]],
            [x[2],  0.,    -x[0]],
            [-x[1], x[0],   0.]
        ], dtype=np.float)

        R = (np.identity(3, dtype=np.float) + np.sin(theta) * A
         + (1. - np.cos(theta)) * np.matmul(A, A))

    R_4by4 = np.array(
        [
            [R[0][0], R[0][1], R[0][2], 0.],
            [R[1][0], R[1][1], R[1][2], 0.],
            [R[2][0], R[2][1], R[2][2], 0.],
            [0., 0., 0., 1.]
        ]
    )

    return R_4by4


def math_convention_to_p3d_mat4(mat4):
    """ convert numpy 4x4 matrix in usual math convention to hardware-optimized p3d matrix representation
    (by entering the components into p3d's Mat4 function in the usual order) """
    return Mat4(*tuple(np.transpose(mat4).flatten()))


def getPointsAndPathLengthsAlongPolygonalChain(
        func=(lambda t: np.array([t, t, t])),
        param_interv=np.array([0, 1]),
        ed_subpath_length=0.25,  # this parameter is key, for each specific curve that's drawn, it has to be changed
        thickness=1.,
        howmany_points=50,
        radius=0.1):
    """ Get all finer points along a coarsely calculated polygonal chain, alongside with the path lengths between them
        (equidistant in terms of path length differences along the coarse polygonal chain (so it's not perfectly accurate,
         especially if the path is calculated coarsely)). """

    # collect all the vertices of the draw_to call where a segment ends. Those are the approximate points I'm looking for

    t = np.linspace(param_interv[0], param_interv[1], num=howmany_points, endpoint=True)
    points = np.array([func(ti) for ti in t])

    points_finer = []
    path_lengths = []

    # ed_subpath_length = 0.25
    remaining_ed_subpath_length = ed_subpath_length

    # current point indices
    ip1 = 0
    ip2 = 1

    remaining_pp_length = np.linalg.norm(points[ip1] - points[ip2])
    measure_from_point = points[ip1]

    points_finer.append(measure_from_point)
    path_lengths.append(0.)

    while True:
        remaining_pp_length = np.linalg.norm(points[ip2] - measure_from_point)
        if remaining_ed_subpath_length <= remaining_pp_length:
            new_finer_point = measure_from_point + remaining_ed_subpath_length * (points[ip2] - measure_from_point)/np.linalg.norm(points[ip2] - measure_from_point)

            points_finer.append(new_finer_point)
            path_lengths.append(np.linalg.norm(points_finer[-1] - points_finer[-2]))

            measure_from_point = new_finer_point
            remaining_ed_subpath_length = ed_subpath_length
        else:
            remaining_ed_subpath_length -= np.linalg.norm(points[ip2] - measure_from_point)
            measure_from_point = points[ip2]
            if ip2 < len(points) - 1:  # i.e. if it's a len(points) == 2 array, then the max index is 1
                ip1 += 1
                ip2 += 1
            else:
                break

    return points_finer, path_lengths


def normalize(vec3_np):
    """ given a 3d numpy vector, normalize it """
    return vec3_np / np.linalg.norm(vec3_np)
