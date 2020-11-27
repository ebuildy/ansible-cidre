#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''

module: platform

short_description: Call Github or Gitlab HTTP API

description: Call Github or Gitlab HTTP API

author:
  - "Thomas Decaux (@ebuildy)"

extends_documentation_fragment:
- ebuildy.cidre.platform_api

options:
  resource:
    description:
    - Query string
    type: str
  action:
    description:
    - HTTP method
    type: str
    default: get
    choices:
    - get
    - update
    - delete
    - create
  query_string:
    description:
    - Data to send as JSON body
    type: raw
  data:
    description:
    - Data to send as JSON body
    type: raw
  context:
    description:
    - Related project / user / issue / milestone ID
    type: raw
  body_format:
    type: str
    default: json

requirements:
  - "python >= 2.7"
'''

EXAMPLES = r'''
- name: Search a milestone
  ebuildy.cidre.platform:
    platform: gitlab
    resource: milestones
    action: get
    context:
      project: 12
    query_string:
        title: "{{ project.version_wanted }}"

- name: Create an issue
  ebuildy.cidre.platform:
    platform: gitlab
    resource: issues
    action: create
    context:
      project: 12
    data:
        title: "Just a text"
        description: "Ok I am a test"
        milestone_id: 1
'''

RETURN = r'''
result:
  description:
  - The platform API response.
  returned: success
  type: complex
