# -*- coding: utf-8 -*-
"""
Importation de fichiers géospatiaux multiples formats
Supports: KMZ, KML, SHP, GeoJSON, GML, DXF, etc.
"""

import zipfile
import xml.etree.ElementTree as ET
import tempfile
import os
import json
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsGeometry, QgsPointXY,
    QgsFeature, QgsFields, QgsField
)
from qgis.PyQt.QtCore import QVariant


class MultiFormatImporter:
    """Importateur universel pour multiples formats géospatiaux"""
    
    SUPPORTED_FORMATS = {
        '.kmz': 'KMZ (Google Earth)',
        '.kml': 'KML (Keyhole Markup Language)',
        '.shp': 'Shapefile',
        '.geojson': 'GeoJSON',
        '.json': 'JSON',
        '.gml': 'GML (Geography Markup Language)',
        '.dxf': 'DXF (AutoCAD)',
        '.gpx': 'GPX (GPS Exchange Format)',
        '.csv': 'CSV (Comma Separated Values)',
    }

    def __init__(self):
        self.points_layer = None
        self.lines_layer = None
        self.polygons_layer = None
        self.import_result = None

    def get_supported_formats(self):
        """Retourne la liste des formats supportés"""
        return self.SUPPORTED_FORMATS

    def import_file(self, file_path):
        """
        Importe un fichier géospatial (format automatiquement détecté)
        """
        if not os.path.exists(file_path):
            raise Exception(f'Fichier non trouvé: {file_path}')

        file_ext = os.path.splitext(file_path)[1].lower()

        # Déterminer le format et importer
        if file_ext == '.kmz':
            return self.import_kmz(file_path)
        elif file_ext == '.kml':
            return self.import_kml(file_path)
        elif file_ext == '.shp':
            return self.import_shapefile(file_path)
        elif file_ext in ['.geojson', '.json']:
            return self.import_geojson(file_path)
        elif file_ext == '.gml':
            return self.import_gml(file_path)
        elif file_ext == '.gpx':
            return self.import_gpx(file_path)
        elif file_ext == '.dxf':
            return self.import_dxf(file_path)
        elif file_ext == '.csv':
            return self.import_csv(file_path)
        else:
            raise Exception(f'Format non supporté: {file_ext}')

    def import_kmz(self, kmz_path):
        """Importe un fichier KMZ (KML compressé)"""
        result = {
            'points_count': 0,
            'lines_count': 0,
            'polygons_count': 0,
            'kml_content': None,
            'format': 'KMZ'
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except Exception as e:
                raise Exception(f'Erreur lors de l\'extraction du KMZ: {e}')

            kml_file = None
            for file in os.listdir(temp_dir):
                if file.endswith('.kml'):
                    kml_file = os.path.join(temp_dir, file)
                    break

            if not kml_file:
                raise Exception('Aucun fichier KML trouvé dans l\'archive KMZ')

            return self._parse_kml(kml_file, result)

    def import_kml(self, kml_path):
        """Importe un fichier KML"""
        result = {
            'points_count': 0,
            'lines_count': 0,
            'polygons_count': 0,
            'kml_content': None,
            'format': 'KML'
        }
        return self._parse_kml(kml_path, result)

    def _parse_kml(self, kml_file, result):
        """Parse un fichier KML"""
        try:
            tree = ET.parse(kml_file)
            root = tree.getroot()
        except Exception as e:
            raise Exception(f'Erreur lors du parsing du KML: {e}')

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

            # Points
            point = placemark.find('kml:Point', ns)
            if point is not None:
                coords = point.findtext('kml:coordinates', '', ns)
                if coords:
                    coords = coords.strip().split(',')
                    if len(coords) >= 2:
                        try:
                            feature = QgsFeature()
                            point_xy = QgsPointXY(float(coords[0]), float(coords[1]))
                            feature.setGeometry(QgsGeometry.fromPointXY(point_xy))
                            feature.setAttributes([name, description, 'POINT'])
                            self.points_layer.dataProvider().addFeature(feature)
                            result['points_count'] += 1
                        except Exception as e:
                            print(f"Erreur point: {e}")

            # Lignes
            linestring = placemark.find('kml:LineString', ns)
            if linestring is not None:
                coords_text = linestring.findtext('kml:coordinates', '', ns)
                if coords_text:
                    coords_list = []
                    for coord in coords_text.strip().split():
                        parts = coord.split(',')
                        if len(parts) >= 2:
                            try:
                                coords_list.append(QgsPointXY(float(parts[0]), float(parts[1])))
                            except ValueError:
                                continue

                    if len(coords_list) >= 2:
                        try:
                            feature = QgsFeature()
                            feature.setGeometry(QgsGeometry.fromPolylineXY(coords_list))
                            feature.setAttributes([name, description, 'LIGNE'])
                            self.lines_layer.dataProvider().addFeature(feature)
                            result['lines_count'] += 1
                        except Exception as e:
                            print(f"Erreur ligne: {e}")

            # Polygones
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
                                    try:
                                        coords_list.append(QgsPointXY(float(parts[0]), float(parts[1])))
                                    except ValueError:
                                        continue

                            if len(coords_list) >= 3:
                                try:
                                    feature = QgsFeature()
                                    feature.setGeometry(QgsGeometry.fromPolygonXY([coords_list]))
                                    feature.setAttributes([name, description, 'POLYGON'])
                                    self.polygons_layer.dataProvider().addFeature(feature)
                                    result['polygons_count'] += 1
                                except Exception as e:
                                    print(f"Erreur polygone: {e}")

        QgsProject.instance().addMapLayer(self.points_layer)
        QgsProject.instance().addMapLayer(self.lines_layer)
        QgsProject.instance().addMapLayer(self.polygons_layer)

        result['kml_content'] = {
            'points_layer': self.points_layer,
            'lines_layer': self.lines_layer,
            'polygons_layer': self.polygons_layer
        }

        return result

    def import_geojson(self, geojson_path):
        """Importe un fichier GeoJSON"""
        result = {
            'points_count': 0,
            'lines_count': 0,
            'polygons_count': 0,
            'kml_content': None,
            'format': 'GeoJSON'
        }

        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        except Exception as e:
            raise Exception(f'Erreur lors de la lecture du GeoJSON: {e}')

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

        features = geojson_data.get('features', [])
        for feature in features:
            try:
                geometry = feature.get('geometry', {})
                properties = feature.get('properties', {})
                name = properties.get('name', 'Sans nom')
                description = properties.get('description', '')
                geom_type = geometry.get('type', '')

                coords = geometry.get('coordinates', [])

                if geom_type == 'Point' and len(coords) >= 2:
                    qgs_feat = QgsFeature()
                    point_xy = QgsPointXY(float(coords[0]), float(coords[1]))
                    qgs_feat.setGeometry(QgsGeometry.fromPointXY(point_xy))
                    qgs_feat.setAttributes([name, description, 'POINT'])
                    self.points_layer.dataProvider().addFeature(qgs_feat)
                    result['points_count'] += 1

                elif geom_type == 'LineString' and len(coords) >= 2:
                    coords_list = [QgsPointXY(float(c[0]), float(c[1])) for c in coords if len(c) >= 2]
                    qgs_feat = QgsFeature()
                    qgs_feat.setGeometry(QgsGeometry.fromPolylineXY(coords_list))
                    qgs_feat.setAttributes([name, description, 'LIGNE'])
                    self.lines_layer.dataProvider().addFeature(qgs_feat)
                    result['lines_count'] += 1

                elif geom_type == 'Polygon' and len(coords) > 0:
                    coords_list = [QgsPointXY(float(c[0]), float(c[1])) for c in coords[0] if len(c) >= 2]
                    if len(coords_list) >= 3:
                        qgs_feat = QgsFeature()
                        qgs_feat.setGeometry(QgsGeometry.fromPolygonXY([coords_list]))
                        qgs_feat.setAttributes([name, description, 'POLYGON'])
                        self.polygons_layer.dataProvider().addFeature(qgs_feat)
                        result['polygons_count'] += 1

            except Exception as e:
                print(f"Erreur lors du traitement du feature GeoJSON: {e}")
                continue

        QgsProject.instance().addMapLayer(self.points_layer)
        QgsProject.instance().addMapLayer(self.lines_layer)
        QgsProject.instance().addMapLayer(self.polygons_layer)

        result['kml_content'] = {
            'points_layer': self.points_layer,
            'lines_layer': self.lines_layer,
            'polygons_layer': self.polygons_layer
        }

        return result

    def import_shapefile(self, shp_path):
        """Importe un fichier Shapefile"""
        try:
            layer = QgsVectorLayer(shp_path, 'Shapefile importé', 'ogr')
            if not layer.isValid():
                raise Exception('Impossible de charger le Shapefile')

            QgsProject.instance().addMapLayer(layer)

            # Compter les géométries
            point_count = 0
            line_count = 0
            polygon_count = 0

            for feature in layer.getFeatures():
                geom = feature.geometry()
                if geom.type() == 0:  # Point
                    point_count += 1
                elif geom.type() == 1:  # Line
                    line_count += 1
                elif geom.type() == 2:  # Polygon
                    polygon_count += 1

            return {
                'points_count': point_count,
                'lines_count': line_count,
                'polygons_count': polygon_count,
                'kml_content': {
                    'points_layer': layer,
                    'lines_layer': layer,
                    'polygons_layer': layer
                },
                'format': 'Shapefile'
            }

        except Exception as e:
            raise Exception(f'Erreur lors de l\'import du Shapefile: {e}')

    def import_gpx(self, gpx_path):
        """Importe un fichier GPX"""
        try:
            layer = QgsVectorLayer(gpx_path, 'GPX importé', 'ogr')
            if not layer.isValid():
                raise Exception('Impossible de charger le fichier GPX')

            QgsProject.instance().addMapLayer(layer)

            point_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 0)
            line_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 1)

            return {
                'points_count': point_count,
                'lines_count': line_count,
                'polygons_count': 0,
                'kml_content': {
                    'points_layer': layer,
                    'lines_layer': layer,
                    'polygons_layer': None
                },
                'format': 'GPX'
            }

        except Exception as e:
            raise Exception(f'Erreur lors de l\'import du GPX: {e}')

    def import_gml(self, gml_path):
        """Importe un fichier GML"""
        try:
            layer = QgsVectorLayer(gml_path, 'GML importé', 'ogr')
            if not layer.isValid():
                raise Exception('Impossible de charger le fichier GML')

            QgsProject.instance().addMapLayer(layer)

            point_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 0)
            line_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 1)
            polygon_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 2)

            return {
                'points_count': point_count,
                'lines_count': line_count,
                'polygons_count': polygon_count,
                'kml_content': {
                    'points_layer': layer,
                    'lines_layer': layer,
                    'polygons_layer': layer
                },
                'format': 'GML'
            }

        except Exception as e:
            raise Exception(f'Erreur lors de l\'import du GML: {e}')

    def import_dxf(self, dxf_path):
        """Importe un fichier DXF"""
        try:
            layer = QgsVectorLayer(dxf_path, 'DXF importé', 'ogr')
            if not layer.isValid():
                raise Exception('Impossible de charger le fichier DXF')

            QgsProject.instance().addMapLayer(layer)

            point_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 0)
            line_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 1)
            polygon_count = sum(1 for f in layer.getFeatures() if f.geometry().type() == 2)

            return {
                'points_count': point_count,
                'lines_count': line_count,
                'polygons_count': polygon_count,
                'kml_content': {
                    'points_layer': layer,
                    'lines_layer': layer,
                    'polygons_layer': layer
                },
                'format': 'DXF'
            }

        except Exception as e:
            raise Exception(f'Erreur lors de l\'import du DXF: {e}')

    def import_csv(self, csv_path):
        """Importe un fichier CSV avec colonnes lat/lon ou x/y"""
        result = {
            'points_count': 0,
            'lines_count': 0,
            'polygons_count': 0,
            'kml_content': None,
            'format': 'CSV'
        }

        try:
            import csv
            
            self.points_layer = QgsVectorLayer('Point', 'Points CSV', 'memory')
            self.points_layer.dataProvider().addAttributes([
                QgsField('name', QVariant.String),
                QgsField('description', QVariant.String),
                QgsField('type', QVariant.String),
            ])
            self.points_layer.updateFields()

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Chercher les colonnes de coordonnées
                        x = None
                        y = None
                        
                        for key in row.keys():
                            key_lower = key.lower()
                            if 'lon' in key_lower or 'x' in key_lower:
                                x = float(row[key])
                            elif 'lat' in key_lower or 'y' in key_lower:
                                y = float(row[key])

                        if x is not None and y is not None:
                            feature = QgsFeature()
                            point_xy = QgsPointXY(x, y)
                            feature.setGeometry(QgsGeometry.fromPointXY(point_xy))
                            name = row.get('name', row.get('Name', 'Point'))
                            description = row.get('description', '')
                            feature.setAttributes([name, description, 'POINT'])
                            self.points_layer.dataProvider().addFeature(feature)
                            result['points_count'] += 1

                    except Exception as e:
                        print(f"Erreur ligne CSV: {e}")
                        continue

            QgsProject.instance().addMapLayer(self.points_layer)
            result['kml_content'] = {
                'points_layer': self.points_layer,
                'lines_layer': None,
                'polygons_layer': None
            }

        except Exception as e:
            raise Exception(f'Erreur lors de l\'import du CSV: {e}')

        return result


# Alias de compatibilité
KMZImporter = MultiFormatImporter
