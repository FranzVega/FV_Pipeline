# -*- coding: utf-8 -*-
"""
PKL Pipeline - Auto Updater
Sistema AGRESIVO de auto-actualizacion desde GitHub
NO crea backups, reemplaza directamente
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


class AutoUpdater(object):
    """Descarga y actualiza archivos desde GitHub"""
    
    def __init__(self):
        try:
            import settings
            self.repo_info = settings.get_repo_info()
            self.current_version = settings.VERSION
            
            # Calcular PIPELINE_ROOT (donde esta todo)
            settings_path = os.path.abspath(settings.__file__)
            config_dir = os.path.dirname(settings_path)
            self.pipeline_root = os.path.dirname(config_dir)
            
            print("Pipeline root: {}".format(self.pipeline_root))
            
        except Exception as e:
            print("Error loading settings: {}".format(e))
            self.repo_info = None
            self.pipeline_root = None
    
    def get_remote_file_list(self):
        """Obtiene lista de archivos del repo en GitHub"""
        if not self.repo_info:
            return None
        
        try:
            # Obtener estructura del repo
            url = "{}/contents".format(self.repo_info['api'])
            print("Fetching repo structure from: {}".format(url))
            
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'PKL-Pipeline-Updater')
            
            response = urllib2.urlopen(request, timeout=10)
            data = json.loads(response.read())
            
            files_to_update = []
            
            # Recorrer directorios
            for item in data:
                if item['type'] == 'dir' and item['name'] in ['config', 'core', 'ui', 'utils']:
                    # Obtener archivos de cada directorio
                    dir_url = item['url']
                    dir_request = urllib2.Request(dir_url)
                    dir_request.add_header('User-Agent', 'PKL-Pipeline-Updater')
                    dir_response = urllib2.urlopen(dir_request, timeout=10)
                    dir_data = json.loads(dir_response.read())
                    
                    for file_item in dir_data:
                        if file_item['type'] == 'file' and file_item['name'].endswith('.py'):
                            files_to_update.append({
                                'name': file_item['name'],
                                'path': file_item['path'],
                                'download_url': file_item['download_url'],
                                'folder': item['name']
                            })
            
            return files_to_update
            
        except Exception as e:
            print("Error fetching file list: {}".format(e))
            return None
    
    def download_and_replace_file(self, file_info):
        """Descarga un archivo y lo reemplaza (SIN backup)"""
        try:
            url = file_info['download_url']
            local_path = os.path.join(self.pipeline_root, file_info['folder'], file_info['name'])
            
            print("Downloading: {}".format(file_info['path']))
            
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'PKL-Pipeline-Updater')
            response = urllib2.urlopen(request, timeout=30)
            content = response.read()
            
            # Escribir directamente (reemplaza si existe)
            with open(local_path, 'wb') as f:
                f.write(content)
            
            print("  -> Updated: {}".format(local_path))
            return True
            
        except Exception as e:
            print("  -> ERROR updating {}: {}".format(file_info['name'], e))
            return False
    
    def update_all_files(self):
        """Actualiza todos los archivos Python del pipeline"""
        if not self.pipeline_root:
            return {'success': False, 'error': 'Pipeline root not found'}
        
        print("=" * 60)
        print("PKL PIPELINE - AUTO UPDATE")
        print("=" * 60)
        
        # Obtener lista de archivos
        files = self.get_remote_file_list()
        if not files:
            return {'success': False, 'error': 'Could not fetch file list'}
        
        print("\nFound {} files to check".format(len(files)))
        
        # Descargar y reemplazar cada archivo
        updated = []
        failed = []
        
        for file_info in files:
            if self.download_and_replace_file(file_info):
                updated.append(file_info['path'])
            else:
                failed.append(file_info['path'])
        
        print("\n" + "=" * 60)
        print("UPDATE COMPLETE")
        print("  Updated: {}".format(len(updated)))
        print("  Failed:  {}".format(len(failed)))
        print("=" * 60)
        
        if failed:
            print("\nFailed files:")
            for f in failed:
                print("  - {}".format(f))
        
        return {
            'success': len(failed) == 0,
            'updated': updated,
            'failed': failed,
            'total': len(files)
        }


# Funcion de conveniencia
def auto_update():
    """Ejecuta auto-update completo"""
    updater = AutoUpdater()
    return updater.update_all_files()