'''

import functools
import os
import json
import datetime

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote

def urls_part_to_url(parts):
    if len(parts) == 0:
        return "/"
    return "/" + functools.reduce(lambda a,b : a + "/" + b, parts)

# Remove final "s" (issues -> issue)
def platform_api_resource_to_context_item(resource):
    return resource[:-1]

def platform_api_build_url(endpoint, resource, context, query_string):

    urlParts = []

    for c_item in context:
        for c_name, c_value in c_item.items():
            r = c_name + "s"

            urlParts.append(r)
            urlParts.append(str(c_value))

    if resource is not None and len(resource) > 0:
        urlParts.append(resource)

    full_url = endpoint + urls_part_to_url(urlParts)

    if len(query_string) > 0:
        full_url += "?" + urlencode(query_string)

    return full_url

def get_endpoint(arg_endpoint, default):
    if arg_endpoint is not None and len(arg_endpoint) > 0:
        return arg_endpoint

    if "CIDRE_URL" in os.environ:
        return os.environ["CIDRE_URL"]

    return default


def gitlab_pre_http(headers, access_token):
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"

    if access_token is None or len(access_token) == 0:
        if "GITLAB_TOKEN" in os.environ:
            access_token = os.environ["GITLAB_TOKEN"]

    if access_token is not None and len(access_token) > 0:
        headers['Authorization'] = "Bearer " + access_token


def gitlab_api_build_url(endpoint, resource, context, query_string):
    endpoint = get_endpoint(endpoint, "https://gitlab.com/api/v4")

    for item in context:
        if "repo" in item:
            item["project"] = quote(item["repo"], safe='')
            del item["repo"]

    if "state" in query_string:
        if query_string['state'] == 'open':
            query_string['state'] = 'opened'
        elif query_string['state'] == 'close':
            query_string['state'] = 'closed'

    return platform_api_build_url(endpoint, resource, context, query_string)

def github_api_build_url(endpoint, resource, context, query_string):
    endpoint = get_endpoint(endpoint, "https://api.github.com")

    return platform_api_build_url(endpoint, resource, context, query_string)

def github_pre_http(headers, access_token):
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/vnd.github.v3+json"

    if access_token is None or len(access_token) == 0:
        if "GITHUB_TOKEN" in os.environ:
            access_token = os.environ["GITHUB_TOKEN"]

    if access_token is not None and len(access_token) > 0:
        headers['Authorization'] = "token " + access_token

def jira_pre_http(headers, access_token):
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"

    if access_token is None or len(access_token) == 0:
        if "JIRA_TOKEN" in os.environ:
            access_token = os.environ["JIRA_TOKEN"]

    if access_token is not None and len(access_token) > 0:
        headers['Authorization'] = "Basic " + access_token

def jira_build_url(endpoint, resource, context, query_string):
    endpoint = get_endpoint(endpoint, "https://jira.atlassian.com/rest")

    if resource == "session":
        endpoint = endpoint + "/auth/latest"
    else:
        endpoint = endpoint + "/api/latest"

    return platform_api_build_url(endpoint, resource, context, query_string)


GITHUB = {
    "env" : {
        "url" : "GITHUB_URL",
        "token" : "GITHUB_TOKEN"
    },
    "http_methods" : {"get": "get", "create": "post", "update": "patch", "delete": "delete"},
    "http_pre_hook" : github_pre_http,
    "http_build_url" : github_api_build_url
}

GITLAB = {
    "env" : {
        "url" : "GITLAB_URL",
        "token" : "GITLAB_TOKEN"
    },
    "http_methods" : {"get": "get", "create": "post", "update": "put", "delete": "delete"},
    "http_pre_hook" : gitlab_pre_http,
    "http_build_url" : gitlab_api_build_url
}

JIRA = {
    "env" : {
        "url" : "JIRA_URL",
        "token" : "JIRA_TOKEN"
    },
    "http_methods" : {"get": "get", "create": "post", "update": "put", "delete": "delete"},
    "http_pre_hook" : jira_pre_http,
    "http_build_url" : jira_build_url
}

def run_module():

    module_args = dict(
        provider=dict(type='str', choices=['github', 'gitlab', 'bitbucket', 'jira']),
        provider_endpoint=dict(type='str'),
        provider_access_token=dict(type='str'),
        action=dict(type='str', choices=['get', 'update', 'create', 'delete'], default="get"),
        resource=dict(type='str'),
        query_string=dict(type='raw', default={}),
        data=dict(type='raw', default={}),
        context=dict(type='raw', default={}),
        body_format=dict(type='str', default='json')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    params = module.params

    if module.check_mode:
        module.exit_json(module.params)

    arg_platform = params.get("provider")
    arg_endpoint = params.get("provider_endpoint")
    arg_access_token =  params.get("provider_access_token")
    arg_resource = params.get("resource")
    arg_action = params.get("action")
    arg_context = params.get("context")
    arg_data = params.get("data")
    arg_query_string = params.get("query_string")

    if arg_platform == "gitlab":
        platform = GITLAB
    elif arg_platform == "jira":
        platform = JIRA
    else:
        platform = GITHUB

    #if "repo" not in arg_context and arg_repo is not None and len(arg_repo) > 0:
    #    arg_context["repo"] = arg_repo

    http_method = platform['http_methods'][arg_action]
    http_url = platform['http_build_url'](arg_endpoint, arg_resource, arg_context, arg_query_string)
    http_query_body = None
    http_headers = {}

    module.warn(http_url)

    platform['http_pre_hook'](http_headers, arg_access_token)

    start = datetime.datetime.utcnow()

    if len(arg_data) > 0:
        http_query_body = json.dumps(arg_data)

    module.params['validate_certs'] = False

    resp, info = fetch_url(
        module,
        http_url,
        headers=http_headers,
        method=http_method,
        data=http_query_body
    )

    http_response_status = int(info['status'])

    if (http_response_status <= 0 or (http_response_status >= 400 and http_response_status < 500)) and "msg" in info:
        module.warn(info["msg"])

    try:
        content = resp.read()
    except AttributeError:
        # there was no content, but the error read()
        # may have been stored in the info as 'body'
        content = info.pop('body', '')

    if arg_platform == "jira" and (http_response_status == 400):
        http_response_status = 200

    if http_response_status <= 0 or (http_response_status >= 400 and http_response_status < 500):
        module.fail_json(msg="Platform error [%s] when %s %s : %s" % (info['status'], http_method, http_url, content))

    try:
        http_content_data = json.loads(content)
    except ValueError as e:
        module.fail_json(msg="[%s] JSON decode error: %s" % (http_response_status, content))

    uresp = {
        "url" : http_url,
        "status" : http_response_status,
        "elapsed" : (datetime.datetime.utcnow() - start).seconds
    }

    module.exit_json(content=http_content_data, **uresp)

def main():
    run_module()


if __name__ == '__main__':
    main()
