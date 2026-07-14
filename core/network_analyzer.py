# -*- coding: utf-8 -*-
"""
Analyse topologique du réseau
"""

import networkx as nx
from qgis.core import QgsGeometry


class NetworkAnalyzer:
    def __init__(self):
        self.graph = None
        self.elements = {}
        self.paths = []

    def analyze_network(self, import_result, detect_elements=True, tolerance=5):
        self.graph = nx.MultiDiGraph()

        lines_layer = import_result['kml_content']['lines_layer']
        points_layer = import_result['kml_content']['points_layer']

        result = {
            'nodes_count': 0,
            'edges_count': 0,
            'elements_count': 0,
            'paths_count': 0,
            'graph': self.graph,
            'elements': {}
        }

        for feature in points_layer.getFeatures():
            geom = feature.geometry()
            point = geom.asPoint()
            node_id = f"point_{feature.id()}"
            self.graph.add_node(
                node_id,
                geometry=point,
                name=feature['name'],
                type=self._detect_element_type(feature['name']) if detect_elements else 'UNKNOWN'
            )
            result['nodes_count'] += 1

        for feature in lines_layer.getFeatures():
            geom = feature.geometry()
            polyline = geom.asPolyline()

            for i, point in enumerate(polyline):
                node_id = f"line_{feature.id()}_vertex_{i}"
                if node_id not in self.graph:
                    self.graph.add_node(node_id, geometry=point)
                    result['nodes_count'] += 1

                if i > 0:
                    prev_node_id = f"line_{feature.id()}_vertex_{i-1}"
                    self.graph.add_edge(
                        prev_node_id,
                        node_id,
                        name=feature['name'],
                        length=self._calculate_distance(polyline[i-1], point),
                        type=feature['type']
                    )
                    result['edges_count'] += 1

        if detect_elements:
            self.elements = self._detect_network_elements(points_layer)
            result['elements_count'] = len(self.elements)
            result['elements'] = self.elements

        self.paths = self._identify_paths()
        result['paths_count'] = len(self.paths)
        result['paths'] = self.paths

        return result

    def _detect_element_type(self, name):
        name_lower = name.lower()
        if 'nro' in name_lower:
            return 'NRO'
        elif 'pm' in name_lower:
            return 'PM'
        elif 'pbo' in name_lower:
            return 'PBO'
        elif 'chambre' in name_lower or 'ch' in name_lower:
            return 'CHAMBRE'
        elif 'client' in name_lower or 'usager' in name_lower:
            return 'CLIENT'
        elif 'potelet' in name_lower or 'poteau' in name_lower:
            return 'POTEAU'
        else:
            return 'ELEMENT'

    def _calculate_distance(self, point1, point2):
        import math
        dx = point2.x() - point1.x()
        dy = point2.y() - point1.y()
        return math.sqrt(dx*dx + dy*dy)

    def _detect_network_elements(self, points_layer):
        elements = {}
        for element_type in ['NRO', 'PM', 'PBO', 'CHAMBRE', 'CLIENT']:
            elements[element_type] = []

        for feature in points_layer.getFeatures():
            element_type = self._detect_element_type(feature['name'])
            if element_type in elements:
                elements[element_type].append({
                    'id': feature.id(),
                    'name': feature['name'],
                    'geometry': feature.geometry().asPoint()
                })

        return elements

    def _identify_paths(self):
        paths = []
        nro_nodes = [node for node, attr in self.graph.nodes(data=True)
                     if attr.get('type') == 'NRO']

        for nro in nro_nodes:
            descendants = nx.descendants(self.graph, nro)
            path = {
                'start': nro,
                'nodes': list(descendants),
                'total_length': self._calculate_path_length(nro, descendants)
            }
            paths.append(path)

        return paths

    def _calculate_path_length(self, start_node, nodes):
        total_length = 0
        for edge in self.graph.edges(data=True):
            if edge[0] == start_node or edge[0] in nodes:
                total_length += edge[2].get('length', 0)
        return total_length
