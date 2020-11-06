#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Thomas Decaux <@ebuildy>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
module: ebuildy.cidre.print
short_description: Print stuff
description: Print markdown or json
author:
- "Thomas Decaux (@ebuildy)"
version_added: '0.5.2'
options:
  format:
    description:
    - json , markdown
    type: str
    choices:
    - json
    - markdown
  msg:
    description:
    - The customized message that is printed. If omitted, prints a generic message.
    type: str
    default: 'Hello world!'
  var:
    description:
    - A variable name to debug.
    - Mutually exclusive with the C(msg) option.
    - Be aware that this option already runs in Jinja2 context and has an implicit C({{ }}) wrapping,
      so you should not be using Jinja2 delimiters unless you are looking for double interpolation.
    type: str
 '''
