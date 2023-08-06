import sys as _sys
import argparse as _argparse
import unittest as _unittest
import collections as _collections
import pprint as _pprint
import math as _math
import functools as _functools
import operator as _operator
import multiprocessing as _multiprocessing
import itertools as _itertools


__version__ = '0.0.15'


class Error(Exception):
    pass


TICK_INTERVAL_PADDING_RATIO = 0.1


GOLDEN_RATIO = (1 + _math.sqrt(5))/2
_SPHERE_MESH_BASES = {
    4: ([(0, 1, 2),
         (1, 2, 3),
         (2, 3, 0),
         (0, 1, 3)],
        [(0, 0, 1),
         (2*_math.sqrt(2)/3, 0, -1/3),
         (-_math.sqrt(2)/3, _math.sqrt(2/3), -1/3),
         (-_math.sqrt(2)/3, -_math.sqrt(2/3), -1/3)],
        1),
    8: ([(4, 0, 1),
         (4, 1, 2),
         (4, 2, 3),
         (4, 3, 0),
         (5, 0, 1),
         (5, 1, 2),
         (5, 2, 3),
         (5, 3, 0)],
        [(1, 0, 0),
         (0, 1, 0),
         (-1, 0, 0),
         (0, -1, 0),
         (0, 0, 1),
         (0, 0, -1)],
        1),
    # http://en.wikipedia.org/wiki/Icosahedron#Cartesian_coordinates
    20: ([(8, 9, 5),
          (8, 9, 4),
          (7, 5, 2),
          (7, 5, 3),
          (3, 1, 9),
          (3, 1, 11),
          (4, 6, 1),
          (4, 6, 0),
          (0, 2, 8),
          (0, 2, 10),
          (10, 11, 6),
          (10, 11, 7),
          (2, 8, 5),
          (8, 4, 0),
          (0, 6, 10),
          (10, 7, 2),
          (5, 3, 9),
          (9, 4, 1),
          (1, 6, 11),
          (11, 3, 7)],
         [(0, 1, GOLDEN_RATIO),
          (0, 1, -GOLDEN_RATIO),
          (0, -1, GOLDEN_RATIO),
          (0, -1, -GOLDEN_RATIO),
          (1, GOLDEN_RATIO, 0),
          (1, -GOLDEN_RATIO, 0),
          (-1, GOLDEN_RATIO, 0),
          (-1, -GOLDEN_RATIO, 0),
          (GOLDEN_RATIO, 0, 1),
          (GOLDEN_RATIO, 0, -1),
          (-GOLDEN_RATIO, 0, 1),
          (-GOLDEN_RATIO, 0, -1)],
         _math.sqrt(1**2 + GOLDEN_RATIO**2)),
}
def sphere_mesh(n=0, r=1, base=20):
    assert n >= 0
    triangles, points, r_ = _SPHERE_MESH_BASES[base]
    points_ = []
    for x, y, z in points:
        points_.append((r*x/r_, r*y/r_, r*z/r_))
    for _ in range(0, n):
        new_triangles = []
        for triangle in triangles:
            new_triangles = _itertools.chain(new_triangles, _divide_triangle(triangle, points_))
        triangles = new_triangles
    return list(triangles), points_


def _divide_triangle(triangle, points):
    i_p1, i_p2, i_p3 = triangle
    p1 = points[i_p1]
    p2 = points[i_p2]
    p3 = points[i_p3]
    n_points = len(points)
    p12 = _unit_middle_point(p1, p2)
    points.append(p12)
    i_p12 = n_points + 0
    p23 = _unit_middle_point(p2, p3)
    points.append(p23)
    i_p23 = n_points + 1
    p31 = _unit_middle_point(p3, p1)
    points.append(p31)
    i_p31 = n_points + 2
    return (i_p1, i_p12, i_p31), (i_p2, i_p12, i_p23), (i_p3, i_p23, i_p31), (i_p12, i_p23, i_p31)


