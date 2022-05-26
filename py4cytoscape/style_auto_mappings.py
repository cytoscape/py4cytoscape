# -*- coding: utf-8 -*-

"""Functions for defining automatic MAPPINGS between table column values and visual properties, organized into sections:

I. Palettes for color mapping generators
II. Schemes for discrete and numerical mapping generators
III. Functions for automatically mapping discrete values to colors, opacities, sizes, heights, widths and shapes

See style_mappings for manual mapping generation
"""

"""Copyright 2020-2022 The Cytoscape Consortium

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# External library imports
import colorbrewer
import random
import numpy as np
import functools


# Internal module imports
from . import styles
from . import tables

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


# ==============================================================================
# I. Palettes for color mapping generators
# ------------------------------------------------------------------------------

# Decorator that turns a palette lambda into a triple (palette function name, palette type, lambda)
def _palette(palette_type):
    def decorator_palette(func):
        @functools.wraps(func)
        def palette_def(*args, **kwargs):
            return (func.__name__, palette_type, func(*args, **kwargs))
        return palette_def
    return decorator_palette

# Decorator that turns a scheme lambda into a triple (scheme function name, scheme type, lambda)
def _scheme(scheme_type):
    def decorator_scheme(func):
        @functools.wraps(func)
        def scheme_def(*args, **kwargs):
            return (func.__name__, scheme_type, func(*args, **kwargs))
        return scheme_def
    return decorator_scheme


# Brewer palettes taken from https://github.com/dsc/colorbrewer-python/blob/master/colorbrewer.py

@_palette('qualitative')
def palette_color_random():
    """Generate random color map of a given size

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of random colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    MAX_COLOR = 256 * 256 * 256
    return lambda value_count: [f'#{random.randint(0, MAX_COLOR):06X}'   for i in range(value_count)]

@_palette('qualitative')
def palette_color_brewer_q_Pastel2(reverse=False):
    """Generate pastel2 Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Pastel2, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Pastel1(reverse=False):
    """Generate pastel1 Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Pastel1, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Dark2(reverse=False):
    """Generate pastel2 Dark2 palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Dark2, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Accent(reverse=False):
    """Generate accent Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Accent, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Paired(reverse=False):
    """Generate paired Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Paired, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Set1(reverse=False):
    """Generate set1 Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Set1, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Set2(reverse=False):
    """Generate set2 Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Set2, reverse)

@_palette('qualitative')
def palette_color_brewer_q_Set3(reverse=False):
    """Generate set3 Brewer palette of a given size ... interpolate as needed ... best for discrete mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Set3, reverse)

@_palette('sequential')
def palette_color_brewer_s_YlGn(reverse=False):
    """Generate YlGn Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.YlGn, reverse)

@_palette('sequential')
def palette_color_brewer_s_YlGnBu(reverse=False):
    """Generate YlGnBu Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.YlGnBu, reverse)

@_palette('sequential')
def palette_color_brewer_s_GnBu(reverse=False):
    """Generate GnBu Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.GnBu, reverse)

@_palette('sequential')
def palette_color_brewer_s_BuGn(reverse=False):
    """Generate BuGn Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.BuGn, reverse)

@_palette('sequential')
def palette_color_brewer_s_PuBuGn(reverse=False):
    """Generate PuBuGn Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.PuBuGn, reverse)

@_palette('sequential')
def palette_color_brewer_s_PuBu(reverse=False):
    """Generate PuBu Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.PuBu, reverse)

@_palette('sequential')
def palette_color_brewer_s_BuPu(reverse=False):
    """Generate BuPu Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.BuPu, reverse)

@_palette('sequential')
def palette_color_brewer_s_RdPu(reverse=False):
    """Generate RdPu Brewer palette of a given size ... interpolate as needed ... best for one-tailed continuous

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.RdPu, reverse)

@_palette('sequential')
def palette_color_brewer_s_PuRd(reverse=False):
    """Generate PuRd Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.PuRd, reverse)

@_palette('sequential')
def palette_color_brewer_s_OrRd(reverse=False):
    """Generate OrRd Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.OrRd, reverse)

@_palette('sequential')
def palette_color_brewer_s_YlOrRd(reverse=False):
    """Generate YlOrRd Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.YlOrRd, reverse)

@_palette('sequential')
def palette_color_brewer_s_YlOrBr(reverse=False):
    """Generate YlOrBr Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.YlOrBr, reverse)

@_palette('sequential')
def palette_color_brewer_s_Purples(reverse=False):
    """Generate Purples Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Purples, reverse)

@_palette('sequential')
def palette_color_brewer_s_Blues(reverse=False):
    """Generate Blues Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Blues, reverse)

