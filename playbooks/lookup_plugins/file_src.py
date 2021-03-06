# (c) 2015, Robert Chady <rchady@sitepen.com>
# Based on `runner/lookup_plugins/file.py` for Ansible
#   (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Debops.
# This file is NOT part of Ansible yet.
#
# Debops is free software: you can redistribute it and/or modify
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
# along with Debops.  If not, see <http://www.gnu.org/licenses/>.

'''

This file implements the `file_src` lookup filter for Ansible.  In difference
to the `file` filter, this searches values based on the `file-paths`
variable (colon separated) as configured in DebOps.

NOTE: This means this filter relies on DebOps.

'''

from ansible import utils, errors
import os

from debops import *
from debops.cmds import *

__author__ = "Robert Chady <rchady@sitepen.com>"
__copyright__ = "Copyright 2015 by Robert Chady <rchady@sitepen.com>"
__license__ = "GNU General Public LIcense version 3 (GPL v3) or later"

conf_template = 'file-paths'

class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)
        ret = []

        # this can happen if the variable contains a string, strictly not desired for lookup
        # plugins, but users may try it, so make it work.
        if not isinstance(terms, list):
            terms = [ terms ]

        project_root = find_debops_project(required=False)
        config = read_config(project_root)
        if conf_template_paths in config['paths']:
            places = config['paths'][conf_template_paths].split(':')
        else:
            places = []


        for term in terms:
            if '_original_file' in inject:
                relative_path = utils.path_dwim_relative(inject['_original_file'], 'files', '', self.basedir, check=False)
                places.append(relative_path)
            for path in places:
                template = os.path.join(path, term)
                if template and os.path.exists(template):
                    ret.append(template)
                    break
            else:
                raise errors.AnsibleError("could not locate file in lookup: %s" % term)

        return ret
