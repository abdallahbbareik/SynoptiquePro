# -*- coding: utf-8 -*-
"""
Onglet d'analyse topologique
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QTextEdit,
    QProgressBar, QCheckBox, QSpinBox, QHBoxLayout
)
from qgis.PyQt.QtCore import pyqtSignal

from ..core.network_analyzer import NetworkAnalyzer


class AnalysisTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self, iface, project_manager, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.project_manager = project_manager
        self.analyzer = NetworkAnalyzer()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Description
        desc = QLabel(u'<b>Étape 2: Analyser le réseau</b><br/>'
                      u'Analyse topologique des câbles et identification des éléments réseau.')
        layout.addWidget(desc)

        # Options
        options_layout = QHBoxLayout()
        
        self.detect_elements = QCheckBox(u'Détecter automatiquement les éléments')
        self.detect_elements.setChecked(True)
        options_layout.addWidget(self.detect_elements)

        self.tolerance_label = QLabel(u'Tolérance (m):')
        self.tolerance = QSpinBox()
        self.tolerance.setValue(5)
        self.tolerance.setMinimum(1)
        self.tolerance.setMaximum(100)
        options_layout.addWidget(self.tolerance_label)
        options_layout.addWidget(self.tolerance)
        options_layout.addStretch()

        layout.addLayout(options_layout)

        # Bouton d'analyse
        analyze_btn = QPushButton(u'Lancer l\'analyse')
        analyze_btn.clicked.connect(self.analyze_network)
        layout.addWidget(analyze_btn)

        # Log
        layout.addWidget(QLabel(u'Résultat d\'analyse:'))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Barre de progression
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        layout.addStretch()
        self.setLayout(layout)

    def analyze_network(self):
        try:
            if not self.project_manager.get_data('import_result'):
                QMessageBox.warning(self, u'Attention', u'Veuillez d\'abord importer un fichier KMZ')
                return

            self.log_text.append(u'\n--- Début de l\'analyse ---')
            self.progress.setValue(0)

            # Analyse du réseau
            result = self.analyzer.analyze_network(
                self.project_manager.get_data('import_result'),
                detect_elements=self.detect_elements.isChecked(),
                tolerance=self.tolerance.value()
            )

            self.progress.setValue(50)
            self.log_text.append(u'✓ Analyse de la topologie complétée')
            self.log_text.append(f'  - Nœuds: {result["nodes_count"]}')
            self.log_text.append(f'  - Arêtes: {result["edges_count"]}')
            self.log_text.append(f'  - Éléments détectés: {result["elements_count"]}')
            self.log_text.append(f'  - Chemins identifiés: {result["paths_count"]}')

            self.project_manager.set_data('analysis_result', result)
            self.project_manager.set_data('network_graph', result['graph'])

            self.progress.setValue(100)
            self.log_text.append(u'\n✓ Analyse terminée avec succès!')
            QMessageBox.information(self, u'Succès', u'L\'analyse a été complétée avec succès!')

        except Exception as e:
            self.log_text.append(f'✗ Erreur: {str(e)}')
            QMessageBox.critical(self, u'Erreur', f'Erreur lors de l\'analyse: {str(e)}')