@_palette('sequential')
def palette_color_brewer_s_Greens(reverse=False):
    """Generate Greens Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Greens, reverse)

@_palette('sequential')
def palette_color_brewer_s_Oranges(reverse=False):
    """Generate Oranges Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Oranges, reverse)

@_palette('sequential')
def palette_color_brewer_s_Reds(reverse=False):
    """Generate Reds Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Reds, reverse)

@_palette('sequential')
def palette_color_brewer_s_Greys(reverse=False):
    """Generate Greys Brewer palette of a given size ... best for one-tailed continuous mapping

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Greys, reverse)

@_palette('divergent')
def palette_color_brewer_d_PuOr(reverse=False):
    """Generate PuOr Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.PuOr, not reverse)

@_palette('divergent')
def palette_color_brewer_d_BrBG(reverse=False):
    """Generate BrBG Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.BrBG, not reverse)

@_palette('divergent')
def palette_color_brewer_d_PRGn(reverse=False):
    """Generate PRGn Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.PRGn, not reverse)

@_palette('divergent')
def palette_color_brewer_d_PiYG(reverse=False):
    """Generate PiYG Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.PiYG, not reverse)

@_palette('divergent')
def palette_color_brewer_d_RdBu(reverse=False):
    """Generate RdBu Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.RdBu, not reverse)

@_palette('divergent')
def palette_color_brewer_d_RdGy(reverse=False):
    """Generate RdGy Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.RdGy, not reverse)

@_palette('divergent')
def palette_color_brewer_d_RdYlBu(reverse=False):
    """Generate RdYlBu Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.RdYlBu, not reverse)

@_palette('divergent')
def palette_color_brewer_d_Spectral(reverse=False):
    """Generate Spectral Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.Spectral, not reverse)

@_palette('divergent')
def palette_color_brewer_d_RdYlGn(reverse=False):
    """Generate RdYlGn Brewer palette of a given size ... best for two-tailed continuous mapping

    Note that this palette is reversed as compared to the standard Brewer Color palette. This
    enables negative attribute values to skew toward not-red and positive attribute values to skew toward red,
    as is customary in biology. To use the standard Brewer Color palette instead, pass reverse=True.

    Args:
        reverse: order the colors backward as compared to standard Brewer palette

    Returns:
        lambda: generates a list of colors

    See Also:
        :meth:`gen_node_color_map`, :meth:`gen_edge_color_map`
    """
    return lambda value_count: _palette_color_brewer(value_count, colorbrewer.RdYlGn, not reverse)


# ==============================================================================
# II. Schemes for discrete and numerical mapping generators
# ------------------------------------------------------------------------------

@_scheme('discrete')
def scheme_d_shapes():
    """Generate list of node shapes of a given size

    Returns:
        lambda: generates a list of shapes

    Raises:
        CyError: if more shapes are requested than exist

    See Also:
        :meth:`gen_node_shape_map`
    """
    return lambda value_count: _scheme_d_shapes(value_count, styles.get_node_shapes(), 'shapes')

@_scheme('discrete')
def scheme_d_line_styles():
    """Generate list of line styles of a given size

    Returns:
        lambda: generates a list of line styles

    Raises:
        CyError: if more line styles are requested than exist

    See Also:
        :meth:`gen_edge_line_style_map`
    """
    return lambda value_count: _scheme_d_shapes(value_count, styles.get_line_styles(), 'line styles')

@_scheme('discrete')
def scheme_d_arrow_shapes():
    """Generate list of arrow shapes of a given size

    Returns:
        lambda: generates a list of arrow shapes

    Raises:
        CyError: if more arrow shapes are requested than exist

    See Also:
        :meth:`gen_edge_arrow_map`
    """
    return lambda value_count: _scheme_d_shapes(value_count, styles.get_arrow_shapes(), 'arrow shapes')

@_scheme('discrete')
def scheme_d_number_random(min_value=0, max_value=255):
    """Generate list of random integers in a given range

    Args:
        min_value (int): Minimum random integer to return
        max_value (int): Maximum random integer to return

    Returns:
        lambda: generates a list of random integers

    See Also:
        :meth:`gen_node_height_map`, :meth:`gen_node_opacity_map`, :meth:`gen_node_size_map`, :meth:`gen_node_width_map`, :meth:`gen_edge_opacity_map`, :meth:`gen_edge_size_map`, :meth:`gen_edge_width_map`
    """
    return lambda value_count: [random.randint(min_value, max_value)   for i in range(value_count)]

