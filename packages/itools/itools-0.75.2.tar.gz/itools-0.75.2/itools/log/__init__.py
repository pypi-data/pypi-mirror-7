# -*- coding: UTF-8 -*-
# Copyright (C) 2009-2010 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2010 David Versmisse <versmisse@lil.univ-littoral.fr>
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
from log import Logger, register_logger
from log import FATAL, ERROR, WARNING, INFO, DEBUG
from log import log_fatal, log_error, log_warning, log_info, log_debug


__all__ = [
    'Logger',
    'register_logger',
    # Log levels
    'FATAL',
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
    # Log functions
    'log_fatal',
    'log_error',
    'log_warning',
    'log_info',
    'log_debug',
    ]

