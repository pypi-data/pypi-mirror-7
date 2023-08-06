# -*- coding: UTF-8 -*-

# Copyright (C) 2007-2009 Henry Obein <henry.obein@gmail.com>
# Copyright (C) 2007-2009, 2012 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2008 David Versmisse <versmisse@lil.univ-littoral.fr>
# Copyright (C) 2008 Fabrice Decroix <fabrice.decroix@gmail.com>
# Copyright (C) 2008 Yannick Martel <yannick.martel@gmail.com>
# Copyright (C) 2008-2009 Dumont Sébastien <sebastien.dumont@itaapy.com>
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

# Import from itools
from itools.core import freeze

# Internal import
from utils import font_value, format_size, get_color_as_hexa
from utils import get_color, get_int_value

# Import from reportlab
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus.frames import ShowBoundaryValue


P_ALIGNMENTS = {'left': TA_LEFT, 'right': TA_RIGHT, 'center': TA_CENTER,
              'justify': TA_JUSTIFY}
TAB_V_ALIGN = ('top', 'middle', 'bottom')
TAB_H_ALIGN = {'left': 'LEFT', 'right': 'RIGHT', 'center': 'CENTER',
               'justify': 'LEFT'}

H_ALIGN = ('left', 'right', 'center')
V_ALIGN = ('top', 'middle', 'bottom')

HEADING = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')

P_PADDINGS = {'padding-top' : 'spaceBefore', 'padding-bottom': 'spaceAfter',
              'padding-left': 'leftIndent', 'padding-right': 'rightIndent'}

TABLE_PADDINGS = { 'padding-top':'TOPPADDING',
                   'padding-bottom': 'BOTTOMPADDING',
                   'padding-left': 'LEFTPADDING',
                   'padding-right': 'RIGHTPADDING'}

FRAME_PADDINGS = {'padding-top': 'topPadding',
                  'padding-bottom': 'bottomPadding',
                  'padding-left': 'leftPadding',
                  'padding-right': 'rightPadding'}

BODY_MARGINS = {'margin-top': 'topMargin',
                'margin-bottom': 'bottomMargin',
                'margin-left': 'leftMargin',
                'margin-right': 'rightMargin'}



def table_get_align(attributes):
    attrs = {}
    hAlign = attributes.get((None, 'align'), None)
    if hAlign in H_ALIGN:
        attrs['hAlign'] = hAlign.upper()
    vAlign = attributes.get((None, 'valign'), None)
    if vAlign in V_ALIGN:
        attrs['vAlign'] = vAlign.upper()
    return attrs


def table_get_margin(style_css):
    """Calculate and return top and bottom margin"""
    margin_top = margin_bottom = None, None
    for key, value in style_css.iteritems():
        if key == 'margin-top':
            margin_top = format_size(value, None)
        elif key == 'margin-bottom':
            margin_bottom = format_size(value, None)

    return margin_top, margin_bottom


def attribute_style_to_dict(value):
    """Build a dictionary from a HTML "style" attribute string
    INPUT: background: red; color: green;
    OUTPUT: {'background': 'red', 'color': 'green'}"""

    css = {}
    for data in value.split(';'):
        if not data:
            continue
        try:
            key, value = data.split(':')
        except ValueError:
            continue
        css[key.strip()] = value.strip()
    return css



#######################################################################
# FONT
#######################################################################
FONT_NAME = {'monospace': 'Courier', 'times-new-roman': 'Times-Roman',
             'arial': 'Helvetica', 'serif': 'Times',
             'sans-serif': 'Helvetica', 'helvetica': 'Helvetica',
             'symbol': 'Symbol',
             'stsong-light': 'STSong-Light', # cn
             'heiseimin-w3': 'HeiseiMin-W3', # jp
             'hysmyeongjo-medium': 'HYSMyeongJo-Medium' # kr
             }

def get_font_name(search_name, default='helvetica'):
    # Maximize the possibility to match the font name
    name = search_name.lower()
    if name in FONT_NAME:
        return FONT_NAME.get(name)
    elif default and default in FONT_NAME:
        # FIXME The default fontname must be pick up from the CSS
        return FONT_NAME.get(default)
    # Fallback to the serif font name
    return FONT_NAME.get('serif')