def _unit_middle_point(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x = (x1 + x2)/2
    y = (y1 + y2)/2
    z = (z1 + z2)/2
    r = _math.sqrt(x**2 + y**2 + z**2)
    return x/r, y/r, z/r


def is_in_convex_hull(px, py, xys, is_counterclockwise=True):
    if not is_counterclockwise:
        return is_in_convex_hull(px, py, list(reversed(xys)))
    else:
        assert is_convex(xys, is_counterclockwise)
        x1, y1 = xys[0]
        x1 -= px
        y1 -= py
        for x2, y2 in _itertools.chain(xys, xys[0:1]):
            x2 -= px
            y2 -= py
            if x1*y2 - y1*x2 < 0:
                return False
            x1 = x2
            y1 = y2
        return True


def is_convex(xys, is_counterclockwise=True):
    if not is_counterclockwise:
        return is_convex(list(reversed(xys)))
    else:
        assert len(xys) >= 3
        (x1, y1), (x2, y2), *more = xys
        for x3, y3 in _itertools.chain(more, xys[0:1]):
            dx12 = x2 - x1
            dy12 = y2 - y1
            dx23 = x3 - x2
            dy23 = y3 - y2
            if dx12*dy23 - dy12*dx23 < 0:
                return False
            x1 = x2
            y1 = y2
            x2 = x3
            y2 = y3
        return True


def each_cons(xs, n):
    assert n >= 1
    return [xs[i:i+n] for i in range(len(xs) - (n - 1))]


def parallel_for(f, *indicess):
    return reshape(_multiprocessing.Pool().starmap(f, _itertools.product(*indicess)),
                   [len(indices) for indices in indicess])


def reshape(xs, ns):
    assert ns
    assert len(xs) == _functools.reduce(_operator.mul, ns, 1)
    return _reshape(xs, ns)


def _reshape(xs, ns):
    if len(ns) == 1:
        return xs
    return _reshape(partition(xs, ns[-1]), ns[0:-1])


def partition(xs, n):
    return [xs[i-n:i] for i in range(n, len(xs) + 1, n)]


def memoize(f):
    cache = {}
    def memoized_f(*args):
        if args in cache:
            return cache[args]
        else:
            cache[args] = retv = f(*args)
            return retv
    memoized_f.cache = cache
    return memoized_f


def profiled_memoize(f):
    cache = {}
    profile = {'new': 0,
               'hit': 0}
    def profiled_memoized_f(*args):
        if args in cache:
            profile['hit'] += 1
            return cache[args]
        else:
            profile['new'] += 1
            cache[args] = retv = f(*args)
            return retv
    profiled_memoized_f.cache = cache
    profiled_memoized_f.profile = profile
    return profiled_memoized_f


def _get_interval(lx):
    assert lx > 0
    dx = 10**(_math.ceil(_math.log10(lx)) - 1)
    if lx > 5*dx:
        return dx
    elif lx > 2*dx:
        return 5*dx/10
    else:
        return 2*dx/10


def _get_lower_limit(x, dx,
                     padding_ratio=TICK_INTERVAL_PADDING_RATIO):
    assert dx > 0
    lower = _math.floor(x/dx)*dx
    if x <= lower + dx*padding_ratio:
        lower -= dx
    return lower


def _get_upper_limit(x, dx,
                     padding_ratio=TICK_INTERVAL_PADDING_RATIO):
    assert dx > 0
    upper = _math.ceil(x/dx)*dx
    if x >= upper - dx*padding_ratio:
        upper += dx
    return upper


def get_tick_configurations(x1, x2,
                            padding_ratio=TICK_INTERVAL_PADDING_RATIO):
    x_small, x_large = sorted([x1, x2])
    dx = _get_interval(x_large - x_small)
    lower = _get_lower_limit(x_small, dx, padding_ratio)
    upper = _get_upper_limit(x_large, dx, padding_ratio)
    return lower, upper, dx


def pp(x):
    _pprint.pprint(x, stream=_sys.stderr)
    return x


def flatten(xss):
    """
    # Flatten containers

    ## Note
    Do not include recursive elements.

    ## Exceptions
    - `RuntimeError`: Recursive elements will cause this
    """
    if isinstance(xss, str):
        yield xss
    else:
        for xs in xss:
            if isinstance(xs, _collections.Iterable):
                for x in flatten(xs):
                    yield x
            else:
                yield xs


def list_2d(n_row, n_column, init=None):
    assert n_row >= 1
    assert n_column >= 1

    return [[init
             for _
             in range(n_column)]
            for _
            in range(n_row)]


def make_fixed_format_parser(fields):
    """
    fields: (('density', 3, int),
             ('opacity', 7, float))
    """
    lower = 0
    _fields = []
    for field in fields:
        name, length, converter = field
        assert length >= 1
        upper = lower + length
        _fields.append((name, lower, upper, converter))
        lower = upper

    def fixed_format_parser(s):
        assert len(s) >= upper
        return {name: converter(s[lower:upper])
                for name, lower, upper, converter
                in _fields}
    return fixed_format_parser


class TestAction(_argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=_argparse.SUPPRESS,
                 default=_argparse.SUPPRESS,
                 help=None):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         default=default,
                         nargs=0,
                         help=help)


    def __call__(self, parser, namespace, values, option_string=None):
        _unittest.main(argv=_sys.argv[:1])
        parser.exit()


