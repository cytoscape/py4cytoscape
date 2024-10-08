# -*- coding:utf-8 -*-

""" Visual Property enumeration and classification
"""

"""Copyright 2020-2022 The Cytoscape Consortium

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

NODE_COLOR_PROPERTIES = {'NODE_FILL_COLOR', 'NODE_LABEL_COLOR', 'NODE_BORDER_PAINT', 'NODE_SELECTED_PAINT'}
NODE_DIMENSION_PROPERTIES = {'NODE_SIZE': 'size', 'NODE_WIDTH': 'width', 'NODE_HEIGHT': 'height',
                             'NODE_LABEL_FONT_SIZE': 'size', 'NODE_BORDER_WIDTH': 'size'}
NODE_OPACITY_PROPERTIES = {'NODE_TRANSPARENCY', 'NODE_BORDER_TRANSPARENCY', 'NODE_LABEL_TRANSPARENCY'}
NODE_SHAPE_PROPERTIES = {'NODE_SHAPE'}
NODE_TOOLTIP_PROPERTIES = {'NODE_TOOLTIP'}
NODE_FONT_FACE_PROPERTIES = {'NODE_LABEL_FONT_FACE'}
NODE_LABEL_PROPERTIES = {'NODE_LABEL'}
NODE_VISIBLE_PROPERTIES = {'NODE_VISIBLE'}
NODE_CUSTOM_GRAPHICS_PROPERTIES = {'NODE_CUSTOMGRAPHICS_1', 'NODE_CUSTOMGRAPHICS_2', 'NODE_CUSTOMGRAPHICS_3',
                                   'NODE_CUSTOMGRAPHICS_4', 'NODE_CUSTOMGRAPHICS_5', 'NODE_CUSTOMGRAPHICS_6',
                                   'NODE_CUSTOMGRAPHICS_7', 'NODE_CUSTOMGRAPHICS_8', 'NODE_CUSTOMGRAPHICS_9'}
NODE_CUSTOM_GRAPHICS_POSITION_PROPERTIES = {'NODE_CUSTOMGRAPHICS_POSITION_1', 'NODE_CUSTOMGRAPHICS_POSITION_2',
                                            'NODE_CUSTOMGRAPHICS_POSITION_3', 'NODE_CUSTOMGRAPHICS_POSITION_4',
                                            'NODE_CUSTOMGRAPHICS_POSITION_5', 'NODE_CUSTOMGRAPHICS_POSITION_6',
                                            'NODE_CUSTOMGRAPHICS_POSITION_7', 'NODE_CUSTOMGRAPHICS_POSITION_8',
                                            'NODE_CUSTOMGRAPHICS_POSITION_9'}

EDGE_COLOR_PROPERTIES = {'EDGE_UNSELECTED_PAINT', 'EDGE_STROKE_UNSELECTED_PAINT', 'EDGE_LABEL_COLOR',
                         'EDGE_SELECTED_PAINT', 'EDGE_STROKE_SELECTED_PAINT',
                         'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', 'EDGE_TARGET_ARROW_UNSELECTED_PAINT'}
EDGE_DIMENSION_PROPERTIES = {'EDGE_LABEL_FONT_SIZE': 'size', 'EDGE_WIDTH': 'width'}
EDGE_OPACITY_PROPERTIES = {'EDGE_LABEL_TRANSPARENCY', 'EDGE_TRANSPARENCY'}
EDGE_LINE_STYLE_PROPERTIES = {'EDGE_LINE_TYPE'}
EDGE_ARROW_STYLE_PROPERTIES = {'EDGE_SOURCE_ARROW_SHAPE', 'EDGE_TARGET_ARROW_SHAPE'}
EDGE_TOOLTIP_PROPERTIES = {'EDGE_TOOLTIP'}
EDGE_FONT_FACE_PROPERTIES = {'EDGE_LABEL_FONT_FACE'}
EDGE_LABEL_PROPERTIES = {'EDGE_LABEL'}
EDGE_VISIBLE_PROPERTIES = {'EDGE_VISIBLE'}

NETWORK_COLOR_PROPERTIES = {'NETWORK_BACKGROUND_PAINT'}

COLOR_PROPERTIES = NODE_COLOR_PROPERTIES | EDGE_COLOR_PROPERTIES | NETWORK_COLOR_PROPERTIES
DIMENSION_PROPERTIES = {**NODE_DIMENSION_PROPERTIES, **EDGE_DIMENSION_PROPERTIES}
OPACITY_PROPERTIES = NODE_OPACITY_PROPERTIES | EDGE_OPACITY_PROPERTIES
SHAPE_PROPERTIES = NODE_SHAPE_PROPERTIES
LINE_STYLE_PROPERTIES = EDGE_LINE_STYLE_PROPERTIES
ARROW_STYLE_PROPERTIES = EDGE_ARROW_STYLE_PROPERTIES
TOOLTIP_PROPERTIES = NODE_TOOLTIP_PROPERTIES | EDGE_TOOLTIP_PROPERTIES
LABEL_PROPERTIES = NODE_LABEL_PROPERTIES | EDGE_LABEL_PROPERTIES
FONT_FACE_PROPERTIES = NODE_FONT_FACE_PROPERTIES | EDGE_FONT_FACE_PROPERTIES
VISIBLE_PROPERTIES = NODE_VISIBLE_PROPERTIES | EDGE_VISIBLE_PROPERTIES
CUSTOM_GRAPHICS_PROPERTIES = NODE_CUSTOM_GRAPHICS_PROPERTIES | NODE_CUSTOM_GRAPHICS_POSITION_PROPERTIES

PROPERTY_NAME_MAP = {'EDGE_COLOR': 'EDGE_UNSELECTED_PAINT',
                     'EDGE_THICKNESS': 'EDGE_WIDTH',
                     'NODE_BORDER_COLOR': 'NODE_BORDER_PAINT',
                     'NODE_BORDER_LINE_TYPE': 'NODE_BORDER_STROKE'}
