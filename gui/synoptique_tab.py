# -*- coding: utf-8 -*-
"""
Onglet de génération de synoptique
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QTextEdit,
    QProgressBar, QComboBox, QCheckBox, QHBoxLayout
)
from qgis.PyQt.QtCore import pyqtSignal

from ..core.synoptique_generator import SynoptiqueGenerator


class SynoptiqueTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self, iface, project_manager, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.project_manager = project_manager
        self.generator = SynoptiqueGenerator()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Description
        desc = QLabel(u'<b>Étape 3: Générer le synoptique</b><br/>'
                      u'Génération automatique du diagramme arborescent du réseau.')
        layout.addWidget(desc)

        # Options
        options_layout = QHBoxLayout()

        options_layout.addWidget(QLabel(u'Style:'))
        self.style_combo = QComboBox()
        self.style_combo.addItems([u'Arborescent', u'Détaillé', u'Hiérarchique'])
        options_layout.addWidget(self.style_combo)

        self.show_distances = QCheckBox(u'Afficher les distances')
        self.show_distances.setChecked(True)
        options_layout.addWidget(self.show_distances)

        self.show_fiber_count = QCheckBox(u'Afficher les fibres')
        self.show_fiber_count.setChecked(True)
        options_layout.addWidget(self.show_fiber_count)

        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Bouton de génération
        generate_btn = QPushButton(u'Générer le synoptique')
        generate_btn.clicked.connect(self.generate_synoptique)
        layout.addWidget(generate_btn)

        # Log
        layout.addWidget(QLabel(u'Résultat:'))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Barre de progression
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        layout.addStretch()
        self.setLayout(layout)

    def generate_synoptique(self):
        try:
            if not self.project_manager.get_data('analysis_result'):
                QMessageBox.warning(self, u'Attention', u'Veuillez d\'abord analyser le réseau')
                return

            self.log_text.append(u'\n--- Génération du synoptique ---')
            self.progress.setValue(0)

            # Génération du synoptique
            result = self.generator.generate(
                self.project_manager.get_data('network_graph'),
                style=self.style_combo.currentText(),
                show_distances=self.show_distances.isChecked(),
                show_fiber_count=self.show_fiber_count.isChecked()
            )

            self.progress.setValue(75)
            self.log_text.append(u'✓ Synoptique généré')
            self.log_text.append(f'  - Niveaux: {result["levels"]}')
            self.log_text.append(f'  - Éléments: {result["elements_count"]}')
            self.log_text.append(f'  - Chemins: {result["paths_count"]}')

            self.project_manager.set_data('synoptique', result)

            self.progress.setValue(100)
            self.log_text.append(u'\n✓ Génération terminée!')
            QMessageBox.information(self, u'Succès', u'Le synoptique a été généré avec succès!')

        except Exception as e:
            self.log_text.append(f'✗ Erreur: {str(e)}')
            QMessageBox.critical(self, u'Erreur', f'Erreur lors de la génération: {str(e)}')