def p_border_style(key, value):
    style_attrs = {}
    if key == 'border':
        tab = value.split()
        for element in tab:
            size = format_size(element, None)
            if size is not None:
                style_attrs['borderWidth'] = size
                continue
            color = get_color_as_hexa(element, None)
            if color is not None:
                style_attrs['borderColor'] = color
                continue
    elif key == 'border-bottom':
        tab = value.split()
        for element in tab:
            size = format_size(element, None)
            if size is not None:
                style_attrs['borderWidth'] = size
                continue
            color = get_color_as_hexa(element, None)
            if color is not None:
                style_attrs['borderColor'] = color
                continue
    elif key == 'border-color':
        color = get_color_as_hexa(value, None)
        if color is not None:
            style_attrs['borderColor'] = color
    elif key == 'border-width':
        size = format_size(value, None)
        if size is not None:
            style_attrs['borderWidth'] = size
    return style_attrs


def table_border_style(border, start, stop):
    width = border.get('borderWidth', None)
    if width is not None and width >= 0:
        color = get_color(border.get('borderColor', 'grey'))
        return [('GRID', start, stop, width, color)]
    return []


def inline_color_style(key, value, context):
    style = None
    if key == 'color':
        style = ('span', {(None, key): get_color_as_hexa(value)})
    elif key in ('background-color'):
        style = ('span', {(None, 'backColor'): get_color_as_hexa(value)})
    return style


def inline_text_style(key, value, context):
    style = None
    if key == 'text-decoration':
        if value == 'underline':
            style = ('u', {})
    return style


def inline_font_style(key, value, context):
    style = None
    if key == 'font-family':
        style = ('span', {(None, 'fontName'): get_font_name(value)})
    elif key == 'font-style':
        if value in ('italic', 'oblique'):
            style = ('i', {})
        elif value != 'normal':
            print '(WW) font-style not valid'
    elif key == 'font-size':
        style = ('span', {(None, 'fontSize'): font_value(value)})
    elif key == 'font-weight':
        if len(value):
            if value[0].isalpha() and value in ('bold', 'bolder'):
                style = ('b', {})
            elif not get_int_value(value, 400) < 700:
                style = ('b', {})
    return style


def p_font_style(key, value, context):
    style_attr = {}
    if key == 'font-family':
        style_attr['fontName'] = get_font_name(value)
    elif key == 'font-style':
        if value in ('italic', 'oblique'):
            context.style_tag_stack.append(('i'))
        elif value != 'normal':
            print '(WW) font-style not valid'
    elif key == 'font-size':
        style_attr['fontSize'] = font_value(value)
    elif key == 'font-weight':
        if len(value):
            if value[0].isalpha() and value in ('bold', 'bolder'):
                context.style_tag_stack.append(('b'))
            elif not get_int_value(value, 400) < 700:
                context.style_tag_stack.append(('b'))
    return style_attr


def p_padding_style(key, value):
    style_attr = {}
    size = format_size(value, None)
    if size is not None:
        if key == 'padding':
            for padding in P_PADDINGS.values():
                style_attr[padding] = size
        elif key in P_PADDINGS.keys():
            style_attr[P_PADDINGS[key]] = size
    return style_attr


def table_padding_style(key, value, start, stop):
    """Calculate the Reportlab padding from the html one
    Note that only the padding-X attributes are allowed"""
    style = []
    size = format_size(value, None)
    if size is not None:
        if key in TABLE_PADDINGS.keys():
            style.append((TABLE_PADDINGS[key], start, stop, size))
    return style


def table_bg_style(key, value, start, stop):
    style = []
    if key == 'background-color':
        color = get_color(value)
        style.append(('BACKGROUND', start, stop, color))
    return style


