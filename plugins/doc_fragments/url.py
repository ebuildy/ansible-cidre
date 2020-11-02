# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

class ModuleDocFragment(object):

    DOCUMENTATION = """
options:
  validate_certs:
    description: Flag to control SSL certificate validation
    type: boolean
    default: True
  use_proxy:
    description: Flag to control if the lookup will observe HTTP proxy environment variables when present.
    type: boolean
    default: True
  username:
    description: Username to use for HTTP authentication.
    type: string
    version_added: "2.8"
  password:
    description: Password to use for HTTP authentication.
    type: string
    version_added: "2.8"
  headers:
    description: HTTP request headers
    type: dictionary
    default: {}
    version_added: "2.9"
  force:
    description: Whether or not to set "cache-control" header with value "no-cache"
    type: boolean
    version_added: "2.10"
    default: False
    vars:
        - name: ansible_lookup_url_force
    env:
        - name: ANSIBLE_LOOKUP_URL_FORCE
    ini:
        - section: url_lookup
          key: force
  timeout:
    description: How long to wait for the server to send data before giving up
    type: float
    version_added: "2.10"
    default: 10
    vars:
        - name: ansible_lookup_url_timeout
    env:
        - name: ANSIBLE_LOOKUP_URL_TIMEOUT
    ini:
        - section: url_lookup
          key: timeout
  http_agent:
    description: User-Agent to use in the request. The default was changed in 2.11 to C(ansible-httpget).
    type: string
    version_added: "2.10"
    default: ansible-httpget
    vars:
        - name: ansible_lookup_url_agent
    env:
        - name: ANSIBLE_LOOKUP_URL_AGENT
    ini:
        - section: url_lookup
          key: agent
  force_basic_auth:
    description: Force basic authentication
    type: boolean
    version_added: "2.10"
    default: False
    vars:
        - name: ansible_lookup_url_agent
    env:
        - name: ANSIBLE_LOOKUP_URL_AGENT
    ini:
        - section: url_lookup
          key: agent
  follow_redirects:
    description: String of urllib2, all/yes, safe, none to determine how redirects are followed, see RedirectHandlerFactory for more information
    type: string
    version_added: "2.10"
    default: 'urllib2'
    vars:
        - name: ansible_lookup_url_follow_redirects
    env:
        - name: ANSIBLE_LOOKUP_URL_FOLLOW_REDIRECTS
    ini:
        - section: url_lookup
          key: follow_redirects
  use_gssapi:
    description:
    - Use GSSAPI handler of requests
    - As of Ansible 2.11, GSSAPI credentials can be specified with I(username) and I(password).
    type: boolean
    version_added: "2.10"
    default: False
    vars:
        - name: ansible_lookup_url_use_gssapi
    env:
        - name: ANSIBLE_LOOKUP_URL_USE_GSSAPI
    ini:
        - section: url_lookup
          key: use_gssapi
  unix_socket:
    description: String of file system path to unix socket file to use when establishing connection to the provided url
    type: string
    version_added: "2.10"
    vars:
        - name: ansible_lookup_url_unix_socket
    env:
        - name: ANSIBLE_LOOKUP_URL_UNIX_SOCKET
    ini:
        - section: url_lookup
          key: unix_socket
  ca_path:
    description: String of file system path to CA cert bundle to use
    type: string
    version_added: "2.10"
    vars:
        - name: ansible_lookup_url_ca_path
    env:
        - name: ANSIBLE_LOOKUP_URL_CA_PATH
    ini:
        - section: url_lookup
          key: ca_path
  unredirected_headers:
    description: A list of headers to not attach on a redirected request
    type: list
    version_added: "2.10"
    vars:
        - name: ansible_lookup_url_unredir_headers
    env:
        - name: ANSIBLE_LOOKUP_URL_UNREDIR_HEADERS
    ini:
        - section: url_lookup
          key: unredirected_headers
    """