@_scheme('discrete')
def scheme_d_number_series(start_value=0, step=10):
    """Generate list of numbers in a given series

    Args:
        start_value (int or float): First number to return
        step (int or float): Increment between numbers in series

    Returns:
        lambda: generates a list of numbers in the series

    See Also:
        :meth:`gen_node_height_map`, :meth:`gen_node_opacity_map`, :meth:`gen_node_size_map`, :meth:`gen_node_width_map`, :meth:`gen_edge_opacity_map`, :meth:`gen_edge_size_map`, :meth:`gen_edge_width_map`
    """
    return lambda value_count: [start_value + i * step    for i in range(value_count)]


@_scheme('continuous')
def scheme_c_number_continuous(start_value=10, end_value=30):
    """Generate a continuous series

    Args:
        start_value (int or float): First number in continuum
        end_value (int or float): Last number in continuum

    Returns:
        lambda: generates a descriptor for a continuous mapping

    See Also:
        :meth:`gen_node_height_map`, :meth:`gen_node_opacity_map`, :meth:`gen_node_size_map`, :meth:`gen_node_width_map`, :meth:`gen_edge_opacity_map`, :meth:`gen_edge_size_map`, :meth:`gen_edge_width_map`
    """
    return lambda min_data, max_data: [start_value, start_value + (end_value - start_value) / 2, end_value]

# ==============================================================================
# III.a Mapping generators for colors
# ------------------------------------------------------------------------------

