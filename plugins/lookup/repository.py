# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: repository
    author: Thomas Decaux
    version_added: "0.1.0"
    short_description: get project ID via name
    extends_documentation_fragment:
    - ebuildy.cidre.platform_api
    - ebuildy.cidre.url
    description:
        - Get github repo or gitlab project
    options:
      _terms:
        description: repo full URL
"""

EXAMPLES = """
- name: Display test-cidre project ID
  debug: msg={{ lookup('ebuildy.cidre.repository', 'ebuildy/test', api='github') }}
"""

RETURN = """
  _list:
    description:
      - project ID
    type: int
"""

import json
import os

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleFileNotFound
from ansible.errors import AnsibleError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils._text import to_bytes, to_text, to_native
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url, ConnectionError, SSLValidationError
from ansible.utils.display import Display

from ..modules.api import GITLAB, GITHUB

display = Display()

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        self.set_options(direct=merge_two_dicts(variables, kwargs))

        arg_platform = self.get_option('api')
        arg_endpoint = self.get_option('api_url')
        arg_access_token = self.get_option('api_token')

        if arg_platform == "gitlab":
            platform = GITLAB
        else:
            platform = GITHUB

        ret = []

        for term in terms:
            full_url = platform['http_build_url'](arg_endpoint, "", [{"repos" : term}], {})

            display.v(full_url)

            http_headers = self.get_option('headers')

            platform['http_pre_hook'](http_headers, "")

            try:
                response = open_url(full_url,
                                    validate_certs=False,#self.get_option('validate_certs'),
                                    use_proxy=self.get_option('use_proxy'),
                                    url_username=self.get_option('username'),
                                    url_password=self.get_option('password'),
                                    headers=http_headers,
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

                if arg_platform == 'github':
                    response_data['web_url'] = response_data['html_url']
                    response_data['id'] = response_data['number']

                ret.append(response_data)

            except HTTPError as e:
                raise AnsibleError("Received HTTP error for %s : %s" % (term, to_native(e)))
            except URLError as e:
                raise AnsibleError("Failed lookup url for %s : %s" % (term, to_native(e)))
            except SSLValidationError as e:
                raise AnsibleError("Error validating the server's certificate for %s: %s" % (term, to_native(e)))
            except ConnectionError as e:
                raise AnsibleError("Error connecting to %s: %s" % (term, to_native(e)))

        return ret
