# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

class ModuleDocFragment(object):

    DOCUMENTATION = """
options:
  github_url:
    description: API endpoint
    type: string
    default: "https://api.github.com"
    env:
    - name: GITHUB_URL
  github_access_token:
    description: access_token
    type: string
    env:
    - name: GITHUB_TOKEN
    """
