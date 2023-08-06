# -*- coding: UTF-8 -*-
# Copyright (C) 2008 J. David Ibáñez <jdavid.ibp@gmail.com>
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
from profile import run as profile
from timeit import Timer

# Import from itools
from itools.uri.parsing import parse_uri, GenericDataType2


test_string = 'http://www.winehq.org/?issue=343#Translations%20within%20WINE'
#test_string = 'http://example.com/'


def bench():
    """Benchmark the speed of itools.abnf using "urlparse.urlsplit" as
    reference.
    """
    # itools
    timer = Timer(
        "parse_uri('%s')" % test_string,
        "from itools.uri.parsing import parse_uri")
    a = timer.repeat(5, number=1)
    a = min(a) * 1000

    # stdlib
    timer = Timer(
        "urlsplit('%s')" % test_string,
        "from urlparse import urlsplit")
    b = timer.timeit(1)
    b = b * 1000

    print '=== urlsplit ==='
    print 'itools: %0.3f ms' % a
    print 'stdlib: %0.3f ms' % b
    print
    print 'itools %d times slower than stdlib' % (a/b)
    print



def bench2():
    """Benchmark the speed of itools.abnf using "urlparse.urlsplit" as
    reference.
    """
    # itools
    timer = Timer(
        "GenericDataType2.decode('%s')" % test_string,
        "from itools.uri.parsing import GenericDataType2")
    a = timer.timeit(1)
    # stdlib
    timer = Timer(
        "GenericDataType.decode('%s')" % test_string,
         "from itools.uri.generic import GenericDataType")
    b = timer.timeit(1)

    print '=== GenericDataType ==='
    print 'itools:', a
    print 'stdlib:', b
    print
    print 'itools %d times slower than stdlib' % (a/b)
    print



if __name__ == '__main__':
    # Just "parse_uri"
    bench()
#    profile('parse_uri("%s")' % test_string)

    # The new GenericDataType
#    bench2()
#    profile('GenericDataType2.decode("%s")' % test_string)