def table_align_style(key, value, start, stop):
    style = []
    if key == 'vertical-align':
        if value in TAB_V_ALIGN:
            style.append(('VALIGN', start, stop, value.upper()))
    elif key == 'text-align':
        val = TAB_H_ALIGN.get(value, 'LEFT')
        style.append(('ALIGN', start, stop, val))
    return style


def build_paragraph_style(context, element, style_css):
    style_attr = {}
    # The default style is Normal
    parent_style_name = 'Normal'
    bulletText = None

    style_attr['autoLeading'] = 'max'
    style_attr['borderPadding'] = 0.1 * cm # TODO Check if it's correct
    style_attr['leading'] = 0.3 * cm

    #FIXME must be moved in default css
    style_attr['spaceBefore'] = 0.3 * cm
    style_attr['spaceAfter'] = 0.3 * cm
    # Leading
    leading_forced = False
    font_size = None

    for key, value in style_css.iteritems():
        if key == 'color':
            style_attr['textColor'] = get_color_as_hexa(value)
        elif key in ('background-color'):
            style_attr['backColor'] = get_color_as_hexa(value)
        elif key == 'text-indent':
            style_attr['firstLineIndent'] = format_size(value)
        elif key == 'text-align':
            if value in P_ALIGNMENTS.keys():
                style_attr['alignment'] = P_ALIGNMENTS.get(value)
        elif key == 'text-decoration':
            if value == 'underline':
                context.style_tag_stack.append(('u'))
        elif element[0] not in ('td', 'th') and key.startswith('border'):
            style_attr.update(p_border_style(key, value))
        elif key.startswith('font'):
            font_style = p_font_style(key, value, context)
            if 'fontSize' in font_style:
                font_size = font_style['fontSize']
            style_attr.update(font_style)
        elif key.startswith('padding'):
            style_attr.update(p_padding_style(key, value))
        elif key.startswith('line-height'):
            leading_forced = True
            style_attr['leading'] = format_size(value)
        elif key == 'width':
            style_attr['width'] = value
        elif key == 'float':
            style_attr['float'] = value
        elif key == 'text-transform':
            if value in ('uppercase', 'lowercase'):
                style_attr['textTransform'] = value


    # Overload the attributes values
    for key, attr_value in element[1].iteritems():
        key = key[1] # (None, key)
        if key == 'class':
            # Set the parent style for inheritance
            parent_style_name = attr_value
        elif key == 'bulletText':
            bulletText = attr_value
        elif key == 'style':
            # TODO parse inline style attribute
            continue

    if element[0] in HEADING + ('toctitle', ):
        parent_style_name = element[0]
    style_name = parent_style_name
    parent_style = context.get_style(parent_style_name)

    # Calulate the leading
    if leading_forced is False and font_size:
        # Reportlab UserGuide
        # a good rule of thumb is to make this 20% larger than the point size
        # But we choose to use a ratio of 33%
        style_attr['leading'] = font_size * 1.33

    return (ParagraphStyle(style_name, parent=parent_style, **style_attr),
            bulletText)


def build_inline_style(context, tag_name, style_css):
    style = {}
    for key, value in style_css.iteritems():
        if key.endswith('color'):
            tag_and_attrs = inline_color_style(key, value, context)
        elif key.startswith('font'):
            tag_and_attrs = inline_font_style(key, value, context)
        elif key.startswith('text'):
            tag_and_attrs = inline_text_style(key, value, context)
        else:
            continue
        if tag_and_attrs:
            tag, attrs = tag_and_attrs
            if tag in style:
                style[tag].update(attrs)
            else:
                style[tag] = attrs
    for tag, attrs in style.iteritems():
        context.tag_stack[0].append((tag, attrs))


def frame_padding_style(key, value):
    style_attr = {}
    size = format_size(value, None)
    if size is not None:
        if key == 'padding':
            for padding in FRAME_PADDINGS.values():
                style_attr[padding] = size
        elif key in FRAME_PADDINGS.keys():
            style_attr[FRAME_PADDINGS[key]] = size
    return style_attr


