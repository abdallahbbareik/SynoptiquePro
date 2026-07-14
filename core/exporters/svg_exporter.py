# -*- coding: utf-8 -*-
"""
Exportation en SVG
"""

import xml.etree.ElementTree as ET
import os


class SVGExporter:
    def __init__(self):
        self.width = 1200
        self.height = 800
        self.x_offset = 50
        self.y_offset = 50
        self.level_height = 150
        self.element_width = 120
        self.element_height = 50

    def export(self, synoptique_data, output_path):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': str(self.width),
            'height': str(self.height),
            'viewBox': f'0 0 {self.width} {self.height}'
        })

        style = ET.SubElement(svg, 'defs')
        style_text = '''<style>
            .element-box { fill: #e8f4f8; stroke: #1f77b4; stroke-width: 2; }
            .element-text { font-family: Arial; font-size: 12px; text-anchor: middle; }
            .connection-line { stroke: #666; stroke-width: 2; fill: none; }
            .title { font-family: Arial; font-size: 20px; font-weight: bold; }
        </style>'''
        style.text = style_text

        title = ET.SubElement(svg, 'text', {
            'x': str(self.width // 2),
            'y': '30',
            'class': 'title',
            'text-anchor': 'middle'
        })
        title.text = 'Synoptique FTTH'

        tree = synoptique_data.get('tree', {})
        y = self.y_offset + 100

        x_counter = 0
        for root_id, root_node in tree.items():
            x = self.x_offset + x_counter * (self.element_width + 50)
            self._draw_node(svg, root_node, x, y, 0)
            x_counter += 1

        tree_str = ET.tostring(svg, encoding='unicode')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tree_str)

    def _draw_node(self, svg, node, x, y, level):
        rect = ET.SubElement(svg, 'rect', {
            'x': str(x - self.element_width // 2),
            'y': str(y),
            'width': str(self.element_width),
            'height': str(self.element_height),
            'class': 'element-box'
        })

        text = ET.SubElement(svg, 'text', {
            'x': str(x),
            'y': str(y + self.element_height // 2 + 5),
            'class': 'element-text'
        })
        text.text = node['name'][:15]

        children = node.get('children', [])
        if children:
            child_y = y + self.level_height
            total_width = len(children) * (self.element_width + 50)
            start_x = x - total_width // 2

            for i, child in enumerate(children):
                child_x = start_x + i * (self.element_width + 50) + self.element_width // 2

                line = ET.SubElement(svg, 'line', {
                    'x1': str(x),
                    'y1': str(y + self.element_height),
                    'x2': str(child_x),
                    'y2': str(child_y),
                    'class': 'connection-line'
                })

                self._draw_node(svg, child, child_x, child_y, level + 1)
