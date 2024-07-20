#Odoo Analysis with Unittest Execution

import os
import ast
import sys
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class OdooAnalysisThread(QThread):
    progress_update = pyqtSignal(int, str)
    result_ready = pyqtSignal(str)
    module_analyzed = pyqtSignal(str, str, str, str, str, int, str)

    def __init__(self, odoo_path, path_id):
        super().__init__()
        self.odoo_path = odoo_path
        self.path_id = path_id

    def run(self):
        modules = []
        total_modules = sum(1 for _ in os.scandir(self.odoo_path) if _.is_dir())
        analyzed_modules = 0

        for module_name in os.scandir(self.odoo_path):
            if module_name.is_dir():
                module_path = module_name.path
                code_content = ""
                test_content = ""
                version = "Unknown"
                test_result = ""

                # Obtener la versión del módulo
                manifest_path = os.path.join(module_path, '__manifest__.py')
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as manifest_file:
                        manifest_content = manifest_file.read()
                        try:
                            manifest_dict = ast.literal_eval(manifest_content)
                            version = manifest_dict.get('version', 'Unknown')
                        except:
                            pass

                # Buscar la carpeta de tests
                tests_folder = os.path.join(module_path, 'tests')
                if os.path.exists(tests_folder) and os.path.isdir(tests_folder):
                    for file in os.listdir(tests_folder):
                        if file.endswith('.py'):
                            file_path = os.path.join(tests_folder, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    test_content += f"# File: {file}\n{f.read()}\n\n"
                            except UnicodeDecodeError:
                                with open(file_path, 'r', encoding='iso-8859-1') as f:
                                    test_content += f"# File: {file}\n{f.read()}\n\n"
                    
                    # Ejecutar pruebas unitarias
                    test_result = self.run_unittest(tests_folder)

                # Analizar archivos del módulo (excluyendo tests)
                for root, dirs, files in os.walk(module_path):
                    if 'tests' in root.split(os.path.sep):
                        continue
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    code_content += f"# File: {file}\n{f.read()}\n\n"
                            except UnicodeDecodeError:
                                with open(file_path, 'r', encoding='iso-8859-1') as f:
                                    code_content += f"# File: {file}\n{f.read()}\n\n"

                self.module_analyzed.emit(module_name.name, module_path, code_content, test_content, version, self.path_id, test_result)
                modules.append({"name": module_name.name, "path": module_path, "version": version})
                
                analyzed_modules += 1
                progress = (analyzed_modules / total_modules) * 100
                self.progress_update.emit(int(progress), f"Analizando módulo: {module_name.name}")

        result = f"Se han encontrado y analizado {len(modules)} módulos de Odoo en la ruta: {self.odoo_path}"
        self.result_ready.emit(result)

    def run_unittest(self, tests_folder):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", tests_folder],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error al ejecutar pruebas: {str(e)}"