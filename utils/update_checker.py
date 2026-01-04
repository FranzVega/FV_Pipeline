# -*- coding: utf-8 -*-
"""
PKL Pipeline - Update Checker
Sistema para verificar y descargar updates desde GitHub
"""
import sys
import os

# Python 2/3 compatibility
if sys.version_info[0] >= 3:
    import urllib.request as urllib2
    import urllib.error
else:
    import urllib2

try:
    import json
except ImportError:
    import simplejson as json


class UpdateChecker(object):
    """Verifica y descarga actualizaciones desde GitHub"""
    
    def __init__(self):
        # Importar settings
        try:
            import settings
            self.repo_info = settings.get_repo_info()
            self.current_version = settings.VERSION
        except:
            print("Error: Could not load settings")
            self.repo_info = None
            self.current_version = "unknown"
    
    def check_for_updates(self):
        """
        Verifica si hay una version mas nueva en GitHub
        Returns: dict con 'available', 'current_version', 'latest_version'
        """
        if not self.repo_info:
            return {'available': False, 'error': 'Settings not loaded'}
        
        try:
            # Obtener el archivo settings.py desde GitHub
            # La estructura del repo es: FV_Pipeline/config/settings.py (sin pkl_pipeline/)
            url = "{}/contents/config/settings.py".format(self.repo_info['api'])
            
            print("Checking for updates...")
            print("URL: {}".format(url))
            
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'PKL-Pipeline-Updater')
            
            response = urllib2.urlopen(request, timeout=10)
            data = json.loads(response.read())
            
            # GitHub API retorna el contenido en base64
            import base64
            content = base64.b64decode(data['content']).decode('utf-8')
            
            # Buscar VERSION en el contenido
            for line in content.split('\n'):
                if line.strip().startswith('VERSION'):
                    # Extraer version: VERSION = "1.0.0"
                    remote_version = line.split('=')[1].strip().strip('"').strip("'")
                    
                    print("Current version: {}".format(self.current_version))
                    print("Latest version:  {}".format(remote_version))
                    
                    update_available = remote_version != self.current_version
                    
                    return {
                        'available': update_available,
                        'current_version': self.current_version,
                        'latest_version': remote_version,
                        'message': 'Update available!' if update_available else 'You are up to date!'
                    }
            
            return {'available': False, 'error': 'Could not parse version'}
            
        except Exception as e:
            print("Error checking for updates: {}".format(e))
            return {
                'available': False,
                'error': str(e),
                'current_version': self.current_version
            }
    
    def get_update_instructions(self):
        """
        Retorna instrucciones para actualizar
        """
        if not self.repo_info:
            return "Error: Repository info not available"
        
        instructions = """
=== HOW TO UPDATE ===

Option 1: Git Pull (if you cloned the repo)
  1. Navigate to your pkl_pipeline folder
  2. Run: git pull origin main
  3. Restart Maya or reload the tool

Option 2: Manual Download
  1. Go to: {}
  2. Download the latest version
  3. Replace your current pkl_pipeline folder
  4. Restart Maya

Option 3: Re-install via drag & drop
  1. Download install.mel from GitHub
  2. Drag & drop to Maya (it will replace the shelf button)

=====================
""".format(self.repo_info['url'])
        
        return instructions


# Funciones de conveniencia
def check_updates():
    """Wrapper para uso rapido"""
    checker = UpdateChecker()
    return checker.check_for_updates()

def show_update_instructions():
    """Muestra instrucciones de actualizacion"""
    checker = UpdateChecker()
    print(checker.get_update_instructions())