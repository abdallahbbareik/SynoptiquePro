# -*- coding: utf-8 -*-
"""
Onglet d'export
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QTextEdit,
    QProgressBar, QCheckBox, QFileDialog, QHBoxLayout, QGroupBox, QGridLayout
)
from qgis.PyQt.QtCore import pyqtSignal
import os

from ..core.exporters.pdf_exporter import PDFExporter
from ..core.exporters.svg_exporter import SVGExporter
from ..core.exporters.excel_exporter import ExcelExporter
from ..core.exporters.drawio_exporter import DrawIOExporter


class ExportTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self, iface, project_manager, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.project_manager = project_manager
        self.export_path = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Description
        desc = QLabel(u'<b>Étape 4: Exporter le résultat</b><br/>'
                      u'Exportez le synoptique dans différents formats.')
        layout.addWidget(desc)

        # Sélection du répertoire
        path_layout = QHBoxLayout()
        self.path_label = QLabel(u'Aucun répertoire sélectionné')
        path_layout.addWidget(self.path_label)
        browse_btn = QPushButton(u'Parcourir')
        browse_btn.clicked.connect(self.select_export_path)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Options d'export
        export_group = QGroupBox(u'Formats d\'export')
        export_layout = QGridLayout()

        self.export_pdf = QCheckBox(u'PDF')
        self.export_pdf.setChecked(True)
        export_layout.addWidget(self.export_pdf, 0, 0)

        self.export_svg = QCheckBox(u'SVG')
        self.export_svg.setChecked(True)
        export_layout.addWidget(self.export_svg, 0, 1)

        self.export_excel = QCheckBox(u'Excel')
        self.export_excel.setChecked(True)
        export_layout.addWidget(self.export_excel, 0, 2)

        self.export_drawio = QCheckBox(u'Draw.io')
        self.export_drawio.setChecked(True)
        export_layout.addWidget(self.export_drawio, 0, 3)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Boutons d'export
        export_btn = QPushButton(u'Exporter')
        export_btn.clicked.connect(self.export)
        layout.addWidget(export_btn)

        # Log
        layout.addWidget(QLabel(u'Résultat d\'export:'))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Barre de progression
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        layout.addStretch()
        self.setLayout(layout)

    def select_export_path(self):
        path = QFileDialog.getExistingDirectory(self, u'Sélectionner le répertoire d\'export')
        if path:
            self.export_path = path
            self.path_label.setText(f'Répertoire: {path}')

    def export(self):
        try:
            if not self.project_manager.get_data('synoptique'):
                QMessageBox.warning(self, u'Attention', u'Veuillez d\'abord générer le synoptique')
                return

            if not self.export_path:
                QMessageBox.warning(self, u'Attention', u'Veuillez sélectionner un répertoire d\'export')
                return

            self.log_text.append(u'\n--- Début de l\'export ---')
            self.progress.setValue(0)

            synoptique_data = self.project_manager.get_data('synoptique')
            export_count = 0
            total_exports = sum([
                self.export_pdf.isChecked(),
                self.export_svg.isChecked(),
                self.export_excel.isChecked(),
                self.export_drawio.isChecked()
            ])

            # Export PDF
            if self.export_pdf.isChecked():
                try:
                    exporter = PDFExporter()
                    pdf_path = os.path.join(self.export_path, 'synoptique.pdf')
                    exporter.export(synoptique_data, pdf_path)
                    self.log_text.append(f'✓ PDF exporté: {pdf_path}')
                    export_count += 1
                except Exception as e:
                    self.log_text.append(f'✗ Erreur PDF: {str(e)}')
                self.progress.setValue(int(25 * export_count / total_exports))

            # Export SVG
            if self.export_svg.isChecked():
                try:
                    exporter = SVGExporter()
                    svg_path = os.path.join(self.export_path, 'synoptique.svg')
                    exporter.export(synoptique_data, svg_path)
                    self.log_text.append(f'✓ SVG exporté: {svg_path}')
                    export_count += 1
                except Exception as e:
                    self.log_text.append(f'✗ Erreur SVG: {str(e)}')
                self.progress.setValue(int(25 * export_count / total_exports))

            # Export Excel
            if self.export_excel.isChecked():
                try:
                    exporter = ExcelExporter()
                    excel_path = os.path.join(self.export_path, 'synoptique.xlsx')
                    exporter.export(synoptique_data, excel_path)
                    self.log_text.append(f'✓ Excel exporté: {excel_path}')
                    export_count += 1
                except Exception as e:
                    self.log_text.append(f'✗ Erreur Excel: {str(e)}')
                self.progress.setValue(int(25 * export_count / total_exports))

            # Export Draw.io
            if self.export_drawio.isChecked():
                try:
                    exporter = DrawIOExporter()
                    drawio_path = os.path.join(self.export_path, 'synoptique.drawio')
                    exporter.export(synoptique_data, drawio_path)
                    self.log_text.append(f'✓ Draw.io exporté: {drawio_path}')
                    export_count += 1
                except Exception as e:
                    self.log_text.append(f'✗ Erreur Draw.io: {str(e)}')
                self.progress.setValue(int(25 * export_count / total_exports))

            self.progress.setValue(100)
            self.log_text.append(u'\n✓ Export terminé!')
            QMessageBox.information(self, u'Succès', u'L\'export a été complété avec succès!')

        except Exception as e:
            self.log_text.append(f'✗ Erreur: {str(e)}')
            QMessageBox.critical(self, u'Erreur', f'Erreur lors de l\'export: {str(e)}')
