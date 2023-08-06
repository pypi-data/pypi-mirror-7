from cadmesh cimport *


class Trap:
    def __init__(self):
        self.log = []

    def write(self, data):
        self.log.append(data)

class AdmeshError(Exception):
    pass


cdef class Stl:
    cdef stl_file _c_stl_file
    cdef bint _opened
    def __cinit__(self, path=''):
        self._opened = False
        if path:
            self.open(path)

    def open(self, path):
        """stl_open"""
        stl_open(&self._c_stl_file, path)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_open')
        self._opened = True

    def repair(self,
               fixall_flag=True,
               exact_flag=False,
               tolerance_flag=False,
               tolerance=0,
               increment_flag=False,
               increment=0,
               nearby_flag=False,
               iterations=2,
               remove_unconnected_flag=False,
               fill_holes_flag=False,
               normal_directions_flag=False,
               normal_values_flag=False,
               reverse_all_flag=False,
               verbose_flag=True):
        """stl_repair"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_repair(&self._c_stl_file,
                   fixall_flag,
                   exact_flag,
                   tolerance_flag,
                   tolerance,
                   increment_flag,
                   increment,
                   nearby_flag,
                   iterations,
                   remove_unconnected_flag,
                   fill_holes_flag,
                   normal_directions_flag,
                   normal_values_flag,
                   reverse_all_flag,
                   verbose_flag)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_repair')


    def __dealloc__(self):
        if self._opened:
            stl_close(&self._c_stl_file)

    def write_ascii(self, file, label='admesh'):
        """stl_write_ascii"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_ascii(&self._c_stl_file, file, label)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_ascii')

    def write_binary(self, file, label='admesh'):
        """stl_write_binary"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_binary(&self._c_stl_file, file, label)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_binary')

    def check_facets_exact(self):
        """stl_check_facets_exact"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_check_facets_exact(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_check_facets_exact')

    def check_facets_nearby(self, tolerance):
        """stl_check_facets_nearby"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_check_facets_nearby(&self._c_stl_file, tolerance)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_check_facets_nearby')

    def remove_unconnected_facets(self):
        """stl_remove_unconnected_facets"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_remove_unconnected_facets(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_remove_unconnected_facets')

    def write_vertex(self, facet, vertex):
        """stl_write_vertex"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_vertex(&self._c_stl_file, facet, vertex)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_vertex')

    def write_facet(self, facet, label='admesh'):
        """stl_write_facet"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_facet(&self._c_stl_file, label, facet)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_facet')

    def write_edge(self, edge, label='admesh'):
        """stl_write_edge"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_edge(&self._c_stl_file, label, edge)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_edge')

    def write_neighbor(self, facet):
        """stl_write_neighbor"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_neighbor(&self._c_stl_file, facet)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_neighbor')

    def write_quad_object(self, file):
        """stl_write_quad_object"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_quad_object(&self._c_stl_file, file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_quad_object')

    def verify_neighbors(self):
        """stl_verify_neighbors"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_verify_neighbors(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_verify_neighbors')

    def fill_holes(self):
        """stl_fill_holes"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_fill_holes(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_fill_holes')

    def fix_normal_directions(self):
        """stl_fix_normal_directions"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_fix_normal_directions(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_fix_normal_directions')

    def fix_normal_values(self):
        """stl_fix_normal_values"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_fix_normal_values(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_fix_normal_values')

    def reverse_all_facets(self):
        """stl_reverse_all_facets"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_reverse_all_facets(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_reverse_all_facets')

    def translate(self, x, y, z):
        """stl_translate"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_translate(&self._c_stl_file, x, y, z)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_translate')

    def translate_relative(self, x, y, z):
        """stl_translate_relative"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_translate_relative(&self._c_stl_file, x, y, z)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_translate_relative')

    def scale(self, factor):
        """stl_scale"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_scale(&self._c_stl_file, factor)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_scale')

    def rotate_x(self, angle):
        """stl_rotate_x"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_rotate_x(&self._c_stl_file, angle)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_rotate_x')

    def rotate_y(self, angle):
        """stl_rotate_y"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_rotate_y(&self._c_stl_file, angle)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_rotate_y')

    def rotate_z(self, angle):
        """stl_rotate_z"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_rotate_z(&self._c_stl_file, angle)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_rotate_z')

    def mirror_xy(self):
        """stl_mirror_xy"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_mirror_xy(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_mirror_xy')

    def mirror_yz(self):
        """stl_mirror_yz"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_mirror_yz(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_mirror_yz')

    def mirror_xz(self):
        """stl_mirror_xz"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_mirror_xz(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_mirror_xz')

    def open_merge(self, file):
        """stl_open_merge"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_open_merge(&self._c_stl_file, file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_open_merge')

    def invalidate_shared_vertices(self):
        """stl_invalidate_shared_vertices"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_invalidate_shared_vertices(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_invalidate_shared_vertices')

    def generate_shared_vertices(self):
        """stl_generate_shared_vertices"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_generate_shared_vertices(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_generate_shared_vertices')

    def write_obj(self, file):
        """stl_write_obj"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_obj(&self._c_stl_file, file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_obj')

    def write_off(self, file):
        """stl_write_off"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_off(&self._c_stl_file, file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_off')

    def write_dxf(self, file, label='admesh'):
        """stl_write_dxf"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_dxf(&self._c_stl_file, file, label)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_dxf')

    def write_vrml(self, file):
        """stl_write_vrml"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_write_vrml(&self._c_stl_file, file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_write_vrml')

    def calculate_volume(self):
        """stl_calculate_volume"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_calculate_volume(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_calculate_volume')

    def initialize(self):
        """stl_initialize"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_initialize(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_initialize')

    def read(self, first_facet, first):
        """stl_read"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_read(&self._c_stl_file, first_facet, first)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_read')

    def facet_stats(self, facet, first):
        """stl_facet_stats"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_facet_stats(&self._c_stl_file, facet, first)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_facet_stats')

    def get_size(self):
        """stl_get_size"""
        if not self._opened:
            raise AdmeshError('STL not opened')
        stl_get_size(&self._c_stl_file)
        if stl_get_error(&self._c_stl_file):
            stl_clear_error(&self._c_stl_file)
            raise AdmeshError('stl_get_size')


