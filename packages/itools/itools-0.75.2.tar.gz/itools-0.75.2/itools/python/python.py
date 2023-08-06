# -*- coding: UTF-8 -*-
# Copyright (C) 2005 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2005-2009 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2008 David Versmisse <versmisse@lil.univ-littoral.fr>
# Copyright (C) 2008 Matthieu France <matthieu@itaapy.com>
# Copyright (C) 2008 Sylvain Taverne <taverne.sylvain@gmail.com>
# Copyright (C) 2008 Wynand Winterbach <wynand.winterbach@gmail.com>
# Copyright (C) 2009 Aurélien Ansel <camumus@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from ast import parse, NodeVisitor

# Import from itools
from itools.handlers import TextFile, register_handler_class
from itools.srx import TEXT



class VisitorUnicode(NodeVisitor):

    def __init__(self):
        self.messages = []


    def visit_Str(self, str):
        if type(str.s) is unicode and str.s.strip():
            # Context = None
            msg = ((TEXT, str.s),), None, str.lineno
            self.messages.append(msg)



class Python(TextFile):

    class_mimetypes = ['text/x-python']
    class_extension = 'py'


    def get_units(self, srx_handler=None):
        data = self.to_str()
        # Make it work with Windows files (the parser expects '\n' ending
        # lines)
        data = ''.join([ x + '\n' for x in data.splitlines() ])
        # Parse and Walk
        ast = parse(data)
        visitor = VisitorUnicode()
        visitor.generic_visit(ast)
        return visitor.messages


# Register
register_handler_class(Python)
