#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: gitlab_project
    author: Thomas Decaux
    version_added: "0.1.0"
    short_description: get project ID via name
    extends_documentation_fragment:
    - community.cidre.gitlab_api
    - community.cidre.url
    description:
        - Get project ID via its name
    options:
      _terms:
        description: project name
        required: True
"""

EXAMPLES = """
- name: Display test-cidre project ID
  debug: msg={{ lookup('community.cidre.gitlab_project', 'test-cidre') }}
"""

RETURN = """
  _list:
    description:
      - project ID
    type: int
"""

import json

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleFileNotFound
from ansible.errors import AnsibleError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url, ConnectionError, SSLValidationError
from ansible.utils.display import Display

display = Display()

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        arg_endpoint = self.get_option('gitlab_url')
        arg_access_token = self.get_option('gitlab_access_token')

        ret = []

        for term in terms:
            display.v("search gitlab project %s" % term)

            full_url = "%s/projects?%s" % (arg_endpoint, urlencode({"search":term}))

            display.vvvv(full_url)

            in_headers = self.get_option('headers')

            in_headers['content-type'] = 'application/json'
            in_headers['Authorization'] = "Bearer " + arg_access_token

            try:
                response = open_url(full_url,
                                    validate_certs=self.get_option('validate_certs'),
                                    use_proxy=self.get_option('use_proxy'),
                                    url_username=self.get_option('username'),
                                    url_password=self.get_option('password'),
                                    headers=in_headers,
                                    force=self.get_option('force'),
                                    timeout=self.get_option('timeout'),
                                    http_agent=self.get_option('http_agent'),
                                    force_basic_auth=self.get_option('force_basic_auth'),
                                    follow_redirects=self.get_option('follow_redirects'),
                                    use_gssapi=self.get_option('use_gssapi'),
                                    unix_socket=self.get_option('unix_socket'),
                                    ca_path=self.get_option('ca_path'),
                                    unredirected_headers=self.get_option('unredirected_headers'))

                response_str = to_text(response.read())

                display.vvvv(response_str)

                response_data = json.loads(response_str)

                if response_data is None or len(response_data) == 0:
                    raise AnsibleError('Project "%s" not found!' % term)

                ret.append(str(response_data[0]))

            except HTTPError as e:
                raise AnsibleError("Received HTTP error for %s : %s" % (term, to_native(e)))
            except URLError as e:
                raise AnsibleError("Failed lookup url for %s : %s" % (term, to_native(e)))
            except SSLValidationError as e:
                raise AnsibleError("Error validating the server's certificate for %s: %s" % (term, to_native(e)))
            except ConnectionError as e:
                raise AnsibleError("Error connecting to %s: %s" % (term, to_native(e)))

        return ret
