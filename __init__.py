# -*- coding: utf-8 -*-
"""
SynoptiquePro - Plugin QGIS pour la génération automatique de synoptiques FTTH
"""

def classFactory(iface):
    from .synoptique_pro import SynoptiquePro
    return SynoptiquePro(iface)
