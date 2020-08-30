# -*- coding: utf-8 -*-

"""Functions for inspecting and managing apps for Cytoscape.
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
import sys

# Internal module imports
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


@cy_log
def disable_app(app, base_url=DEFAULT_BASE_URL):
    """Disable App.

    Disable an app to effectively remove it from your Cytoscape session without having to uninstall it.

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'appName': <name of app>}, and is returned whether or not app exists

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> disable_app('stringApp')
        {'appName': 'stringApp'}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps disable app="{app}"', base_url=base_url)
    return narrate(res)


@cy_log
def enable_app(app, base_url=DEFAULT_BASE_URL):
    """Enable App.

    Enable a previously installed and disabled app in Cytoscape.

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'appName': <name of app>}, and is returned whether or not app exists

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> enable_app('stringApp')
        {'appName': 'stringApp'}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps enable app="{app}"', base_url=base_url)
    return narrate(res)


@cy_log
def get_app_information(app, base_url=DEFAULT_BASE_URL):
    """Retrieve the name, brief description and version of a Cytoscape app.

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: 'Unused memory freed up.'

    Raises:
        CyError: if app is unknown
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_app_information('stringApp')
        {'app': 'stringApp', 'descriptionName': 'Import and augment Cytoscape networks from STRING', 'version': '1.5.1'}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps information app="{app}"', base_url=base_url)
    return res


@cy_log
def install_app(app, base_url=DEFAULT_BASE_URL):
    """Installs an app in Cytoscape

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} always empty, whether app exists or not

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> install_app('stringApp')
        {}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps install app="{app}"', base_url=base_url)
    return narrate(res)


@cy_log
def get_available_apps(base_url=DEFAULT_BASE_URL):
    """Retrieve a list of apps available for installation in Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts, one for each app {'appName': <appname>, 'description': <description>, 'details': <details>}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_available_apps()
        [{'appName': 'stringApp', 'description': 'Import and augment Cytoscape networks from STRING', 'details': ''}, {...}, ...]
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post('apps list available', base_url=base_url)
    return res


@cy_log
def get_disabled_apps(base_url=DEFAULT_BASE_URL):
    """Retrieve list of currently disabled apps in Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts, one for each app {'appName': <appname>, 'version': <version>, 'description': <description>, 'status': <status>} where <status> is always 'Disabled'

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_disabled_apps()
        [{'appName': 'stringApp', 'version': '1.4.2', 'description': 'Import and augment Cytoscape networks from STRING', 'status': 'Disabled'}, {...}, ...]
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post('apps list disabled', base_url=base_url)
    return res


@cy_log
def get_installed_apps(base_url=DEFAULT_BASE_URL):
    """Retrieve list of currently installed apps in Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts, one for each app {'appName': <appname>, 'version': <version>, 'description': <description>, 'status': <status>} where status may be 'Installed', 'Disabled', 'Uninstalled'

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_installed_apps()
        [{'appName': 'JSON Support', 'version': '3.7.0', 'description': 'null', 'status': 'Installed'}, ...]
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post('apps list installed', base_url=base_url)
    return res


@cy_log
def get_uninstalled_apps(base_url=DEFAULT_BASE_URL):
    """Retrieve list of apps not currently installed in Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts, one for each app {'appName': <appname>, 'version': <version>, 'description': <description>, 'status': <status>} where status may be 'Installed', 'Disabled', 'Uninstalled'

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_uninstalled_apps()
        [{'appName': 'JSON Support', 'version': '3.7.0', 'description': 'null', 'status': 'Uninstalled'}, ...]
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post('apps list uninstalled', base_url=base_url)
    return res


@cy_log
def get_app_updates(base_url=DEFAULT_BASE_URL):
    """Retrieve list of currently installed Cytoscape apps with updates available.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts, one for each app {'appName': <appname>, 'version': <version>, 'information': <information>}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_app_updates()
        [{'appName': 'JSON Support', 'version': '3.7.0', 'information': 'null'}, ...]
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post('apps list updates', base_url=base_url)
    return res


@cy_log
def open_app_store(app, base_url=DEFAULT_BASE_URL):
    """Opens the Cytoscape App Store in a new tab in your default browser.

    Args:
        app (str): Name of app ('' for main App Store page)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} whether page for app exists or not

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> open_app_store('stringApp')
        {}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps open appstore app="{app}"', base_url=base_url)
    return narrate(res)


@cy_log
def get_app_status(app, base_url=DEFAULT_BASE_URL):
    """Retrieve the current status of a Cytoscape app: Installed, Uninstalled or Disabled.

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'appName': <appname>, 'status': <status>} where <status> is Installed, Disabled or Uninstalled

    Raises:
        CyError: if app does not exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_app_status('stringApp')
        {'appName': 'stringApp', 'status': 'Installed'}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps status app="{app}"', base_url=base_url)
    return res


@cy_log
def uninstall_app(app, base_url=DEFAULT_BASE_URL):
    """Uninstall an app from Cytoscape.

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'appName': <name of app>} whether app exists or not

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> uninstall_app('stringApp')
        {'appName': 'stringApp'}
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps uninstall app="{app}"', base_url=base_url)
    return narrate(res)


@cy_log
def update_app(app, base_url=DEFAULT_BASE_URL):
    """Update a Cytoscape app to the latest available version.

    Args:
        app (str): Name of app
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [] whether or not app exists

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> update_app('stringApp')
        []
    """
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post(f'apps update app="{app}"', base_url=base_url)
    return narrate(res)
