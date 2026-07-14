# -*- coding: utf-8 -*-
"""
Gestionnaire de projet
"""

class ProjectManager:
    def __init__(self):
        self.data = {}
        self.project_path = None
        self.project_name = None

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key, default=None):
        return self.data.get(key, default)

    def clear_data(self):
        self.data = {}

    def save_project(self, path):
        import json
        import os
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, 'project.json'), 'w') as f:
            serializable_data = {}
            for key, value in self.data.items():
                if key != 'graph':
                    serializable_data[key] = value
            json.dump(serializable_data, f, indent=2, default=str)

    def load_project(self, path):
        import json
        import os
        try:
            with open(os.path.join(path, 'project.json'), 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f'Erreur lors du chargement: {e}')
