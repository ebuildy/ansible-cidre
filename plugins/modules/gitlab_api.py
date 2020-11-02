#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''

module: community.cidre.gitlab_api

short_description: Call Gitlab HTTP API

author:
  - "Thomas Decaux (@ebuildy)"

description:
  - Use the Gitlab Python API client.

options:
  endpoint:
    description:
    - Full URL to API, default to https://gitlab.com/api/v4
    type: str
  access_token:
    description:
    - access_token to use, default to env GITLAB_TOKEN
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
  ebuildy.cidre.gitlab_api:
    endpoint: "https://gitlab.mysupersite.com/api/v4"
    resource: milestones
    action: get
    context:
      project: 12
    query_string:
        title: "{{ project.version_wanted }}"

- name: Create an issue
  ebuildy.cidre.gitlab_api:
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
  - The Gitlab API response.
  returned: success
  type: complex
'''

import functools, os, json, datetime

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.utils.display import Display

display = Display()

def gitlab_api_get_http_method(resource, action):
    d = {"get": "get", "create": "post", "update": "put", "delete": "delete"}
    return d[action].upper()

def urls_part_to_url(parts):
    if len(parts) == 0:
        return "/"
    return "/" + functools.reduce(lambda a,b : a + "/" + b, parts)

# Remove final "s" (issues -> issue)
def gitlab_api_resource_to_context_item(resource):
    return resource[:-1]

def gitlab_api_build_url(endpoint, resource, context, query_string):

    urlParts = []

    for c_name, c_value in context.items():
        r = c_name + "s"

        urlParts.append(r)
        urlParts.append(str(c_value))

    if resource is not None and len(resource) > 0:
        urlParts.append(resource)

#    resource_item_name = gitlab_api_resource_to_context_item(resource)

#    if resource_item_name in context:
#        urlParts.append(str(context[resource_item_name]))

    full_url = endpoint + urls_part_to_url(urlParts)

    if len(query_string) > 0:
        full_url += "?" + urlencode(query_string)

    return full_url


def run_module():

    module_args = dict(
        endpoint=dict(type='str',default=os.getenv('GITLAB_URL')),
        access_token=dict(type='str', default=os.getenv('GITLAB_TOKEN')),
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

    arg_endpoint = params.get("endpoint")
    arg_access_token =  params.get("access_token")
    arg_resource = params.get("resource")
    arg_action = params.get("action")
    arg_context = params.get("context")
    arg_data = params.get("data")
    arg_query_string = params.get("query_string")

    if arg_endpoint is None or len(arg_endpoint) == 0:
        arg_endpoint = "https://gitlab.com/api/v4"

    http_method = gitlab_api_get_http_method(arg_resource, arg_action)
    http_url = gitlab_api_build_url(arg_endpoint, arg_resource, arg_context, arg_query_string)
    http_query_body = None

    if arg_access_token is None or len(arg_access_token) == 0:
        module.fail_json(msg="Missing access_token!")

    start = datetime.datetime.utcnow()

    if len(arg_data) > 0:
        http_query_body = json.dumps(arg_data)

    display.v(http_url)

    resp, info = fetch_url(
        module,
        http_url,
        headers={"Content-Type" : "application/json", "Authorization" : "Bearer " + arg_access_token},
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
        if "error" in http_content_data:
            error_str = http_content_data["error"]
        else:
            error_str = json.dumps(http_content_data)

        module.fail_json(msg="Gitlab API error: [%s] %s" % (info['status'], error_str))

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
