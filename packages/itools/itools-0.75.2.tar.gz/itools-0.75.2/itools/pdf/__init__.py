# -*- coding: UTF-8 -*-
# Copyright (C) 2007, 2009-2010 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2008 David Versmisse <versmisse@lil.univ-littoral.fr>
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

# Import from itools
from itools.core import get_abspath
from itools.handlers import ro_database
from itools.relaxng import RelaxNGFile
from pdf import PDFFile

# There are imports from ReportLab in these imports, so, ...
try:
    from pml import pmltopdf, stl_pmltopdf
except ImportError:
    print 'You need to install the package "reportlab" to get PML working.'

    # Not implemented, ...
    def not_implemented(*args, **kw):
        raise NotImplementedError, 'the package "reportlab" must be installed'
    pmltopdf = not_implemented
    stl_pmltopdf = not_implemented


__all__ = [
    'PDFFile',
    'pmltopdf',
    'stl_pmltopdf']


# Read the Relax NG schema of PML and register its namespace
rng_file = get_abspath('PML-schema.rng')
rng_file = ro_database.get_handler(rng_file, RelaxNGFile)
rng_file.auto_register()

