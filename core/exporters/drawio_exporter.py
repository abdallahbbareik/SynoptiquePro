# -*- coding: utf-8 -*-
"""
Exportation en Draw.io
"""

import xml.etree.ElementTree as ET
import os


class DrawIOExporter:
    def __init__(self):
        self.cell_width = 120
        self.cell_height = 50
        self.level_height = 150
        self.colors = {
            'NRO': '#FF6B6B',
            'PM': '#4ECDC4',
            'PBO': '#45B7D1',
            'CHAMBRE': '#FFA07A',
            'CLIENT': '#90EE90',
            'POTEAU': '#D3D3D3',
            'ELEMENT': '#E0E0E0'
        }

    def export(self, synoptique_data, output_path):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        mxfile = ET.Element('mxfile', {
            'host': 'app.diagrams.net',
            'modified': 'now',
            'agent': 'SynoptiquePro',
            'etag': 'none',
            'version': '1.0.0',
            'type': 'device'
        })

        diagram = ET.SubElement(mxfile, 'diagram', {'id': 'Page-1', 'name': 'Synoptique'})
        mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')

        root = ET.SubElement(mxGraphModel, 'root')
        mxCell = ET.SubElement(root, 'mxCell', {'id': '0'})
        mxCell = ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

        tree = synoptique_data.get('tree', {})
        cell_id = 2
        y_position = 50
        x_position = 50

        for root_id, root_node in tree.items():
            cell_id = self._add_node_to_drawio(root, root_node, cell_id, x_position, y_position, 0)
            y_position += self.level_height * (self._get_tree_depth(root_node) + 1) + 50

        tree_str = ET.tostring(mxfile, encoding='unicode')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(tree_str)

    def _add_node_to_drawio(self, parent, node, cell_id, x, y, level):
        node_type = node.get('type', 'ELEMENT')
        color = self.colors.get(node_type, '#E0E0E0')

        parent_cell = ET.SubElement(parent, 'mxCell', {
            'id': str(cell_id),
            'value': node['name'],
            'style': f'rounded=1;whiteSpace=wrap;html=1;fillColor={color};fontColor=#000000;fontSize=12;fontStyle=1;',
            'vertex': '1',
            'parent': '1'
        })

        geometry = ET.SubElement(parent_cell, 'mxGeometry', {
            'x': str(x),
            'y': str(y),
            'width': str(self.cell_width),
            'height': str(self.cell_height),
            'as': 'geometry'
        })

        cell_id += 1

        children = node.get('children', [])
        if children:
            child_y = y + self.level_height
            total_width = len(children) * (self.cell_width + 50)
            start_x = x - total_width // 2 + self.cell_width // 2

            for i, child in enumerate(children):
                child_x = start_x + i * (self.cell_width + 50)

                connector = ET.SubElement(parent, 'mxCell', {
                    'id': str(cell_id),
                    'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;',
                    'edge': '1',
                    'parent': '1',
                    'source': str(cell_id - 1),
                    'target': str(cell_id + 1)
                })

                edge_geometry = ET.SubElement(connector, 'mxGeometry', {
                    'relative': '1',
                    'as': 'geometry'
                })

                cell_id += 1

                cell_id = self._add_node_to_drawio(parent, child, cell_id, child_x, child_y, level + 1)

        return cell_id

    def _get_tree_depth(self, node):
        if not node.get('children'):
            return 0
        return 1 + max(self._get_tree_depth(child) for child in node['children'])
