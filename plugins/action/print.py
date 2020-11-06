# Copyright 2012, Dag Wieers <dag@wieers.com>
# Copyright 2016, Toshio Kuratomi <tkuratomi@ansible.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleUndefinedVariable
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase

import sys, json

style = 'vim'
pprint = print

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer, MarkdownLexer
    from pygments.formatters import Terminal256Formatter
except ImportError:
    pass  # Handled by AnsibleAWSModule

FORMAT_JSON = 'json'
FORMAT_MARKDOWN = 'md'
FORMAT_MARKDOWN_2 = 'markdown'

class ActionModule(ActionBase):
    ''' Print statements during execution '''

    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(('msg', 'var', 'format'))

    def markdown_out(self, data):
        print(highlight(data, MarkdownLexer(), Terminal256Formatter())[0:-1])

    def json_out(self, data, pretty=False, mono=False, piped_out=False):
        print(highlight(json.dumps(data, indent=2), JsonLexer(), Terminal256Formatter())[0:-1])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        if 'msg' in self._task.args and 'var' in self._task.args:
            return {"failed": True, "msg": "'msg' and 'var' are incompatible options"}

        arg_format = self._task.args['format']

        if arg_format is None or len(arg_format) == 0:
            arg_format = FORMAT_JSON

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        if 'msg' in self._task.args:
            arg_content = self._task.args['msg']
        elif 'var' in self._task.args:
            arg_content = self._templar.template(self._task.args['var'], convert_bare=True, fail_on_undefined=True)

        if arg_format == FORMAT_MARKDOWN or arg_format == FORMAT_MARKDOWN_2:
            self.markdown_out(arg_content)
        else:
            self.json_out(arg_content)

        return { "failed" : False}
