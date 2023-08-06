"""
    Rogue-like map utility's such as line-of-sight, field-of-view, and path-finding.
    
"""
#import array
import ctypes
import itertools
import math

import untdl
# noinspection PyProtectedMember
from .__tcod import _lib, _PATHCALL

_FOVTYPES = {'BASIC': 0, 'DIAMOND': 1, 'SHADOW': 2, 'RESTRICTIVE': 12, 'PERMISSIVE': 11}


def _get_fov_type(fov):
    """Return a FOV from a string"""
    old_fov = fov
    fov = str(fov).upper()
    if fov in _FOVTYPES:
        return _FOVTYPES[fov]
    if fov[:10] == 'PERMISSIVE' and fov[10].isdigit() and fov[10] != '9':
        return 4 + int(fov[10])
    raise untdl.TDLError('No such fov option as %s' % old_fov)


# noinspection PyUnusedLocal
class AStar(object):
    """A* pathfinder
    
    Using this class requires a callback detailed in L{AStar.__init__}
    """

    __slots__ = ('_as_parameter_', '_callback', '__weakref__')

    def __init__(self, width, height, callback,
                 digital_cost=math.sqrt(2), advanced=False):
        """Create an A* pathfinder using a callback.
        
        Before crating this instance you should make one of two types of
        callbacks:
         - A function that returns the cost to move to (x, y)
        or
         - A function that returns the cost to move between
           (destX, destY, sourceX, sourceY)
        If path is blocked the function should return zero or None.
        When using the second type of callback be sure to set advanced=True
        
        @type width: int
        @param width: width of the pathfinding area in tiles
        @type height: int
        @param height: height of the pathfinding area in tiles
        
        @type callback: function
        @param callback: A callback taking parameters depending on the setting
                         of 'advanced' and returning the cost of
                         movement for an open tile or zero for a
                         blocked tile.
        
        @type digital_cost: float
        @param digital_cost: Multiplier for diagonal movement.
        
                            Can be set to zero to disable diagonal movement
                            entirely.
        
        @type advanced: boolean
        @param advanced: A simple callback with 2 positional parameters may not
                         provide enough information.  Setting this to True will
                         call the callback with 2 additional parameters giving
                         you both the destination and the source of movement.
                         
                         When True the callback will need to accept
                         (destX, destY, sourceX, sourceY) as parameters.
                         Instead of just (destX, destY).
                         
        """
        if not digital_cost:  # set None or False to zero
            digital_cost = 0.0
        if advanced:
            def new_callback(source_x, source_y, dest_x, dest_y, null):
                path_cost = callback(dest_x, dest_y, source_x, source_y)
                if path_cost:
                    return path_cost
                return 0.0
        else:
            def new_callback(source_x, source_y, dest_x, dest_y, null):
                path_cost = callback(dest_x, dest_y)  # expecting a float or 0
                if path_cost:
                    return path_cost
                return 0.0
        self._callback = _PATHCALL(new_callback)
        """A CFUNCTYPE callback to be kept in memory."""
        self._as_parameter_ = _lib.TCOD_path_new_using_function(width, height,
                                                                self._callback, None, digital_cost)

    def __del__(self):
        _lib.TCOD_path_delete(self)

    def get_path(self, orig_x, orig_y, dest_x, dest_y):
        """
        Get the shortest path from origXY to destXY.
        
        @rtype: [(x, y), ...]
        @return: Returns a list walking the path from origXY to destXY.
                 This excludes the starting point and includes the destination.
                 
                 If no path is found then an empty list is returned.
        """
        found = _lib.TCOD_path_compute(self, orig_x, orig_y, dest_x, dest_y)
        if not found:
            return []  # path not found
        x, y = ctypes.c_int(), ctypes.c_int()
        xref, yref = ctypes.byref(x), ctypes.byref(y)
        recalculate = ctypes.c_bool(True)
        path = []
        while _lib.TCOD_path_walk(self, xref, yref, recalculate):
            path.append((x.value, y.value))
        return path


