import os
import sys
import venv
import subprocess
import sqlite3
import platform
import psutil
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Lista de dependencias requeridas
required_modules = ['PyQt6', 'pyttsx3', 'psutil']

def generate_requirements():
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w') as f:
            for module in required_modules:
                f.write(f"{module}\n")
        print("Archivo requirements.txt generado.")

def create_virtual_env():
    if not os.path.exists('zegion_env'):
        print("Creando entorno virtual...")
        venv.create('zegion_env', with_pip=True)
        print("Entorno virtual creado.")
    else:
        print("El entorno virtual ya existe.")

def get_python_executable():
    if sys.platform == 'win32':
        return os.path.join('zegion_env', 'Scripts', 'python.exe')
    return os.path.join('zegion_env', 'bin', 'python')

def install_requirements():
    python = get_python_executable()
    subprocess.check_call([python, "-m", "pip", "install", "-r", "requirements.txt"])

def run_in_virtual_env():
    python = get_python_executable()
    os.execv(python, [python] + sys.argv)

def check_and_install_dependencies():
    generate_requirements()
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Los siguientes módulos no están instalados: {', '.join(missing_modules)}")
        print("Instalando módulos...")
        install_requirements()
        print("Módulos instalados correctamente. Reiniciando el script...")
        run_in_virtual_env()

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

if not is_venv():
    create_virtual_env()
    run_in_virtual_env()

check_and_install_dependencies()

import pyttsx3

class Mahoraga:
    def __init__(self):
        self.os_info = None
        self.resources_info = None
        self.odoo_modules = []
        self.odoo_path = None

    def learn_environment(self):
        self.detect_os()
        self.optimize_resources()

    def detect_os(self):
        self.os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        print(f"Sistema operativo detectado: {json.dumps(self.os_info, indent=2)}")

    def optimize_resources(self):
        self.resources_info = {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict(),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict()
        }
        print(f"Información de recursos: {json.dumps(self.resources_info, indent=2)}")

    def learn_odoo_structure(self, odoo_path):
        self.odoo_path = odoo_path
        if os.path.exists(self.odoo_path):
            for root, dirs, files in os.walk(self.odoo_path):
                if '__manifest__.py' in files:
                    module_name = os.path.basename(root)
                    self.odoo_modules.append({
                        "name": module_name,
                        "path": root,
                        "files": self.get_module_files(root)
                    })
            print(f"Se han encontrado {len(self.odoo_modules)} módulos de Odoo.")
        else:
            print("La ruta especificada no existe.")

    def get_module_files(self, module_path):
        files = []
        for root, _, filenames in os.walk(module_path):
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
        return files

    def analyze_odoo_tests(self):
        if not self.odoo_path:
            return "Por favor, primero especifica la ruta de los módulos de Odoo."
        test_files = []
        for module in self.odoo_modules:
            for file in module['files']:
                if 'tests' in file:
                    with open(file, 'r') as f:
                        content = f.read()
                        if 'unittest' in content or 'test' in content.lower():
                            test_files.append(file)
        return f"Se han encontrado {len(test_files)} archivos de test en los módulos de Odoo."

class Zegion(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_tts()
        self.init_db()
        self.mahoraga = Mahoraga()

    def init_ui(self):
        self.setWindowTitle('Zegion Assistant')
        self.setGeometry(100, 100, 400, 500)
        self.setWindowIcon(QIcon('escarabajo_purpura.png'))

        layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Ingrese su comando aquí...")
        layout.addWidget(self.input_text)

        self.submit_button = QPushButton('Enviar')
        self.submit_button.clicked.connect(self.process_command)
        layout.addWidget(self.submit_button)

        self.response_label = QLabel("Respuesta de Zegion aparecerá aquí")
        layout.addWidget(self.response_label)

        self.setLayout(layout)

    def init_tts(self):
        self.engine = pyttsx3.init()

    def init_db(self):
        self.conn = sqlite3.connect('zegion_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands_history
            (id INTEGER PRIMARY KEY, command TEXT, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        self.conn.commit()

    def process_command(self):
        command = self.input_text.toPlainText()
        response = self.execute_command(command)
        self.response_label.setText(response)
        self.speak(response)
        self.save_command_history(command, response)

    def execute_command(self, command):
        if command.lower() == "hola":
            return "Hello"
        elif command.lower() == "activar over warrior":
            return "Modo activo"
        elif command.lower() == "activo":
            return f"Path de los módulos: {os.getcwd()}"
        elif command.lower().startswith("aprender entorno"):
            self.mahoraga.learn_environment()
            return "Análisis del entorno completado."
        elif command.lower().startswith("set odoo path"):
            path = command.split("set odoo path", 1)[1].strip()
            if not path:
                path = QFileDialog.getExistingDirectory(self, "Seleccionar directorio de módulos Odoo")
            if path:
                self.mahoraga.learn_odoo_structure(path)
                return f"Ruta de Odoo establecida: {path}"
            else:
                return "No se seleccionó ninguna ruta."
        elif command.lower() == "analizar tests odoo":
            return self.mahoraga.analyze_odoo_tests()
        else:
            return "Comando no reconocido"

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def save_command_history(self, command, response):
        self.cursor.execute('INSERT INTO commands_history (command, response) VALUES (?, ?)', (command, response))
        self.conn.commit()

class Sukuna:
    def __init__(self):
        # Implementar red neuronal para aprendizaje y generación de unittest
        pass

    def generate_unittest(self):
        # Lógica para generar unittest
        pass

    def generate_test_report(self):
        # Lógica para generar informe de test
        pass

class Combat:
    def __init__(self):
        # Implementar red neuronal de simulación evolutiva
        pass

    def simulate_battle(self):
        # Implementar los 8 pasos de combate
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    zegion = Zegion()
    zegion.show()
    sys.exit(app.exec())