def body_margin_style(key, value):
    style_attr = {}
    size = format_size(value, None)
    if size is not None:
        if key == 'margin':
            for margin in BODY_MARGINS.values():
                style_attr[margin] = size
        elif key in BODY_MARGINS.keys():
            style_attr[BODY_MARGINS[key]] = size
    return style_attr


def build_frame_style(context, style_css, inline_attributes=freeze({})):
    frame_attr = {}
    border = {}

    keys = style_css.keys()
    keys.sort()
    # revert keys to avoid css inheritance
    for key in keys:
        value = style_css[key]
        if key.startswith('border'):
            border.update(p_border_style(key, value))
        if key in ('height', 'width'):
            frame_attr[key] = value
        elif key.startswith('padding'):
            frame_attr.update(frame_padding_style(key, value))
        elif key.startswith('margin'):
            frame_attr.update(body_margin_style(key, value))

    if border:
        sb = ShowBoundaryValue(get_color(border.get('borderColor', 'black')),
                               border.get('borderWidth', 1))
        frame_attr['showBoundary'] = sb
    return frame_attr


def compute_border_style(value):
    border_value = value.strip().lower()
    dash = None
    if border_value == 'solid':
        dash = None
    elif border_value == 'dashed':
        dash = [5, 5]
    elif border_value == 'dotted':
        dash = [2, 2]
    return dash


def _calculate_table_border(value):
    """INPUT border: 1px solid red
    Calculate the 3 attributes
    width, style, color"""
    css_value = value.strip()
    if css_value.endswith(';'):
        css_value = css_value[:-1]
    values = value.split()
    if len(values) == 3:
        # 1px solid red
        width, style, color = values
        width = format_size(width, 1)
        style = compute_border_style(style)
        color = get_color_as_hexa(color)
    else:
        # Not well formed
        return None

    return (width, style, color)


def _compute_table_border_full(value):
    values = _calculate_table_border(value)
    if values is None:
        return None
    width, style, color = values
    return {# top
            'border-top-color': color,
            'border-top-width': width,
            'border-top-style': style,
            # right
            'border-right-color': color,
            'border-right-width': width,
            'border-right-style': style,
            # bottom
            'border-bottom-color': color,
            'border-bottom-width': width,
            'border-bottom-style': style,
            # left
            'border-left-color': color,
            'border-left-width': width,
            'border-left-style': style,
            }


def compute_table_border(key, value):
    """Key is one of these values
    border
    border-XXX-width
    border-XXX-style
    border-XXX-color
    width XXX equals to top, right, bottom, left

    with border equals to
    border-top + border-right + border-bottom + border-left
    """

    if key == 'border':
        # explode the key in sub key
        # border-top
        # border-right
        # border-bottom
        # border-left
        return _compute_table_border_full(value)
    elif key in ('border-top-width',
                 'border-right-width',
                 'border-bottom-width',
                 'border-left-width'):
        return {key: format_size(value, 1)}
    elif key in ('border-top-style',
                 'border-right-style',
                 'border-bottom-style',
                 'border-left-style'):
        return {key: compute_border_style(value)}
    elif key in ('border-top-color',
                 'border-right-color',
                 'border-bottom-color',
                 'border-left-color'):
        return {key: get_color_as_hexa(value)}
    return None


def table_css_border_to_rl_table_style(style, start, stop):
    buffer = {}
    map = {'border-top': 'LINEABOVE',
           'border-right': 'LINEAFTER',
           'border-bottom': 'LINEBELOW',
           'border-left': 'LINEBEFORE'}

    for key, value in style.iteritems():
        start_key = key.rsplit('-', 1)[0]
        rl_key = map.get(start_key, None)
        if rl_key is None:
            continue
        # width, color
        buffer.setdefault(rl_key, [-1, -1])
        if key.endswith('width'):
            buffer[rl_key][0] = value
        elif key.endswith('color'):
            buffer[rl_key][1] = value
        # DASHED TODO

    table_style = []
    for key, value in buffer.iteritems():
        width, color = value
        if width == 0:
            continue
        table_style.append((key, start, stop, width, color))

    return table_style