def quick_fov(x, y, callback, fov='PERMISSIVE', radius=7.5, light_walls=True, sphere=True):
    """All field-of-view functionality in one call.
    
    Before using this call be sure to make a function, lambda, or method that takes 2
    positional parameters and returns True if light can pass through the tile or False
    for light-blocking tiles and for indexes that are out of bounds of the
    dungeon.
    
    This function is 'quick' as in no hassle but can quickly become a very slow
    function call if a large radius is used or the callback provided itself
    isn't optimized.
    
    Always check if the index is in bounds both in the callback and in the
    returned values.  These values can go into the negatives as well.
    
    @type x: int
    @param x: x center of the field-of-view
    @type y: int
    @param y: y center of the field-of-view
    @type callback: function
    @param callback: This should be a function that takes two positional arguments x,y
                     and returns True if the tile at that position is transparent
                     or False if the tile blocks light or is out of bounds.
    @type fov: string
    @param fov: The type of field-of-view to be used.  Available types are:
    
                'BASIC', 'DIAMOND', 'SHADOW', 'RESTRICTIVE', 'PERMISSIVE',
                'PERMISSIVE0', 'PERMISSIVE1', ..., 'PERMISSIVE8'
    @type radius: float
    @param radius: Radius of the field-of-view.
    
                   When sphere is True a floating point can be used to fine-tune
                   the range.  Otherwise the radius is just rounded up.
    
                   Be careful as a large radius has an exponential affect on
                   how long this function takes.
    @type light_walls: boolean
    @param light_walls: Include or exclude wall tiles in the field-of-view.
    @type sphere: boolean
    @param sphere: True for a spherical field-of-view.  False for a square one.
    
    @rtype: set((x, y), ...)
    @return: Returns a set of (x, y) points that are within the field-of-view.
    """
    true_radius = radius
    radius = int(math.ceil(radius))
    map_size = radius * 2 + 1
    fov = _get_fov_type(fov)

    set_prop = _lib.TCOD_map_set_properties  # make local
    in_fov = _lib.TCOD_map_is_in_fov

    #  ctrue = ctypes.c_bool(1)
    cfalse = ctypes.c_bool(False)
    tcod_map = _lib.TCOD_map_new(map_size, map_size)
    try:
        # pass one, write callback data to the tcod_map
        for (x_, cX), (y_, cY) in itertools.product(((i, ctypes.c_int(i)) for i in range(map_size)),
                                                    ((i, ctypes.c_int(i)) for i in range(map_size))):
            pos = (x_ + x - radius,
                   y_ + y - radius)
            transparent = bool(callback(*pos))
            set_prop(tcod_map, cX, cY, transparent, cfalse)

        # pass two, compute fov and build a list of points
        _lib.TCOD_map_compute_fov(tcod_map, radius, radius, radius, light_walls, fov)
        touched = set()  # points touched by field of view
        for (x_, cX), (y_, cY) in itertools.product(((i, ctypes.c_int(i)) for i in range(map_size)),
                                                    ((i, ctypes.c_int(i)) for i in range(map_size))):
            if sphere and math.hypot(x_ - radius, y_ - radius) > true_radius:
                continue
            if in_fov(tcod_map, cX, cY):
                touched.add((x_ + x - radius, y_ + y - radius))
    finally:
        _lib.TCOD_map_delete(tcod_map)
    return touched


def bresenham(x1, y1, x2, y2):
    """
    Iterate over points in a bresenham line.
    
    Implementation hastily copied from RogueBasin.
    
    @return: Returns an iterator of (x, y) points.
    """
    points = []
    is_steep = abs(y2 - y1) > abs(x2 - x1)
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    dx = x2 - x1
    dy = abs(y2 - y1)
    error = int(dx / 2)
    y = y1
    if y1 < y2:
        y_step = 1
    else:
        y_step = -1
    for x in range(x1, x2 + 1):
        if is_steep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= dy
        if error < 0:
            y += y_step
            error += dx
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return iter(points)  # force as iter so I can sleep at night


__all__ = ['AStar', 'quick_fov']
