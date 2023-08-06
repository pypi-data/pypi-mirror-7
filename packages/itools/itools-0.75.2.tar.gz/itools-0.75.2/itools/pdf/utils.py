# -*- coding: UTF-8 -*-

# Copyright (C) 2007-2009 Henry Obein <henry.obein@gmail.com>
# Copyright (C) 2007-2010, 2012 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2008 David Versmisse <versmisse@lil.univ-littoral.fr>
# Copyright (C) 2008 Dumont Sébastien <sebastien.dumont@itaapy.com>
# Copyright (C) 2008 Fabrice Decroix <fabrice.decroix@gmail.com>
# Copyright (C) 2008 Yannick Martel <yannick.martel@gmail.com>
# Copyright (C) 2010 Hervé Cauwelier <herve@oursours.net>
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
from math import floor

# Import from itools
from itools.datatypes import Unicode, Integer
from itools.handlers import ro_database, Image
from itools.fs import vfs

# Import from reportlab
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm, pica



encoding = 'UTF-8'

def stream_next(stream):
    """
        return the next value of the stream
        (event, value, line_number)
        or
        (None, None, None) if StopIteration exception is raised
    """

    try:
        event, value, line_number = stream.next()
        return (event, value, line_number)
    except StopIteration:
        return (None, None, None)


def normalize(data):
    """
        Normalize data

        http://www.w3.org/TR/html401/struct/text.html#h-9.1
        collapse input white space sequences when producing output inter-word
        space.
    """

    # decode the data
    data = Unicode.decode(data, encoding)
    return ' '.join(data.split())


def join_content(data):
    data = ''.join(data)
    data = Unicode.decode(data, encoding)
    return data


def get_color_as_hexa(str_value, default='#000000'):
    value = str_value.strip()
    if value.startswith('rgb'):
        value = value.lstrip('rgb(').rstrip(')').split(',')
        value = [ int(i) for i in value ]
        tmp = []
        if len(value) == 3:
            # RGB
            for i in value:
                if i < 256:
                    tmp.append('%02x' % i)
                else:
                    print '(WW) the color "%s" is not well formed ' % str_value
                    return default
        value = '#%s' % ''.join(tmp)
    elif value.startswith('#'):
        value_length = len(value)
        if value_length == 4:
            # #aba -> #aabbaa
            r = value[1] * 2
            g = value[2] * 2
            b = value[3] * 2
            value = '#%s%s%s' % (r, g, b)
        elif value_length != 7:
            print '(WW) the color "%s" is not well formed ' % str_value
    else:
        # Warning getAllNamedColors() uses a singleton
        value = ('#%02x%02x%02x' %
                 colors.toColor(value, colors.black).bitmap_rgb())
    return value


def exist_attribute(attrs, keys, at_least=False):
    """
        if at_least is False
        Return True if all key in keys
        are contained in the dictionnary attrs
    """

    if at_least is False:
        for key in keys:
            if (None, key) not in attrs:
                return False
        return True
    else:
        for key in keys:
            if (None, key) in attrs:
                return True
        return False


##############################################################################
# Math
##############################################################################
def round(value):
    return floor(value + 0.5)


def pc_float(ratio, value):
    if ratio == 100:
        return value
    return ratio * value / 100.0


def get_int_value(value, default=0):
    """
    Return the interger representation of value is his decoding succeed
    otherwise the default value
    """
    if not value:
        return default
    try:
        return Integer.decode(value)
    except ValueError:
        return default


##############################################################################
# reportlab
##############################################################################
FONTSIZE = {'xx-small': 20, 'x-small': 40, 'smaller': 60, 'small':80,
            'medium':100, 'large': 120, 'larger': 140, 'x-large': 160,
            'xx-large': 180}


# 16px = 12pt
SIZE = {'in': inch, 'cm': cm, 'mm': mm, 'pica': pica, 'px': 1, 'pt': 4/3}


def font_value(str_value, style_size=12):
    style_size = 12  # TODO : replace default_value by current stylesheet size
    if str_value[0].isalpha():
        ratio = FONTSIZE.get(str_value, 100)
        value = pc_float(ratio, style_size)
    elif str_value.endswith('%'):
        ratio = get_int_value(str_value.rstrip('%'), 100)
        value = pc_float(ratio, style_size)
    elif str_value.endswith('pt'):
        value = str_value.rstrip('pt')
        ratio = SIZE['pt']
        value = get_int_value(value, style_size) * ratio
    else:
        # px
        value = str_value.rstrip('px')
        value = get_int_value(value, style_size)
    return value


def reportlab_value(value, current_value, default=None):
    size = format_size(value, default)
    if isinstance(size, str) and size.endswith('%'):
        size = get_int_value(size[:-1])
        size = pc_float(size, current_value)
    return size


def format_size(value, default=None):
    """
       Return the reportlab value of value
       only if value is a string
       '2cm' -> 2 * cm
       '2in' -> 2 * inch
       '2in' -> 2 * mm
       '2in' -> 2 * pica
       '2%' -> '2%'
    """

    if value is None:
        return default

    coef = 1
    if not isinstance(value, (str, unicode)):
        return value
    if value == 'None':
        return None
    if value.endswith('%'):
        return value
    for key in SIZE.keys():
        if value.endswith(key):
            value = value[:-len(key)]
            coef = SIZE[key]
            break
    try:
        value = float(value) * coef
    except ValueError:
        value = default
    return value


def get_color(value):
    value = get_color_as_hexa(value)
    color = colors.toColor(value, colors.black)
    return color


##############################################################################
# Image
##############################################################################
def check_image(filename, context):
    if vfs.exists(filename) is False:
        print u"(WW) The filename '%s' doesn't exist" % filename
        filename = context.image_not_found_path
    im = None
    if filename.startswith('http://'):
        # Remote file
        # If the image is a remote file, we create a StringIO
        # object contains the image data to avoid reportlab problems ...
        data = vfs.open(filename).read()
        my_file = context.get_tmp_file()
        filename = my_file.name
        my_file.write(data)
        my_file.close()
        im = Image(string=data)
    if im is None:
        im = ro_database.get_handler(filename, Image)

    x, y = im.get_size()
    if not (x or y):
        print u'image not valid : %s' % filename
        filename = context.image_not_found_path
        im = ro_database.get_handler(filename, Image)
        x, y = im.get_size()

    return filename, (x, y)
