# -*- coding: utf-8 -*-
"""
Importation de fichiers KMZ
"""

import zipfile
import xml.etree.ElementTree as ET
import tempfile
import os
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsGeometry, QgsPoint,
    QgsFeature, QgsFields, QgsField
)
from qgis.PyQt.QtCore import QVariant


class KMZImporter:
    def __init__(self):
        self.points_layer = None
        self.lines_layer = None
        self.polygons_layer = None

    def import_kmz(self, kmz_path):
        result = {
            'points_count': 0,
            'lines_count': 0,
            'polygons_count': 0,
            'kml_content': None
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            kml_file = None
            for file in os.listdir(temp_dir):
                if file.endswith('.kml'):
                    kml_file = os.path.join(temp_dir, file)
                    break

            if not kml_file:
                raise Exception('Aucun fichier KML trouvé dans l\'archive')

            tree = ET.parse(kml_file)
            root = tree.getroot()

            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            placemarks = root.findall('.//kml:Placemark', ns)

            self.points_layer = QgsVectorLayer('Point', 'Points FTTH', 'memory')
            self.lines_layer = QgsVectorLayer('LineString', 'Câbles FTTH', 'memory')
            self.polygons_layer = QgsVectorLayer('Polygon', 'Zones', 'memory')

            for layer in [self.points_layer, self.lines_layer, self.polygons_layer]:
                layer.dataProvider().addAttributes([
                    QgsField('name', QVariant.String),
                    QgsField('description', QVariant.String),
                    QgsField('type', QVariant.String),
                ])
                layer.updateFields()

            for placemark in placemarks:
                name = placemark.findtext('kml:name', '', ns)
                description = placemark.findtext('kml:description', '', ns)

                point = placemark.find('kml:Point', ns)
                if point is not None:
                    coords = point.findtext('kml:coordinates', '', ns)
                    if coords:
                        coords = coords.strip().split(',')
                        if len(coords) >= 2:
                            feature = QgsFeature()
                            feature.setGeometry(QgsGeometry.fromPointXY(
                                QgsPoint(float(coords[0]), float(coords[1]))
                            ))
                            feature.setAttributes([name, description, 'POINT'])
                            self.points_layer.dataProvider().addFeature(feature)
                            result['points_count'] += 1

                linestring = placemark.find('kml:LineString', ns)
                if linestring is not None:
                    coords_text = linestring.findtext('kml:coordinates', '', ns)
                    if coords_text:
                        coords_list = []
                        for coord in coords_text.strip().split():
                            parts = coord.split(',')
                            if len(parts) >= 2:
                                coords_list.append(QgsPoint(float(parts[0]), float(parts[1])))

                        if len(coords_list) >= 2:
                            feature = QgsFeature()
                            feature.setGeometry(QgsGeometry.fromPolylineXY(coords_list))
                            feature.setAttributes([name, description, 'LIGNE'])
                            self.lines_layer.dataProvider().addFeature(feature)
                            result['lines_count'] += 1

                polygon = placemark.find('kml:Polygon', ns)
                if polygon is not None:
                    outer_boundary = polygon.find('kml:outerBoundaryIs', ns)
                    if outer_boundary is not None:
                        ring = outer_boundary.find('kml:LinearRing', ns)
                        if ring is not None:
                            coords_text = ring.findtext('kml:coordinates', '', ns)
                            if coords_text:
                                coords_list = []
                                for coord in coords_text.strip().split():
                                    parts = coord.split(',')
                                    if len(parts) >= 2:
                                        coords_list.append(QgsPoint(float(parts[0]), float(parts[1])))

                                if len(coords_list) >= 3:
                                    feature = QgsFeature()
                                    feature.setGeometry(QgsGeometry.fromPolygonXY([coords_list]))
                                    feature.setAttributes([name, description, 'POLYGON'])
                                    self.polygons_layer.dataProvider().addFeature(feature)
                                    result['polygons_count'] += 1

            QgsProject.instance().addMapLayer(self.points_layer)
            QgsProject.instance().addMapLayer(self.lines_layer)
            QgsProject.instance().addMapLayer(self.polygons_layer)

            result['kml_content'] = {
                'points_layer': self.points_layer,
                'lines_layer': self.lines_layer,
                'polygons_layer': self.polygons_layer
            }

        return result
