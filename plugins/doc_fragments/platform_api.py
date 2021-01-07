# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

class ModuleDocFragment(object):

    DOCUMENTATION = """
options:
  api:
    description:
    - gitlab / github / jira
    type: str
    choices:
    - github
    - gitlab
    - bitbucket
    - jira
    - confluence
  repo:
    description: repo name or numerical ID
    type: string
  api_url:
    description: API endpoint
    type: string
  api_token:
    description: access_token
    type: string
    """
