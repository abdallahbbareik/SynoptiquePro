# -*- coding: utf-8 -*-
"""
SynoptiquePro - Plugin principal QGIS
"""

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication
import os
import sys

from .gui.main_dialog import MainDialog
from .core.project_manager import ProjectManager


class SynoptiquePro:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = u'&SynoptiquePro'
        self.toolbar = self.iface.addToolBar(u'SynoptiquePro')
        self.toolbar.setObjectName(u'SynoptiquePro')
        self.project_manager = ProjectManager()

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        if parent is None:
            parent = self.iface.mainWindow()

        action = QAction(text, parent)
        if icon_path:
            action.setIcon(QIcon(icon_path))
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'resources', 'icon.png')
        self.add_action(
            icon_path,
            text=u'Ouvrir SynoptiquePro',
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(u'&SynoptiquePro', action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        dialog = MainDialog(self.iface, self.project_manager)
        dialog.exec_()
