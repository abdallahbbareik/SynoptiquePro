# -*- coding: utf-8 -*-
"""
Onglet d'import KMZ
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox,
    QTextEdit, QProgressBar
)
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsProject
import os

from ..core.kmz_importer import KMZImporter
from ..core.project_manager import ProjectManager


class ImportTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self, iface, project_manager, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.project_manager = project_manager
        self.kmz_importer = KMZImporter()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Description
        desc = QLabel(u'<b>Étape 1: Importer le fichier KMZ</b><br/>'
                      u'Sélectionnez un fichier KMZ contenant le plan des câbles FTTH.')
        layout.addWidget(desc)

        # Sélection fichier
        self.file_label = QLabel(u'Aucun fichier sélectionné')
        layout.addWidget(self.file_label)

        select_btn = QPushButton(u'Sélectionner un fichier KMZ')
        select_btn.clicked.connect(self.select_kmz_file)
        layout.addWidget(select_btn)

        # Bouton d'import
        import_btn = QPushButton(u'Importer le KMZ')
        import_btn.clicked.connect(self.import_kmz)
        layout.addWidget(import_btn)

        # Log
        layout.addWidget(QLabel(u'Résultat d\'import:'))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Barre de progression
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        layout.addStretch()
        self.setLayout(layout)
        self.kmz_path = None

    def select_kmz_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            u'Sélectionner un fichier KMZ',
            '',
            u'KMZ Files (*.kmz);;All Files (*)'
        )
        if file_path:
            self.kmz_path = file_path
            self.file_label.setText(f'Fichier: {os.path.basename(file_path)}')
            self.log_text.append(f'✓ Fichier sélectionné: {file_path}')

    def import_kmz(self):
        if not self.kmz_path:
            QMessageBox.warning(self, u'Attention', u'Veuillez sélectionner un fichier KMZ')
            return

        try:
            self.log_text.append(u'\n--- Début de l\'import ---')
            self.progress.setValue(0)

            # Import du KMZ
            result = self.kmz_importer.import_kmz(self.kmz_path)

            self.progress.setValue(50)
            self.log_text.append(u'✓ KMZ importé avec succès')
            self.log_text.append(f'  - Points: {result["points_count"]}')
            self.log_text.append(f'  - Lignes: {result["lines_count"]}')
            self.log_text.append(f'  - Polygones: {result["polygons_count"]}')

            # Sauvegarde du projet
            self.project_manager.set_data('kmz_path', self.kmz_path)
            self.project_manager.set_data('import_result', result)

            self.progress.setValue(100)
            self.log_text.append(u'\n✓ Import terminé avec succès!')
            QMessageBox.information(self, u'Succès', u'Le fichier KMZ a été importé avec succès!')

        except Exception as e:
            self.log_text.append(f'✗ Erreur: {str(e)}')
            QMessageBox.critical(self, u'Erreur', f'Erreur lors de l\'import: {str(e)}')
