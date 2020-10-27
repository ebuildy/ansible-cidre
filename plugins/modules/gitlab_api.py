#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''

module: cidre

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
    type: list
    elements: str
    choices:
    - projects
    - milestones
    - issues
    - releases
  action:
    description:
    - HTTP method
    type: list
    elements: str
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

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule

def run_module():

    module_args = dict(
        endpoint=dict(type='str'),
        access_token=dict(type='str'),
        action=dict(type='list', elements='str', choices=['get', 'update', 'create', 'delete'], required=True),
        resource=dict(type='str', required=True),
        query_string=dict(type='raw'),
        data=dict(type='raw'),
        context=dict(type='raw')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(module.params)

    fetch_url(module.params["endpoint"])

    module.exit_json(module.params)

def main():
    run_module()


if __name__ == '__main__':
    main()
