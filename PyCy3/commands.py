# -*- coding: utf-8 -*-

import requests
import urllib.parse
import json

from .pycy3_utils import *
from .exceptions import CyError
from PyCy3.decorators import debug

def __init__(self):
    pass

#TODO: Refactor functions to centralize HTTP handling and error handling


def cyrest_get(operation=None, parameters=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """ Perform HTTP GET and return a list object if JSON is returned; otherwise, just text """
    try:
        r = requests.get(url = build_url(base_url, operation), params=parameters)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        content = json.loads(e.response.content) if e.response and e.response.content else ''
        print("In commands:cyrest_get(): " + str(e) + '\n' + str(content))
        raise


def cyrest_post(operation=None, parameters=None, body=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """ Perform HTTP POST and return a list object if JSON is returned; otherwise, just text """
    try:
        r = requests.post(url=build_url(base_url, operation), params=parameters, json=body)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        content = json.loads(e.response.content)
        print("In commands:cyrest_post(): " + str(e) + '\n' + str(content))
        raise


def cyrest_put(operation=None, parameters=None, body=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """ Perform HTTP PUT and return a list object if JSON is returned; otherwise, just text """
    try:
        r = requests.put(url=build_url(base_url, operation), params=parameters, json=body)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        content = json.loads(e.response.content)
        print("In commands:cyrest_put(): " + str(e) + '\n' + str(content))
        raise


def cyrest_delete(operation=None, parameters=None, base_url=DEFAULT_BASE_URL, require_json=True):
    try:
        r = requests.delete(url = build_url(base_url, operation), params=parameters)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        content = json.loads(e.response.content)
        print("In commands:cyrest_delete(): " + str(e) + '\n' + str(content))
        raise

def commands_post(cmd, base_url=DEFAULT_BASE_URL, require_json=True):
    try:
        post_url = _command_2_post_query_url(cmd, base_url=base_url)
        post_body = _command_2_post_query_body(cmd)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(post_url, data=post_body, headers=headers)
        r.raise_for_status()
        return json.loads(r.text)['data']
    except requests.exceptions.RequestException as e:
        content = json.loads(e.response.content)
        print("In commands:commands_post(): " + str(e) + '\n' + str(content))

        raise CyError(content['errors'][0]['message'])

def _command_2_post_query_url(cmd, base_url=DEFAULT_BASE_URL):
    """ Construct complete command URL from base URL and Cytoscape command """

    # Wipe out parameters so we can focus just on the Cytoscape command
    # For example, 'network get attribute network="test" namespace="default" columnList="SUID"'
    # becomes 'network get attributeXXXXXXnetwork="test"XXXXXXnamespace="default"XXXXXXcolumnList="SUID"'
    cmd_mark_params = re.sub(r' ([A-Za-z0-9_-]*=)', 'XXXXXX\\1', cmd)

    # Separate Cytoscape command and parameters. Using the above:
    # 'network get attribute', 'network="test"', 'namespace="default"', 'columnList="SUID"'
    split_cmd = cmd_mark_params.split('XXXXXX')
    cy_cmd = split_cmd[0]

    # Assemble just the cy_cmd as a CyREST command URL
    if cy_cmd is None: cy_cmd = ''
    url = base_url + urllib.parse.quote('/commands/' + re.sub(' ', '/', cy_cmd, count=1))

    return url

def _command_2_post_query_body(cmd):
    """ Construct body of POST as JSON representing inline parameters """

    # Set markers 'XXXXXX" on each parameter so we can see where they are.
    # For example, 'network get attribute network="test" namespace="default" columnList="SUID"'
    # becomes 'network get attributeXXXXXXnetwork="test"XXXXXXnetwork="default"XXXXXXcolumnList="SUID"'
    cmd_mark_params = re.sub(r' ([A-Za-z0-9_-]*=)', 'XXXXXX\\1', cmd)
    split_cmd = cmd_mark_params.split("XXXXXX")

    # Extract just the parameters ... if there are none, invent one
    params = split_cmd[1:]
    if params is None: params = ['atLeastOneArg=required']

    # Create a dictionary containing params as key-value, squeezing out quotes
    param_dict = {}
    for x in params:
        p = re.sub('"', '', x).split('=', 1)
        if p[0] is None: raise CyError('Missing parameter name')
        param_dict[p[0]] = p[1]

    return str.encode(json.dumps(param_dict))

def prep_post_query_lists(cmd_list=None, cmd_by_col=None):
    if cmd_list is None:
         cmd_list_ready = 'selected'
    elif not cmd_by_col is None:
        cmd_list_col = [cmd_by_col + ':' + cmd    for cmd in cmd_list]
        cmd_list_ready = ','.join(cmd_list_col)
    else:
        cmd_list_ready = cmd_list if isinstance(cmd_list, str) else ','.join(cmd_list)

    return cmd_list_ready
