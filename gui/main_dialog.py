# -*- coding: utf-8 -*-
"""
Dialogue principale de SynoptiquePro
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget,
    QFileDialog, QMessageBox, QProgressBar
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.core import QgsProject
import os

from .import_tab import ImportTab
from .analysis_tab import AnalysisTab
from .synoptique_tab import SynoptiqueTab
from .export_tab import ExportTab
from ..core.project_manager import ProjectManager


class MainDialog(QDialog):
    def __init__(self, iface, project_manager, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.project_manager = project_manager
        self.setWindowTitle(u'SynoptiquePro - Génération de Synoptiques FTTH')
        self.setGeometry(100, 100, 1000, 700)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel(u'<h2>SynoptiquePro - Analyse et Génération de Synoptiques FTTH</h2>')
        layout.addWidget(title)

        # Onglets
        self.tabs = QTabWidget()

        self.import_tab = ImportTab(self.iface, self.project_manager)
        self.analysis_tab = AnalysisTab(self.iface, self.project_manager)
        self.synoptique_tab = SynoptiqueTab(self.iface, self.project_manager)
        self.export_tab = ExportTab(self.iface, self.project_manager)

        self.tabs.addTab(self.import_tab, u'1. Import KMZ')
        self.tabs.addTab(self.analysis_tab, u'2. Analyse')
        self.tabs.addTab(self.synoptique_tab, u'3. Synoptique')
        self.tabs.addTab(self.export_tab, u'4. Export')

        layout.addWidget(self.tabs)

        # Barre de progression
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton(u'Fermer')
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connexions des signaux
        self.import_tab.progress_signal.connect(self.update_progress)
        self.analysis_tab.progress_signal.connect(self.update_progress)
        self.synoptique_tab.progress_signal.connect(self.update_progress)
        self.export_tab.progress_signal.connect(self.update_progress)

    def update_progress(self, value):
        self.progress.setValue(value)
