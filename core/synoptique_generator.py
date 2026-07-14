# -*- coding: utf-8 -*-
"""
Générateur de synoptique
"""

import networkx as nx


class SynoptiqueGenerator:
    def __init__(self):
        self.synoptique = None
        self.tree_structure = None

    def generate(self, graph, style='Arborescent', show_distances=True, show_fiber_count=True):
        self.tree_structure = self._build_tree_structure(graph)

        result = {
            'style': style,
            'show_distances': show_distances,
            'show_fiber_count': show_fiber_count,
            'levels': len(self.tree_structure),
            'elements_count': self._count_elements(self.tree_structure),
            'paths_count': len(self.tree_structure),
            'tree': self.tree_structure,
            'ascii_representation': self._generate_ascii_tree(self.tree_structure)
        }

        return result

    def _build_tree_structure(self, graph):
        tree = {}

        root_nodes = [node for node, attr in graph.nodes(data=True)
                      if attr.get('type') == 'NRO']

        if not root_nodes:
            root_nodes = [list(graph.nodes())[0]]

        for root in root_nodes:
            tree[root] = self._traverse_tree(graph, root, set())

        return tree

    def _traverse_tree(self, graph, node, visited):
        if node in visited:
            return None

        visited.add(node)

        node_data = graph.nodes[node]
        children = []

        for successor in graph.successors(node):
            if successor not in visited:
                child = self._traverse_tree(graph, successor, visited.copy())
                if child:
                    children.append(child)

        return {
            'id': node,
            'name': node_data.get('name', node),
            'type': node_data.get('type', 'UNKNOWN'),
            'children': children,
            'geometry': node_data.get('geometry')
        }

    def _count_elements(self, tree_structure):
        count = 0
        for key, value in tree_structure.items():
            count += self._count_node_children(value) + 1
        return count

    def _count_node_children(self, node):
        count = len(node.get('children', []))
        for child in node.get('children', []):
            count += self._count_node_children(child)
        return count

    def _generate_ascii_tree(self, tree_structure):
        lines = []
        for root_id, root_node in tree_structure.items():
            lines.append(root_node['name'])
            lines.extend(self._generate_ascii_lines(root_node, ''))
        return '\n'.join(lines)

    def _generate_ascii_lines(self, node, prefix):
        lines = []
        children = node.get('children', [])

        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            connector = '└── ' if is_last else '├── '
            lines.append(f'{prefix}{connector}{child["name"]}')

            extension = '    ' if is_last else '│   '
            lines.extend(self._generate_ascii_lines(child, prefix + extension))

        return lines