@cy_log
def gen_node_color_map(table_column,
                       palette = {'d': palette_color_brewer_q_Set2(),
                                  'c': (palette_color_brewer_s_GnBu(), palette_color_brewer_d_RdYlBu())},
                       mapping_type='c',
                       default_color=None,
                       style_name=None,
                       network=None,
                       base_url=DEFAULT_BASE_URL):
    """Generate color map parameters for discrete or continuous values in a node table

    A basic palette is a tuple containing the palette function name, palette type, and a lambda resolving
    to an actual Brewer palette. There are a few ways a palette can be encoded in the ``palette`` parameter. The most
    generic is a dictionary that identifies which basic palette to use if the ``mapping_type`` is discrete or
    continuous. Or the basic palette can be provided directly (without being in a dict). Either way,
    For discrete mappings, the basic palette that should be qualitative. For continuous mappings, either one or two basic
    palettes can be provided. If only one, that basic palette will be used whether the Cytoscape column data turns
    out to be 1-tailed or 2-tailed. If two basic palettes are provided, the second will be used if the Cytoscape column
    data turns out to be 2-tailed. Basic palettes for 1-tailed data should be sequential palettes, and for 2-tailed data
    should be divergent palettes.

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        palette (dict or tuple): Descriptor for functions that return a color list of a given length
        mapping_type (str): continuous or discrete (c, d); default is continuous
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a color style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or continuous mapping attempted on non-numeric values
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_node_color_map('newcol', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['3'], 'colors': ['#66C2A5'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d', default_color='#00FF00', style_name='galFiltered Style', network='galFiltered.sif')
        {'table_column': 'newcol', 'table_column_values': ['3'], 'colors': ['#7FC97F'], 'mapping_type': 'd', 'default_color': '#00FF00', 'style_name': 'galFiltered Style', 'network': 'galFiltered.sif', 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_color_map('newcol', style_name='galFiltered Style')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E0F3DB', '#A8DDB5', '#43A2CA'], 'mapping_type': 'c', 'default_color': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_node_border_color_mapping`, :meth:`set_node_color_mapping`, :meth:`set_node_label_color_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_color_map('node', table_column, palette, mapping_type, default_color, style_name, network, base_url)

@cy_log
def gen_edge_color_map(table_column,
                       palette = {'d': palette_color_brewer_q_Set2(),
                                  'c': (palette_color_brewer_s_GnBu(), palette_color_brewer_d_RdYlBu())},
                       mapping_type='c',
                       default_color=None,
                       style_name=None,
                       network=None,
                       base_url=DEFAULT_BASE_URL):
    """Generate color map parameters for discrete or continuous values in an edge table

    A basic palette is a tuple containing the palette function name, palette type, and a lambda resolving
    to an actual Brewer palette. There are a few ways a palette can be encoded in the ``palette`` parameter. The most
    generic is a dictionary that identifies which basic palette to use if the ``mapping_type`` is discrete or
    continuous. Or the basic palette can be provided directly (without being in a dict). Either way,
    For discrete mappings, the basic palette that should be qualitative. For continuous mappings, either one or two basic
    palettes can be provided. If only one, that basic palette will be used whether the Cytoscape column data turns
    out to be 1-tailed or 2-tailed. If two basic palettes are provided, the second will be used if the Cytoscape column
    data turns out to be 2-tailed. Basic palettes for 1-tailed data should be sequential palettes, and for 2-tailed data
    should be divergent palettes.

    Args:
        table_column (str): Name of Cytoscape edge table column to map values from
        palette (dict or tuple): Descriptor for functions that return a color list of a given length
        mapping_type (str): continuous or discrete (c, d); default is continuous
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a color style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or continuous mapping attempted on non-numeric values
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_edge_color_map('interaction', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'colors': ['#66C2A5', '#FC8D62'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'colors': ['#7FC97F', '#BEAED4'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_color_map('EdgeBetweenness')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'colors': ['#E0F3DB', '#A8DDB5', '#43A2CA'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues())
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'colors': ['#DEEBF7', '#9ECAE1', '#3182BD'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_color_map('EdgeBetweenness', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'colors': ['#DEEBF7', '#9ECAE1', '#3182BD'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_edge_color_mapping`, :meth:`set_edge_label_color_mapping`, :meth:`set_edge_source_arrow_color_mapping`, :meth:`set_edge_target_arrow_color_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_color_map('edge', table_column, palette, mapping_type, default_color, style_name, network, base_url)

# ==============================================================================
# III.b Mapping generators for opacities
# ------------------------------------------------------------------------------

@cy_log
def gen_node_opacity_map(table_column,
                         number_scheme={'d': scheme_d_number_series(),
                                        'c': scheme_c_number_continuous()},
                         mapping_type='c',
                         default_number=None,
                         style_name=None,
                         network=None,
                         base_url=DEFAULT_BASE_URL):
    """Generate opacity map parameters for discrete or continuous values in a node table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        number_scheme (dict or func): Descriptor for functions that return an opacity list of a given length
        mapping_type (str): continuous or discrete (c, d); default is continuous
        default_number (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a opacity style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_node_opacity_map('newcol', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'opacities': [0, 10, 20], 'mapping_type': 'd', 'default_opacity': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_opacity_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'opacities': [100, 120, 140], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_opacity_map('newcol')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'opacities': [10, 20.0, 30], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_opacity_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'opacities': [100, 150.0, 200], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_node_border_opacity_mapping`, :meth:`set_node_fill_opacity_mapping`, :meth:`set_node_label_opacity_mapping`, :meth:`set_node_combo_opacity_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('node', table_column, number_scheme, mapping_type, 'opacities', 'default_opacity', default_number, style_name, network, base_url)

@cy_log
def gen_edge_opacity_map(table_column,
                         number_scheme={'d': scheme_d_number_series(),
                                        'c': scheme_c_number_continuous()},
                         mapping_type='c',
                         default_number=None,
                         style_name=None,
                         network=None,
                         base_url=DEFAULT_BASE_URL):
    """Generate opacity map parameters for discrete or continuous values in an edge table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape edge table column to map values from
        number_scheme (dict or func): Descriptor for functions that return an opacity list of a given length
        default_number (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a opacity style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_edge_opacity_map('interaction', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'opacities': [0, 10], 'mapping_type': 'd', 'default_opacity': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_opacity_map('interaction', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'opacities': [100, 120], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_opacity_map('EdgeBetweenness')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'opacities': [10, 20.0, 30], 'mapping_type': 'c', 'default_opacity': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_opacity_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'opacities': [100, 150.0, 200], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_edge_label_opacity_mapping`, :meth:`set_edge_opacity_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('edge', table_column, number_scheme, mapping_type, 'opacities', 'default_opacity', default_number, style_name, network, base_url)

# ==============================================================================
# III.c Mapping generators for widths
# ------------------------------------------------------------------------------

@cy_log
def gen_node_width_map(table_column,
                       number_scheme={'d': scheme_d_number_series(),
                                      'c': scheme_c_number_continuous()},
                       mapping_type='c',
                       default_number=None,
                       style_name=None,
                       network=None,
                       base_url=DEFAULT_BASE_URL):
    """Generate width map parameters for discrete or continuous values in a node table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        number_scheme (dict or func): Descriptor for functions that return a width list of a given length
        default_number (int): width value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a width style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_node_width_map('newcol', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'widths': [0, 10, 20], 'mapping_type': 'd', 'default_width': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_width_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'widths': [100, 120, 140], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_width_map('newcol')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'widths': [10, 20.0, 30], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_width_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'widths': [100, 150.0, 200], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_node_border_width_mapping`, :meth:`set_node_width_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('node', table_column, number_scheme, mapping_type, 'widths', 'default_width', default_number, style_name, network, base_url)

@cy_log
def gen_edge_width_map(table_column,
                       number_scheme={'d': scheme_d_number_series(),
                                      'c': scheme_c_number_continuous()},
                       mapping_type='c',
                       default_number=None,
                       style_name=None,
                       network=None,
                       base_url=DEFAULT_BASE_URL):
    """Generate width map parameters for discrete or continuous values in an edge table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape edge table column to map values from
        number_scheme (dict or func): Descriptor for functions that return an width list of a given length
        mapping_type (str): continuous or discrete (c, d); default is continuous
        default_number (int): width value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a width style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_edge_width_map('interaction', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'widths': [0, 10], 'mapping_type': 'd', 'default_width': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_width_map('interaction', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'widths': [100, 120], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_width_map('EdgeBetweenness')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'widths': [10, 20.0, 30], 'mapping_type': 'c', 'default_width': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_width_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'widths': [100, 150.0, 200], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_edge_line_width_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('edge', table_column, number_scheme, mapping_type, 'widths', 'default_width', default_number, style_name, network, base_url)

# ==============================================================================
# III.d Mapping generators for heights
# ------------------------------------------------------------------------------

@cy_log
def gen_node_height_map(table_column,
                        number_scheme={'d': scheme_d_number_series(),
                                       'c': scheme_c_number_continuous()},
                        mapping_type='c',
                        default_number=None,
                        style_name=None,
                        network=None,
                        base_url=DEFAULT_BASE_URL):
    """Generate height map parameters for discrete or continuous values in a node table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        number_scheme (dict or func): Descriptor for functions that return a height list of a given length
        mapping_type (str): continuous or discrete (c, d); default is continuous
        default_number (int): height value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a height style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_node_height_map('newcol', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'heights': [0, 10, 20], 'mapping_type': 'd', 'default_height': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_height_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'heights': [100, 120, 140], 'mapping_type': 'd', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_height_map('newcol')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'heights': [10, 20.0, 30], 'mapping_type': 'c', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_height_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'heights': [100, 150.0, 200], 'mapping_type': 'c', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_node_height_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('node', table_column, number_scheme, mapping_type, 'heights', 'default_height', default_number, style_name, network, base_url)

# ==============================================================================
# III.e Mapping generators for sizes
# ------------------------------------------------------------------------------

@cy_log
def gen_node_size_map(table_column,
                      number_scheme={'d': scheme_d_number_series(),
                                     'c': scheme_c_number_continuous()},
                      mapping_type='c',
                      default_number=None,
                      style_name=None,
                      network=None,
                      base_url=DEFAULT_BASE_URL):
    """Generate size map parameters for discrete or continuous values in a node table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        number_scheme (dict or func): Descriptor for functions that return a size list of a given length
        mapping_type (str): continuous or discrete (c, d); default is continuous
        default_number (int): size value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a size style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_node_sizes_map('newcol', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'sizes': [0, 10, 20], 'mapping_type': 'd', 'default_size': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_sizes_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '6'], 'sizes': [100, 120, 140], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_sizes_map('newcol')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'sizes': [10, 20.0, 30], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_node_sizes_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'sizes': [100, 150.0, 200], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_node_font_size_mapping`, :meth:`set_node_size_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('node', table_column, number_scheme, mapping_type, 'sizes', 'default_size', default_number, style_name, network, base_url)

@cy_log
def gen_edge_size_map(table_column,
                      number_scheme={'d': scheme_d_number_series(),
                                     'c': scheme_c_number_continuous()},
                      mapping_type='c',
                      default_number=None,
                      style_name=None,
                      network=None,
                      base_url=DEFAULT_BASE_URL):
    """Generate size map parameters for discrete or continuous values in an edge table

    A basic scheme is a tuple containing the scheme function name, scheme type, and a lambda resolving to a function
    that provides map-to values. There are a few ways a scheme can be encoded in the ``number_scheme`` parameter. The most
    generic is a dictionary that identifies which basic scheme to use if the ``mapping_type`` is discrete or
    continuous. Or the basic scheme can be provided directly (without being in a dict). Either way,
    for discrete mappings, the basic scheme that should be discrete. For continuous mappings, the basic
    scheme should be continuous.

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        number_scheme (dict or func): Descriptor for functions that return a size list of a given length
        default_number (int): size value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a size style_mappings setter function

    Raises:
        CyError: if network doesn't exist, or mapping_type is unsupported, or number_scheme doesn't match mapping_type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_edge_size_map('interaction', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'sizes': [0, 10], 'mapping_type': 'd', 'default_size': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_size_map('interaction', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'sizes': [100, 120], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_size_map('EdgeBetweenness')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'sizes': [10, 20.0, 30], 'mapping_type': 'c', 'default_size': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}
        >>> gen_edge_size_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'sizes': [100, 150.0, 200], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_node_font_size_mapping`, :meth:`set_node_size_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_map('edge', table_column, number_scheme, mapping_type, 'sizes', 'default_size', default_number, style_name, network, base_url)

# ==============================================================================
# III.f Mapping generators for shapes
# ------------------------------------------------------------------------------

@cy_log
def gen_node_shape_map(table_column,
                       default_shape=None,
                       style_name=None,
                       network=None,
                       base_url=DEFAULT_BASE_URL):
    """Generate shape map parameters for discrete values in a node table

    Args:
        table_column (str): Name of Cytoscape node table column to map values from
        default_shape (str): shape name to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a shape style_mappings setter function

    Raises:
        CyError: if network doesn't exist or if the number of discrete values exceed the number of available shapes
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_node_shape_map('newcol', style_name='galFiltered Style')
        {'table_column': 'newcol', 'table_column_values': ['8', '7', '1'], 'shapes': ['VEE', 'OCTAGON', 'HEXAGON'], 'default_shape': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

    See Also:
        :meth:`set_node_shape_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_d_shape_map('node', table_column, scheme_d_shapes(), 'shapes', 'default_shape', default_shape, style_name, network, base_url)


@cy_log
def gen_edge_line_style_map(table_column,
                            default_line_style='SOLID',
                            style_name=None,
                            network=None,
                            base_url=DEFAULT_BASE_URL):
    """Generate line style map parameters for discrete values in an edge table

    Args:
        table_column (str): Name of Cytoscape edge table column to map values from
        default_line_style (str): line style name to set as default for all unmapped values (default is SOLID)
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to a line style style_mappings setter function

    Raises:
        CyError: if network doesn't exist or if the number of discrete values exceed the number of available line styles
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_edge_line_style_map('interaction', style_name='galFiltered Style')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'line_styles': ['PARALLEL_LINES', 'SINEWAVE'], 'default_line_style': 'SOLID', 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_edge_line_style_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _gen_d_shape_map('edge', table_column, scheme_d_line_styles(), 'line_styles', 'default_line_style', default_line_style, style_name, network, base_url)

@cy_log
def gen_edge_arrow_map(table_column,
                       default_shape='ARROW',
                       style_name=None,
                       network=None,
                       base_url=DEFAULT_BASE_URL):
    """Generate arrow shape map parameters for discrete values in an edge table

    Args:
        table_column (str): Name of Cytoscape edge table column to map values from
        default_shape (str): arrow shape name to set as default for all unmapped values (default is ARROW)
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Collection of parameter values suitable for passing to an arrow style_mappings setter function

    Raises:
        CyError: if network doesn't exist or if the number of discrete values exceed the number of available arrow styles
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> gen_edge_arrow_map('interaction', style_name='galFiltered Style')
        {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'shapes': ['ARROW', 'T'], 'default_shape': 'ARROW', 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'}

    See Also:
        :meth:`set_edge_source_arrow_shape_mapping`, :meth:`set_edge_target_arrow_shape_mapping`
    """
    return _gen_d_shape_map('edge', table_column, scheme_d_arrow_shapes(), 'shapes', 'default_shape', default_shape, style_name, network, base_url)

# Generate a brewer palette of a given size, and interpolate if there isn't a palette of the desired size
def _palette_color_brewer(value_count, palette, reverse):
    # Get the list of palette lengths available for this palette
    # A palette is a list of color lists tuned for the number of colors needed. For example,
    # palette A may have 3:[color1, color2, color3] and 4:[color1, color2, color3, color4]. If
    # value_count isn't supported in the palette, we interpolate as best we can.
    palette_lengths = sorted(palette.keys())
    longest_palette = palette_lengths[-1]
    if value_count <= longest_palette:
        # We have the palette for this list of values already, except that if there are too few values,
        # we take the colors from the smallest palette and call it a day
        candidate_palette = palette[max(value_count, palette_lengths[0])][0:value_count]
        if reverse: candidate_palette.reverse()
    else:
        # There are more values than the largest palette, so interpolate by using the largest palette. To get
        # m colors out of a p colored palette, suppose that the palette colors are in a series of points along a line.
        # For each data value, march a fixed distance down the line ... whatever that distance is, mix the two
        # closest colors in proportion to their proximity.
        #
        # Get the longest palette and the fixed distance, then initialize the interpolated palette
        max_palette = palette[longest_palette]
        if reverse: max_palette.reverse()
        per_color_increment = float(len(max_palette) - 1) / (value_count - 1)
        candidate_palette = list(' ' * value_count)

        # March through the original palette and mix colors to create interpolated palette
        for entry in range(value_count):
            # Find the next point on the palette line
            real_index = entry * per_color_increment

            # Find the palette entry immediately before and after it, and calculate the proportion each contributes
            low_index = int(real_index)
            high_index = min(int(real_index + 1), len(max_palette) - 1)
            high_color_percent = real_index - low_index

            # Get the previous and next colors as (red, green, blue) tuples
            low_color_bound = max_palette[low_index]
            high_color_bound = max_palette[high_index]

            # Mix the two colors in proportion to their distance from current point, and return as tuple
            candidate_palette[entry] = tuple(int(l * (1 - high_color_percent) + h * high_color_percent + 0.5)  for l,h in zip(low_color_bound, high_color_bound))

    # Convert list of color tuples into list of hex values
    return [f'#{c[0]:02X}{c[1]:02X}{c[2]:02X}'  for c in candidate_palette]

# Given a list of shapes, trim the list to a desired size
def _scheme_d_shapes(value_count, shapes, shape_name):
    if value_count > len(shapes):
        raise CyError(f'Attempt to return {value_count} {shape_name}, but there are only {len(shapes)} {shape_name}')
    shapes.sort()
    return shapes[0:value_count]

# Find the unique values in a column, map them to a desired target set, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _gen_color_map(table,
                   table_column,
                   palette,
                   mapping_type,
                   default_value,
                   style_name,
                   network,
                   base_url):

    mapping_type = normalize_mapping(mapping_type, 'color palette', ['d', 'c'])

    if isinstance(palette, dict):
        if mapping_type in palette:
            palette = palette[mapping_type]
        else:
            raise CyError(f'Palette dictionary does not contain entry for "{mapping_type}" mapping')

    if mapping_type == 'd':
        return _gen_d_color_map(table, table_column, palette, default_value, style_name, network, base_url)
    else:
        return _gen_c_color_map(table, table_column, palette, default_value, style_name, network, base_url)


# Find the unique values in a column, map them to a desired target set, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _gen_d_color_map(table,
                     table_column,
                     palette,
                     default_value,
                     style_name,
                     network,
                     base_url):
    # Check palette and map values to colors
    palette_func_name = palette[0]
    palette_type = palette[1]
    palette_func = palette[2]

    if 'qualitative' not in palette_type:
        narrate(f'Warning: {palette_func_name} is not a qualitative palette and may give poor results for a discrete mapping.')

    return _map_values(table, table_column, palette_func, 'colors', 'default_color', default_value, style_name, network, base_url)

# Find the min/max values in a column, create a palette mapping, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _gen_c_color_map(table,
                     table_column,
                     palette,
                     default_value,
                     style_name,
                     network,
                     base_url):
    # Find out all of the values in the named column
    df_values = tables.get_table_columns(table=table, columns=table_column, network=network, base_url=base_url)

    # Start out with using preferred palette (for continuous, there could be a one-tailed or two-tailed scheme)
    palette_to_use = palette[0] if type(palette[0]) is tuple else palette

    # For continuous, one tailed means all negative or all positive ... otherwise two-tailed with 0 in between
    max_data = df_values[table_column].max()
    min_data = df_values[table_column].min()
    if type(max_data) in [int, float]:
        if np.isnan(max_data):
            min_data = 0
            max_data = 1
        if np.sign(min_data) == np.sign(max_data):
            # One-tailed mapping ... btw: prefer sequential palette if color mapping
            mid_data = min_data + (max_data - min_data) / 2
            src_values = [min_data, mid_data, max_data]
            best_palette = 'sequential'
            map_type = 'one-tailed'
        else:
            # Two-tailed mapping ... btw: prefer divergent palette if color mapping
            max_max_data = max(abs(min_data), abs(max_data))
            src_values = [-max_max_data, 0, max_max_data]
            if type(palette[0]) is tuple and len(palette) >= 2:
                palette_to_use = palette[1]
            best_palette = 'divergent'
            map_type = 'two-tailed'
    else:
        raise CyError(f'Cannot perform continuous mapping on column "{table_column}", which is not numeric')

    # Check palette and map values to colors
    palette_func_name = palette_to_use[0]
    palette_type = palette_to_use[1]
    palette_func = palette_to_use[2]

    if best_palette not in palette_type:
        narrate(f'Warning: {palette_func_name} is not a {best_palette} palette and may give poor results for a {map_type} continuous mapping.')
    dst_values = palette_func(len(src_values))

    return {'table_column': table_column, 'table_column_values': src_values, 'colors': dst_values,
            'mapping_type': 'c', 'default_color': default_value, 'style_name': style_name,
            'network': network, 'base_url': base_url}

# Find the unique values in a column, map them to a desired target set, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _gen_map(table,
             table_column,
             scheme,
             mapping_type,
             value_name,
             default_name,
             default_value,
             style_name,
             network,
             base_url):

    mapping_type = normalize_mapping(mapping_type, 'color palette', ['d', 'c'])

    if isinstance(scheme, dict):
        if mapping_type in scheme:
            scheme = scheme[mapping_type]
        else:
            raise CyError(f'Scheme dictionary does not contain entry for "{mapping_type}" mapping')

    if mapping_type == 'd':
        return _gen_d_map(table, table_column, scheme, value_name, default_name, default_value, style_name, network, base_url)
    else:
        return _gen_c_map(table, table_column, scheme, value_name, default_name, default_value, style_name, network, base_url)


# Find the unique values in a column, map them to a desired target set, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _gen_d_map(table,
               table_column,
               scheme,
               value_name,
               default_name,
               default_value,
               style_name,
               network,
               base_url):

    # Check scheme and map values
    scheme_func_name = scheme[0]
    scheme_type = scheme[1]
    scheme_func = scheme[2]

    if 'discrete' not in scheme_type:
        raise CyError(f'Scheme {scheme_func_name} cannot be used for discrete mappings')

    return _map_values(table, table_column, scheme_func, value_name, default_name, default_value, style_name, network, base_url)


# Find the unique values in a column, map them to a desired target set, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _map_values(table, table_column, scheme_func, value_name, default_name, default_value, style_name, network, base_url):

    # Find out all of the values in the named column
    df_values = tables.get_table_columns(table=table, columns=table_column, network=network, base_url=base_url)

    # Find the frequency distribution, with most common elements first (... not same ordering as Cytoscape) ... guarantee the order by sorting
    df_freq = df_values[table_column].value_counts()
    if len(df_freq) > 1:
        # df_values rows aren't left in a predictable order, so that means the color assignments will vary from
        # run to run. To make this consistent and testable, we sort all values within the same frequency count.
        # To do this, we turn the frequency series into a dataframe then sort first on frequency count and then
        # on value.
        df_freq = df_freq.to_frame().rename_axis('index').sort_values(by=[table_column, 'index'], ascending=[True, True])

    # Create the mapped values that correspond to the unique elements
    src_values = [str(i)   for i in df_freq.index]

    dst_values = scheme_func(len(src_values))
    return {'table_column': table_column, 'table_column_values': src_values, value_name: dst_values,
            'mapping_type': 'd', default_name: default_value, 'style_name': style_name,
            'network': network, 'base_url': base_url}


# Find the unique values in a column, map them to a desired target set, and return a dictionary of parameter values
# suitable for passing to style_mapping setter function
def _gen_c_map(table,
               table_column,
               scheme,
               value_name,
               default_name,
               default_value,
               style_name,
               network,
               base_url):

    # Check palette and map values to colors
    scheme_func_name = scheme[0]
    scheme_type = scheme[1]
    scheme_func = scheme[2]

    if 'continuous' not in scheme_type:
        raise CyError(f'Scheme {scheme_func_name} cannot be used for continuous mappings')

    # Find out all of the values in the named column
    df_values = tables.get_table_columns(table=table, columns=table_column, network=network, base_url=base_url)

    # For continuous, create triple that contains min, mid, max
    max_data = df_values[table_column].max()
    min_data = df_values[table_column].min()
    if type(max_data) in [int, float]:
        if np.isnan(max_data):
            min_data = 0
            max_data = 1
        mid_data = min_data + (max_data - min_data) / 2
        src_values = [min_data, mid_data, max_data]
    else:
        raise CyError(f'Cannot perform continuous mapping on column "{table_column}", which is not numeric')

    # Create map to min, mid, max values
    dst_values = scheme_func(min_data, max_data)
    return {'table_column': table_column, 'table_column_values': src_values, value_name: dst_values,
            'mapping_type': 'c', default_name: default_value, 'style_name': style_name,
            'network': network, 'base_url': base_url}

# Find the unique values in a column, map them to desired target shapes, and return a dictionary of parameter values
# suiteable for passing to style_mapping setter function
def _gen_d_shape_map(table,
                     table_column,
                     scheme,
                     value_name,
                     default_name,
                     default_value,
                     style_name,
                     network,
                     base_url):
    shape_map = _gen_d_map(table, table_column, scheme, value_name, default_name, default_value, style_name, network, base_url)
    shape_map.pop('mapping_type')
    return shape_map



