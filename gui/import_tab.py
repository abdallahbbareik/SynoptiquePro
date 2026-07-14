# -*- coding: utf-8 -*-
"""
Onglet d'import multiformat géospatial avec sélection de couches QGIS
Supports: KMZ, KML, SHP, GeoJSON, GML, DXF, GPX, CSV
+ Sélection des couches déjà chargées dans QGIS
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox,
    QTextEdit, QProgressBar, QComboBox, QHBoxLayout, QGroupBox, QListWidget,
    QListWidgetItem, QCheckBox, QTabWidget
)
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsProject, QgsVectorLayer
import os

from ..core.kmz_importer import MultiFormatImporter


class ImportTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self, iface, project_manager, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.project_manager = project_manager
        self.importer = MultiFormatImporter()
        self.file_path = None
        self.selected_layers = []
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Créer des onglets pour les deux méthodes
        self.tabs = QTabWidget()

        # Onglet 1: Import depuis fichier
        self.file_tab = self._create_file_import_tab()
        self.tabs.addTab(self.file_tab, u'Importer un fichier')

        # Onglet 2: Sélection depuis QGIS
        self.qgis_tab = self._create_qgis_layers_tab()
        self.tabs.addTab(self.qgis_tab, u'Sélectionner depuis QGIS')

        main_layout.addWidget(self.tabs)

        # Zone de résultat commune
        result_layout = QVBoxLayout()
        result_layout.addWidget(QLabel(u'<b>Résultat de l\'import:</b>'))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        result_layout.addWidget(self.log_text)

        # Barre de progression
        self.progress = QProgressBar()
        result_layout.addWidget(self.progress)

        main_layout.addLayout(result_layout)
        self.setLayout(main_layout)

    def _create_file_import_tab(self):
        """Crée l'onglet d'import depuis fichier"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Description
        desc = QLabel(u'<b>Importer un fichier géospatial</b><br/>'
                      u'Sélectionnez un fichier contenant le plan des câbles FTTH.<br/>'
                      u'<small>Formats supportés: KMZ, KML, SHP, GeoJSON, GML, DXF, GPX, CSV</small>')
        layout.addWidget(desc)

        # Sélection fichier
        file_layout = QHBoxLayout()
        self.file_label = QLabel(u'Aucun fichier sélectionné')
        file_layout.addWidget(self.file_label)
        select_btn = QPushButton(u'Parcourir')
        select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_btn)
        layout.addLayout(file_layout)

        # Méthode d'import
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel(u'Méthode d\'import:'))
        self.import_method = QComboBox()
        self.import_method.addItems([
            u'Direct (QGIS natif - sans modification)',
            u'Analyse complète (parsing détaillé)'
        ])
        method_layout.addWidget(self.import_method)
        method_layout.addStretch()
        layout.addLayout(method_layout)

        # Options
        options_group = QGroupBox(u'Options')
        options_layout = QVBoxLayout()
        
        self.add_to_project = QCheckBox(u'Ajouter les couches au projet QGIS')
        self.add_to_project.setChecked(True)
        options_layout.addWidget(self.add_to_project)
        
        self.auto_zoom = QCheckBox(u'Zoomer automatiquement sur les couches')
        self.auto_zoom.setChecked(True)
        options_layout.addWidget(self.auto_zoom)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Bouton d'import
        import_btn = QPushButton(u'Importer le fichier')
        import_btn.clicked.connect(self.import_file)
        layout.addWidget(import_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_qgis_layers_tab(self):
        """Crée l'onglet de sélection des couches QGIS"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Description
        desc = QLabel(u'<b>Sélectionner des couches depuis QGIS</b><br/>'
                      u'Choisissez parmi les couches déjà chargées dans votre projet QGIS.')
        layout.addWidget(desc)

        # Bouton de rafraîchissement
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton(u'Rafraîchir la liste')
        refresh_btn.clicked.connect(self.refresh_layer_list)
        refresh_layout.addStretch()
        refresh_layout.addWidget(refresh_btn)
        layout.addLayout(refresh_layout)

        # Liste des couches
        layout.addWidget(QLabel(u'Couches disponibles:'))
        self.layers_list = QListWidget()
        self.layers_list.setSelectionMode(self.layers_list.MultiSelection)
        layout.addWidget(self.layers_list)

        # Filtres
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(u'Filtrer par type:'))
        self.filter_type = QComboBox()
        self.filter_type.addItems([
            u'Tous',
            u'Points',
            u'Lignes',
            u'Polygones'
        ])
        self.filter_type.currentTextChanged.connect(self.refresh_layer_list)
        filter_layout.addWidget(self.filter_type)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Bouton de sélection
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton(u'Sélectionner tout')
        select_all_btn.clicked.connect(lambda: self.layers_list.selectAll())
        select_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton(u'Désélectionner tout')
        deselect_all_btn.clicked.connect(lambda: self.layers_list.clearSelection())
        select_layout.addWidget(deselect_all_btn)
        layout.addLayout(select_layout)

        # Bouton d'utilisation
        use_btn = QPushButton(u'Utiliser les couches sélectionnées')
        use_btn.clicked.connect(self.use_selected_layers)
        layout.addWidget(use_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def select_file(self):
        """Sélection du fichier géospatial"""
        file_filter = u'Tous les fichiers géospatiaux (*.kmz *.kml *.shp *.geojson *.json *.gml *.dxf *.gpx *.csv);;' \
                     u'KMZ Files (*.kmz);;' \
                     u'KML Files (*.kml);;' \
                     u'Shapefile (*.shp);;' \
                     u'GeoJSON (*.geojson *.json);;' \
                     u'GML (*.gml);;' \
                     u'DXF (*.dxf);;' \
                     u'GPX (*.gpx);;' \
                     u'CSV (*.csv);;' \
                     u'Tous les fichiers (*)'

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            u'Sélectionner un fichier géospatial',
            '',
            file_filter
        )
        
        if file_path:
            self.file_path = file_path
            file_ext = os.path.splitext(file_path)[1].lower()
            self.file_label.setText(f'Fichier: {os.path.basename(file_path)} ({file_ext})')
            self.log_text.append(f'✓ Fichier sélectionné: {os.path.basename(file_path)}')

    def import_file(self):
        """Importe le fichier sélectionné"""
        if not self.file_path:
            QMessageBox.warning(self, u'Attention', u'Veuillez sélectionner un fichier')
            return

        try:
            self.log_text.append(u'\n--- Début de l\'import ---')
            self.progress.setValue(0)

            file_ext = os.path.splitext(self.file_path)[1].lower()
            method = self.import_method.currentText()

            if u'Direct' in method:
                # Import direct sans modification
                result = self._import_direct(self.file_path, file_ext)
            else:
                # Analyse complète
                result = self.importer.import_file(self.file_path)

            self.progress.setValue(50)
            self.log_text.append(u'✓ Fichier importé avec succès')
            self.log_text.append(f'  - Format: {result.get("format", "Inconnu")}')
            self.log_text.append(f'  - Points: {result.get("points_count", 0)}')
            self.log_text.append(f'  - Lignes: {result.get("lines_count", 0)}')
            self.log_text.append(f'  - Polygones: {result.get("polygons_count", 0)}')

            # Sauvegarde du projet
            self.project_manager.set_data('file_path', self.file_path)
            self.project_manager.set_data('import_result', result)
            self.project_manager.set_data('import_format', file_ext)

            self.progress.setValue(100)
            self.log_text.append(u'\n✓ Import terminé avec succès!')
            QMessageBox.information(self, u'Succès', u'Le fichier a été importé avec succès!')

        except Exception as e:
            self.log_text.append(f'✗ Erreur: {str(e)}')
            QMessageBox.critical(self, u'Erreur', f'Erreur lors de l\'import: {str(e)}')
            self.progress.setValue(0)

    def refresh_layer_list(self):
        """Rafraîchit la liste des couches disponibles dans QGIS"""
        self.layers_list.clear()
        
        project = QgsProject.instance()
        all_layers = project.mapLayers().values()
        filter_type = self.filter_type.currentText()

        for layer in all_layers:
            if not isinstance(layer, QgsVectorLayer):
                continue

            # Filtrer par type
            geom_type = layer.geometryType()
            type_name = self._get_geometry_type_name(geom_type)

            if filter_type != u'Tous':
                filter_map = {
                    u'Points': 0,
                    u'Lignes': 1,
                    u'Polygones': 2
                }
                if geom_type != filter_map.get(filter_type, -1):
                    continue

            # Créer l'élément de liste
            item_text = f"{layer.name()} ({type_name}) - {layer.featureCount()} features"
            item = QListWidgetItem(item_text)
            item.setData(1, layer.id())  # Stocker l'ID de la couche
            self.layers_list.addItem(item)

    def _get_geometry_type_name(self, geom_type):
        """Convertit le type de géométrie en nom lisible"""
        names = {
            0: u'Points',
            1: u'Lignes',
            2: u'Polygones',
            3: u'Géométries multiples'
        }
        return names.get(geom_type, u'Inconnu')

    def use_selected_layers(self):
        """Utilise les couches sélectionnées dans QGIS"""
        try:
            self.log_text.append(u'\n--- Utilisation des couches sélectionnées ---')
            self.progress.setValue(0)

            selected_items = self.layers_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, u'Attention', u'Veuillez sélectionner au moins une couche')
                return

            project = QgsProject.instance()
            selected_layers = []
            result = {
                'points_count': 0,
                'lines_count': 0,
                'polygons_count': 0,
                'format': 'QGIS Layers',
                'kml_content': {
                    'layers': []
                }
            }

            for item in selected_items:
                layer_id = item.data(1)
                layer = project.mapLayer(layer_id)

                if layer and isinstance(layer, QgsVectorLayer):
                    selected_layers.append(layer)
                    result['kml_content']['layers'].append(layer)

                    # Compter les géométries
                    for feature in layer.getFeatures():
                        geom = feature.geometry()
                        if geom.type() == 0:
                            result['points_count'] += 1
                        elif geom.type() == 1:
                            result['lines_count'] += 1
                        elif geom.type() == 2:
                            result['polygons_count'] += 1

                    self.log_text.append(f'  ✓ Couche utilisée: {layer.name()}')

            self.progress.setValue(50)

            # Sauvegarde du projet
            self.project_manager.set_data('import_result', result)
            self.project_manager.set_data('import_format', 'QGIS')
            self.project_manager.set_data('selected_layers', selected_layers)

            self.progress.setValue(100)
            self.log_text.append(f'\n✓ {len(selected_layers)} couche(s) sélectionnée(s) avec succès!')
            self.log_text.append(f'  - Points: {result["points_count"]}')
            self.log_text.append(f'  - Lignes: {result["lines_count"]}')
            self.log_text.append(f'  - Polygones: {result["polygons_count"]}')

            QMessageBox.information(self, u'Succès', f'{len(selected_layers)} couche(s) sélectionnée(s) avec succès!')

        except Exception as e:
            self.log_text.append(f'✗ Erreur: {str(e)}')
            QMessageBox.critical(self, u'Erreur', f'Erreur lors de la sélection: {str(e)}')
            self.progress.setValue(0)

    def _import_direct(self, file_path, file_ext):
        """Import direct des fichiers sans modification (méthode native QGIS)"""
        result = {
            'points_count': 0,
            'lines_count': 0,
            'polygons_count': 0,
            'format': file_ext.upper(),
            'kml_content': None
        }

        try:
            if file_ext == '.kmz':
                # Extraction du KMZ
                import zipfile
                import tempfile

                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    kml_file = None
                    for file in os.listdir(temp_dir):
                        if file.endswith('.kml'):
                            kml_file = os.path.join(temp_dir, file)
                            break

                    if not kml_file:
                        raise Exception('Aucun fichier KML trouvé dans le KMZ')

                    # Charger directement dans QGIS
                    layer = QgsVectorLayer(kml_file, os.path.basename(file_path), 'ogr')
                    if not layer.isValid():
                        raise Exception('Impossible de charger le KML')

                    if self.add_to_project.isChecked():
                        QgsProject.instance().addMapLayer(layer)

                    # Compter les géométries
                    for feature in layer.getFeatures():
                        geom = feature.geometry()
                        if geom.type() == 0:  # Point
                            result['points_count'] += 1
                        elif geom.type() == 1:  # Line
                            result['lines_count'] += 1
                        elif geom.type() == 2:  # Polygon
                            result['polygons_count'] += 1

                    result['kml_content'] = {
                        'layer': layer,
                        'file_path': file_path
                    }

                    if self.auto_zoom.isChecked():
                        self.iface.mapCanvas().zoomToFeatureExtent(layer.extent())

            elif file_ext in ['.kml', '.shp', '.geojson', '.json', '.gml', '.dxf', '.gpx']:
                # Import direct avec QGIS OGR
                layer = QgsVectorLayer(file_path, os.path.basename(file_path), 'ogr')
                if not layer.isValid():
                    raise Exception(f'Impossible de charger le fichier {file_ext}')

                if self.add_to_project.isChecked():
                    QgsProject.instance().addMapLayer(layer)

                # Compter les géométries
                for feature in layer.getFeatures():
                    geom = feature.geometry()
                    if geom.type() == 0:  # Point
                        result['points_count'] += 1
                    elif geom.type() == 1:  # Line
                        result['lines_count'] += 1
                    elif geom.type() == 2:  # Polygon
                        result['polygons_count'] += 1

                result['kml_content'] = {
                    'layer': layer,
                    'file_path': file_path
                }

                if self.auto_zoom.isChecked():
                    self.iface.mapCanvas().zoomToFeatureExtent(layer.extent())

            elif file_ext == '.csv':
                # Import CSV (pas de couche directe, utiliser MultiFormatImporter)
                result = self.importer.import_csv(file_path)

            else:
                raise Exception(f'Format non supporté: {file_ext}')

        except Exception as e:
            raise Exception(f'Erreur lors de l\'import direct: {e}')

        return result
