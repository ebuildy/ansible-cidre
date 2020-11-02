#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''

module: community.cidre.platform

short_description: Call Github or Gitlab HTTP API

author:
  - "Thomas Decaux (@ebuildy)"

options:
  platform:
    description:
    - gitlab / github
    type: str
    choices:
    - github
    - gitlab
    - bitbucket
  endpoint:
    description:
    - Full URL to API, default to public URL
    type: str
  access_token:
    description:
    - access_token to use, default to env platform_TOKEN / GITLAB_TOKEN
    type: str
  resource:
    description:
    - Query string
    type: str
    choices:
    - projects
    - milestones
    - issues
    - releases
  action:
    description:
    - HTTP method
    type: str
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

requirements:
  - "python >= 2.7"
  - "openshift >= 0.6"
  - "PyYAML >= 3.11"
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
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.utils.display import Display

display = Display()

GITHUB = {
    "DEFAULT_URL": "https://api.github.com",

    "env" : {
        "url" : "GITHUB_URL",
        "token" : "GITHUB_TOKEN"
    },

    "http_methods" : {"get": "get", "create": "post", "update": "patch", "delete": "delete"},

    "DEFAULT_HEADERS": {
        "Content-Type" : "application/json",
        "Accept" : "application/vnd.github.v3+json"
    },

    "AUTH_HEADER": "token"

}

GITLAB = {
    "DEFAULT_URL": "https://gitlab.com/api/v4",

    "env" : {
        "url" : "GITLAB_URL",
        "token" : "GITLAB_TOKEN"
    },

    "http_methods" : {"get": "get", "create": "post", "update": "put", "delete": "delete"},

    "DEFAULT_HEADERS": {
        "Content-Type" : "application/json"
    },

    "AUTH_HEADER": "Bearer"

}

def urls_part_to_url(parts):
    if len(parts) == 0:
        return "/"
    return "/" + functools.reduce(lambda a,b : a + "/" + b, parts)

# Remove final "s" (issues -> issue)
def platform_api_resource_to_context_item(resource):
    return resource[:-1]

def platform_api_build_url(endpoint, resource, context, query_string):

    urlParts = []

    for c_name, c_value in context.items():
        r = c_name + "s"

        urlParts.append(r)
        urlParts.append(str(c_value))

    if resource is not None and len(resource) > 0:
        urlParts.append(resource)

    full_url = endpoint + urls_part_to_url(urlParts)

    if len(query_string) > 0:
        full_url += "?" + urlencode(query_string)

    return full_url


def run_module():

    module_args = dict(
        platform=dict(type='str', choices=['github', 'gitlab', 'bitbucket']),
        endpoint=dict(type='str'),
        access_token=dict(type='str'),
        action=dict(type='str', choices=['get', 'update', 'create', 'delete'], default="get"),
        resource=dict(type='str', choices=['projects', 'groups', 'issues', 'milestones']),
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

    arg_platform = params.get("platform")
    arg_endpoint = params.get("endpoint")
    arg_access_token =  params.get("access_token")
    arg_resource = params.get("resource")
    arg_action = params.get("action")
    arg_context = params.get("context")
    arg_data = params.get("data")
    arg_query_string = params.get("query_string")

    if arg_platform == "gitlab":
        platform = GITLAB
    else:
        platform = GITHUB

    if arg_endpoint is None or len(arg_endpoint) == 0:
        if platform['env']['url'] in os.environ:
            arg_access_token = os.environ[platform['env']['url']]
        else:
            arg_endpoint = platform["DEFAULT_URL"]

    http_method = platform['http_methods'][arg_action]
    http_url = platform_api_build_url(arg_endpoint, arg_resource, arg_context, arg_query_string)
    http_query_body = None
    http_headers = platform["DEFAULT_HEADERS"]

    if arg_access_token is None or len(arg_access_token) == 0:
        if platform['env']['token'] in os.environ:
            arg_access_token = os.environ[platform['env']['token']]
        else:
            display.vv("Missing access_token!")

    if len(arg_access_token) > 0:
        http_headers["Authorization"] = "%s %s" % (platform['AUTH_HEADER'], arg_access_token)

    start = datetime.datetime.utcnow()

    if len(arg_data) > 0:
        http_query_body = json.dumps(arg_data)

    display.v(http_url)

    resp, info = fetch_url(
        module,
        http_url,
        headers=http_headers,
        method=http_method,
        data=http_query_body
    )

    try:
        content = resp.read()
    except AttributeError:
        # there was no content, but the error read()
        # may have been stored in the info as 'body'
        content = info.pop('body', '')

    http_response_status = int(info['status'])
    http_content_data = json.loads(content)

    if http_response_status >= 400 and http_response_status < 500:
        module.fail_json(msg="Platform error [%s] when calling %s : %s" % (info['status'], http_url, content))

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