def _fn_for_test_parallel_for(x, y):
    return x, y


class _Tester(_unittest.TestCase):

    def test_sphere_mesh(self):
        triangles, points = sphere_mesh(n=2, base=4)
        self.assertEqual(len(triangles), 4**3)
        self.assertEqual(len(points), 4**3)

    def test__divide_triangle(self):
        points = [(0, 0, 1), (1, 0, 0), (0, 1, 0)]
        triangles = _divide_triangle((0, 1, 2), points)
        self.assertEqual(triangles, ((0, 3, 5), (1, 3, 4), (2, 4, 5), (3, 4, 5)))
        self.assertEqual(points, [(0, 0, 1),
                                  (1, 0, 0),
                                  (0, 1, 0),
                                  (0.7071067811865475, 0.0, 0.7071067811865475),
                                  (0.7071067811865475, 0.7071067811865475, 0.0),
                                  (0.0, 0.7071067811865475, 0.7071067811865475)])

    def test_is_in_convex_hull(self):
        with self.assertRaises(AssertionError):
            is_in_convex_hull(1, 2, [(0, 0),
                                     (1, 0),
                                     (1, -1)])
        self.assertTrue(is_in_convex_hull(0, 0, [(0, 0),
                                                 (1, 0),
                                                 (1, 1)]))
        xys = [(0, 0),
               (2, 0),
               (2, 1),
               (2, 2),
               (1, 2)]
        self.assertTrue(is_in_convex_hull(1, 1, xys))
        self.assertTrue(is_in_convex_hull(1, 1, list(reversed(xys)), False))
        self.assertFalse(is_in_convex_hull(3, 3, xys))

    def test_is_convex(self):
        with self.assertRaises(AssertionError):
            is_convex([])
        with self.assertRaises(AssertionError):
            is_convex([(1, 2)])
        with self.assertRaises(AssertionError):
            is_convex([(1, 2), (3, 4)])
        self.assertTrue(is_convex([(0, 0),
                                   (1, 0),
                                   (0.5, 1)]))
        self.assertTrue(is_convex([(0, 0),
                                   (1, 0),
                                   (1, 1),
                                   (1, 2),
                                   (0, 1)]))
        self.assertFalse(is_convex([(0, 0),
                                    (1, 0),
                                    (0.5, 1),
                                    (0, 5)]))
        self.assertFalse(is_convex([(0, 0),
                                    (0.5, 1),
                                    (1, 0)]))
        self.assertTrue(is_convex([(0, 0),
                                   (0.5, 1),
                                   (1, 0)],
                                  False))


    def test_each_cons(self):
        with self.assertRaises(AssertionError):
            each_cons([1, 2, 3], 0)

        for xs, n, expected in (
                ([], 1, [],),
                ([1, 2, 3], 1, [[1], [2], [3]],),
                ([1, 2, 3], 2, [[1, 2], [2, 3]],),
                ([1, 2, 3], 3, [[1, 2, 3]],),
                ([1, 2, 3], 4, [],),
        ):
            self.assertEqual(each_cons(xs, n), expected)

    def test_parallel_for(self):
        self.assertEqual(parallel_for(_fn_for_test_parallel_for, [1, 2], [3, 4, 5]), [[(1, 3), (1, 4), (1, 5)], [(2, 3), (2, 4), (2, 5)]])

    def test_reshape(self):
        with self.assertRaises(AssertionError):
            reshape((1,), ())
        with self.assertRaises(AssertionError):
            reshape((1, 2, 3), (2, 2))

        for xs, ns, expected in (
                ([1, 2, 3], (3,), [1, 2, 3]),
                ([1, 2, 3], (3, 1), [[1], [2], [3]]),
                ([1, 2, 3, 4], (2, 2), [[1, 2], [3, 4]]),
                ([1, 2, 3, 4, 5, 6], (2, 3), [[1, 2, 3], [4, 5, 6]]),
                ([1, 2, 3, 4, 5, 6, 7, 8], (2, 2, 2), [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]),
        ):
            self.assertEqual(reshape(xs, ns), expected)

    def test_partition(self):
        with self.assertRaises(ValueError):
            partition((1, 2), 0)

        for xs, n, expected in (
                ((), -1, []),
                ((1, 2), -1, []),

                ((), 1, []),
                ((), 2, []),

                ([1, 3], 1, [[1], [3]]),
                ([1, 4], 2, [[1, 4]]),
                ([1, 5], 3, []),
        ):
            self.assertEqual(partition(xs, n), expected)

    def test__get_interval(self):
        with self.assertRaises(AssertionError):
            _get_interval(-1)
        with self.assertRaises(AssertionError):
            _get_interval(0)

        lx_dx = [(1, 0.1),

                 (2, 0.2),

                 (3, 0.5),
                 (4, 0.5),
                 (5, 0.5),

                 (6, 1),
                 (7, 1),
                 (8, 1),
                 (9, 1),
                 (10, 1),

                 (11, 2),
                 (12, 2),
                 (19, 2),
                 (20, 2),

                 (21, 5),
                 (22, 5),
                 (49, 5),
                 (50, 5),

                 (51, 10),
                 (52, 10),
                 (99, 10),
                 (100, 10)]
        for lx, dx in lx_dx:
            self.assertAlmostEqual(_get_interval(lx), dx)

    def test__get_lower_limit(self):
        with self.assertRaises(AssertionError):
            _get_lower_limit(0, 0)
        with self.assertRaises(AssertionError):
            _get_lower_limit(0, -1)

        self.assertAlmostEqual(_get_lower_limit(-10, 3), -12)
        self.assertAlmostEqual(_get_lower_limit(-12, 3), -15)

    def test__get_upper_limit(self):
        with self.assertRaises(AssertionError):
            _get_upper_limit(0, 0)
        with self.assertRaises(AssertionError):
            _get_upper_limit(0, -1)

        self.assertAlmostEqual(_get_upper_limit(-10, 3), -9)
        self.assertAlmostEqual(_get_upper_limit(-12, 3), -9)

    def test_get_tick_configurations(self):
        x1, x2, dx = get_tick_configurations(101.001, 103.0001)
        self.assertAlmostEqual(x1, 100.8)
        self.assertAlmostEqual(x2, 103.2)
        self.assertAlmostEqual(dx, 0.2)

        x1, x2, dx = get_tick_configurations(0, 1)
        self.assertAlmostEqual(x1, -0.1)
        self.assertAlmostEqual(x2, 1.1)
        self.assertAlmostEqual(dx, 0.1)

    def test_list_2d(self):
        self.assertEqual(list_2d(2, 3),
                         [[None, None, None],
                          [None, None, None]])

        self.assertEqual(list_2d(2, 3, 0),
                         [[0, 0, 0],
                          [0, 0, 0]])

    def test_flatten(self):
        self.assertEqual(list(flatten([])), [])
        self.assertEqual(list(flatten([1, 2])), [1, 2])
        self.assertEqual(list(flatten([1, [2, 3]])), [1, 2, 3])
        self.assertEqual(list(flatten(['ab'])), ['ab'])
        self.assertEqual(tuple(sorted(flatten((1, 2, (3, [4, set([5, 6]), 7 ], [8, 9]))))),
                         tuple(sorted((1, 2, 3, 4, 5, 6, 7, 8, 9))))

    def test_make_fixed_format_parser(self):
        with self.assertRaises(AssertionError):
            make_fixed_format_parser((('a', 0, int),))
        fixed_format_parser\
            = make_fixed_format_parser((('a', 3, int),
                                        ('b', 7, lambda x: -int(x))))
        self.assertEqual(fixed_format_parser(' 325      '),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser(' 325      \n'),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser(' 32  5    '),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser('32   5    abc'),
                         {'a': 32, 'b': -5})
        with self.assertRaises(AssertionError):
            fixed_format_parser('123456789')


if __name__ == '__main__':
    _unittest.main()
