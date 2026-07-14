# -*- coding: utf-8 -*-
"""
Exportation en PDF
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import os


class PDFExporter:
    def __init__(self):
        pass

    def export(self, synoptique_data, output_path):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        doc = SimpleDocTemplate(output_path, pagesize=landscape(A4))
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph('Synoptique FTTH', title_style))
        story.append(Spacer(1, 0.3*inch))

        info_data = [
            ['Paramètre', 'Valeur'],
            ['Style', synoptique_data.get('style', 'N/A')],
            ['Niveaux', str(synoptique_data.get('levels', 0))],
            ['Éléments', str(synoptique_data.get('elements_count', 0))],
            ['Chemins', str(synoptique_data.get('paths_count', 0))],
            ['Distances visibles', 'Oui' if synoptique_data.get('show_distances') else 'Non'],
            ['Fibres visibles', 'Oui' if synoptique_data.get('show_fiber_count') else 'Non'],
        ]

        table = Table(info_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph('Arborescence du réseau', styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        ascii_tree = synoptique_data.get('ascii_representation', 'N/A')
        tree_style = ParagraphStyle(
            'TreeStyle',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=8,
            leftIndent=0
        )
        story.append(Paragraph(f'<pre>{ascii_tree}</pre>', tree_style))

        doc.build(story)