def _get_table_style(style_css, start, stop):
    table_style = []
    for key, value in style_css.iteritems():
        if key.startswith('padding'):
            table_style.extend(table_padding_style(key, value, start, stop))
        elif key.startswith('background'):
            table_style.extend(table_bg_style(key, value, start, stop))
        elif key.endswith('align'):
            table_style.extend(table_align_style(key, value, start, stop))
        elif key == 'font-family':
            rl_value = get_font_name(value)
            table_style.extend([('FONT', start, stop, rl_value)])
        elif key == 'line-height':
            rl_value = format_size(value)
            table_style.extend([('LEADING', start, stop, rl_value)])

    return table_style


def _get_table_style_border_only(style_css, start, stop):
    border = {}
    for key, value in style_css.iteritems():
        if key.startswith('border'):
            border_value = compute_table_border(key, value)
            if border_value:
                border[key] = border_value
    return border


def get_table_style(style_css, attributes, start, stop):
    table_style = []
    # bufferize the border
    border_css_buffer = {}
    border_css = {}

    table_style = _get_table_style(style_css, start, stop)
    border_css_buffer = _get_table_style_border_only(style_css, start, stop)

    for key1, value in attributes.iteritems():
        key1 = key1[1]
        if key1 == 'style':
            style_css2 = attribute_style_to_dict(value)
            table_style.extend(_get_table_style(style_css, start, stop))
            border_css_buffer.update(_get_table_style_border_only(style_css2,
                                                                  start, stop))

    keys = border_css_buffer.keys()
    keys.sort()
    # revert keys to avoid css inheritance
    for key in keys:
        border_css.update(border_css_buffer[key])
    table_style.extend(table_css_border_to_rl_table_style(border_css, start,
                                                          stop))

    return table_style


def get_hr_style_from_css(css):
    available_css_attrs = ('width', 'border-width', 'color', 'margin-top',
                           'margin-bottom', 'float', 'border-style')
    float_mapping = {'left': 'LEFT', 'right': 'RIGTH', 'none': 'CENTER'}

    attrs = {}
    for key, value in css.iteritems():
        if key in available_css_attrs:
            if key  == 'width':
                attrs['width'] = format_size(value)
            elif key == 'border-width':
                attrs['thickness'] = format_size(value)
            elif key == 'color':
                attrs['color'] = get_color(value)
            elif key == 'margin-top':
                attr_value = format_size(value)
                if attr_value is not None:
                    attrs['spaceBefore'] = attr_value
            elif key == 'margin-bottom':
                attr_value = format_size(value)
                if attr_value is not None:
                    attrs['spaceAfter'] = attr_value
            elif key == 'float':
                attrs['hAlign'] = float_mapping.get(value, 'CENTER')
            elif key == 'border-style':
                dash = None
                if value == 'solid':
                    dash = None
                elif value == 'dashed':
                    dash = [5, 5]
                elif value == 'dotted':
                    dash = [2, 2]
                attrs['dash'] = dash

    return attrs


def get_hr_style(style_css, attributes):
    """Build Reportlab HR style from CSS properties

    available properties are
    CSS                 Reportlab
    --------------------------------
    - width             width
    - border-width      thickness
    - color             color
    - margin-top        spaceBefore
    - margin-bottom     spaceAfter
    - float             hAlign
    - border-style      dash

    TODO
    Reportlab attribute vAlign
    """

    # CSS
    attrs = get_hr_style_from_css(style_css)
    # Overload with local attributes
    # TODO

    if 'width' not in attrs:
        attrs['width'] = '100%'

    return attrs


def makeTocHeaderStyle(level, delta, epsilon, fontName='Times-Roman'):
    """
        Make a header style for different levels.
    """

    assert level >= 0, "Level must be >= 0."

    PS = ParagraphStyle
    size = 12
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0,
               firstLineIndent = -epsilon,
               leftIndent = level*delta + epsilon)

    return style


# This map of functions is defined here
# to avoid definition's problems
ATTR_TO_STYLE = {'cellpadding': (table_padding_style, 'padding'),
                 'bgcolor': (table_bg_style, 'background-color')}
