# -*- coding: utf-8 -*-

"""Functions that support use of Cytoscape in a Jupyter Notebook environment.
"""

"""Copyright 2020 The Cytoscape Consortium

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

# Internal module imports
from . import network_views
from . import sandbox

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_notebook import get_notebook_is_running

@cy_log
def notebook_export_show_image(filename='image', type='PNG', resolution=None, units=None, height=None, width=None, zoom=None,
                               sandbox_name=None, network=None, base_url=DEFAULT_BASE_URL, *, overwrite_file=True):
    """Show network view in notebook output.

    Export a network view to an image file, then upload the file to the notebook file system and display the image.

    Args:
        filename (str): Full path or path relative to current working directory, in addition to the name of the file.
            File is used to save image of network view so it can be transferred to the notebook file system and displayed.
            Extension is automatically added based on the ``type`` argument.
        type (str): Type of image to export, e.g., PNG (default), JPEG, PDF, SVG, PS (PostScript).
        resolution (int): The resolution of the exported image, in DPI. Valid only for bitmap formats, when the selected
            width and height 'units' is inches. The possible values are: 72 (default), 100, 150, 300, 600.
        units (str) The units for the 'width' and 'height' values. Valid only for bitmap formats, such as PNG and JPEG.
            The possible values are: pixels (default), inches.
        height (float): The height of the exported image. Valid only for bitmap formats, such as PNG and JPEG.
        width (float): The width of the exported image. Valid only for bitmap formats, such as PNG and JPEG.
        zoom (float): The zoom value to proportionally scale the image. The default value is 100.0. Valid only for bitmap
            formats, such as PNG and JPEG
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and used.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        overwrite_file (bool): False allows Cytoscape show a message box before overwriting the file if the file already
            exists; True allows Cytoscape to overwrite it without asking

    Returns:
        object: iPython.display.Image class instance

    Raises:
        CyError: if network doesn't exist or the file cannot be written
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> notebook_export_show_image()
        >>> notebook_export_show_image('myfile.png', overwrite_file=False)
        >>> notebook_export_show_image('imagex', type='JPG')
    """
    return _export_show_image(export_first=True, filename=filename, type=type, resolution=resolution, units=units,
                              height=height, width=width, zoom=zoom, sandbox_name=sandbox_name, network=network,
                              base_url=base_url, overwrite_file=overwrite_file)

@cy_log
def notebook_show_image(filename, type='PNG', sandbox_name=None, network=None, base_url=DEFAULT_BASE_URL,
                        *, overwrite_file=True):
    """Show a pre-existing image file in notebook output.

    Upload an existing image file to the notebook file system and display the image.

    Args:
        filename (str): Full path or path relative to current working directory, in addition to the name of the file.
            File must already exist, and will be transferred to the notebook file system and displayed.
            Extension is automatically added based on the ``type`` argument.
        type (str): Type of image to export, e.g., PNG (default), JPEG, PDF, SVG, PS (PostScript).
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        overwrite_file (bool): False allows Cytoscape show a message box before overwriting the file if the file already
            exists; True allows Cytoscape to overwrite it without asking

    Returns:
        object: iPython.display.Image class instance

    Raises:
        CyError: if network doesn't exist or the file cannot be written
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> notebook_show_image('myimage.jpg', overwrite_file=False)
        >>> notebook_show_image('imagex', type='JPG')
    """
    return _export_show_image(export_first=False, filename=filename, type=type, sandbox_name=sandbox_name,
                              base_url=base_url, overwrite_file=overwrite_file)

def _export_show_image(export_first, filename='image', type='PNG', resolution=None, units=None, height=None, width=None, zoom=None,
                       sandbox_name=None, network=None, base_url=DEFAULT_BASE_URL, *, overwrite_file=True):
    if get_notebook_is_running():
        # Add suffix if one is not supplied ... preserve sandbox subdirectory if one is provided
        if re.search('.' + type.lower() + '$', filename) is None: filename += '.' + type.lower()

        # Create network image file in sandbox
        if export_first:
            network_views.export_image(filename=filename, type=type, resolution=resolution, units=units, height=height, width=width, zoom=zoom,
                                       network=network, base_url=base_url, overwrite_file=overwrite_file)

        # Transfer sandbox version of image to local storage so notebook can see it
        sandbox.sandbox_get_from(filename, overwrite=overwrite_file, sandbox_name=sandbox_name, base_url=base_url)

        from IPython import display
        return display.Image(filename)
    else:
        raise CyError('Cannot display network view image unless running as a Jupyter Notebook.')


