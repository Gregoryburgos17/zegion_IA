import os
import sys
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QProgressBar, QPlainTextEdit, QInputDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from database_manager import DatabaseManager
from environment_analysis import EnvironmentAnalysisThread
from odoo_analysis import OdooAnalysisThread
from mahoraga import Mahoraga
import pyttsx3
import json

class OdooTestThread(QThread):
    progress_update = pyqtSignal(int, str)
    result_ready = pyqtSignal(str)

    def __init__(self, odoo_path, config_path, db_name, module_name):
        super().__init__()
        self.odoo_path = odoo_path
        self.config_path = config_path
        self.db_name = db_name
        self.module_name = module_name

    def run(self):
        try:
            # Configurar el PYTHONPATH
            server_path = os.path.join(self.odoo_path, 'server')
            sys.path.insert(0, server_path)
            os.environ['PYTHONPATH'] = f"{server_path};{os.environ.get('PYTHONPATH', '')}"

            # Definir la ruta al ejecutable de Python y odoo-bin
            python_path = r'D:\Odoo_16\python\python.exe'
            odoo_bin_path = r'D:\Odoo_16\server\odoo-bin'

            command = [
                python_path,
                odoo_bin_path,
                "-c", self.config_path,
                "-d", self.db_name,
                "--test-enable",
                "--stop-after-init",
                "--log-level=test",
                "-i", self.module_name,
                "-u", self.module_name
            ]
            # Ejecutar el comando
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(process)
            # Leer la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.progress_update.emit(50, output.strip())

            # Obtener el código de retorno
            rc = process.poll()
            print(rc)
            # Emitir el resultado
            if rc == 0:
                self.result_ready.emit(f"Pruebas completadas exitosamente para el módulo {self.module_name}")
            else:
                stderr_output = process.stderr.read()
                self.result_ready.emit(f"Error en las pruebas del módulo {self.module_name}. Código de salida: {rc}\n\nError:\n{stderr_output}")

        except Exception as e:
            self.result_ready.emit(f"Error al ejecutar las pruebas: {str(e)}")

class Zegion(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.init_tts()
        self.mahoraga = Mahoraga(self.db_manager)

    def init_ui(self):
        self.setWindowTitle('Zegion Assistant')
        self.setGeometry(100, 100, 600, 700)
        self.setWindowIcon(QIcon('escarabajo_purpura.png'))

        layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Ingrese su comando aquí...")
        layout.addWidget(self.input_text)

        self.submit_button = QPushButton('Enviar')
        self.submit_button.clicked.connect(self.process_command)
        layout.addWidget(self.submit_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.response_text = QPlainTextEdit()
        self.response_text.setReadOnly(True)
        layout.addWidget(self.response_text)

        self.setLayout(layout)

    def init_tts(self):
        self.engine = pyttsx3.init()

    def process_command(self):
        command = self.input_text.toPlainText()
        response = self.execute_command(command)
        self.response_text.setPlainText(response)
        self.speak(response)
        self.db_manager.save_command_history(command, response)

    def execute_command(self, command):
        if command.lower() == "hola":
            return "Hello"
        elif command.lower() == "activar over warrior":
            return "Modo activo"
        elif command.lower() == "activo":
            return f"Path de los módulos: {os.getcwd()}"
        elif command.lower() == "aprender entorno":
            self.analyze_environment()
            return "Iniciando análisis del entorno..."
        elif command.lower().startswith("add odoo path"):
            return self.add_odoo_path(command)
        elif command.lower() == "list odoo paths":
            return self.list_odoo_paths()
        elif command.lower() == "analizar modulos odoo":
            return self.analyze_all_odoo_paths()
        elif command.lower() == "ejecutar tests odoo":
            return self.run_odoo_tests()
        elif command.lower() == "predecir optimización":
            return self.predict_optimization()
        elif command.lower() == "run":
            return self.run()
        else:
            return "Comando no reconocido"

    def run(self):
        self.progress_bar.setVisible(True)
        
        # Valores predefinidos para pruebas
        odoo_path = r'D:\Odoo_16'
        config_path = r'D:\Odoo_16\server\odoo.conf'
        db_name = 'ada_16'
        module_name = 'account_accountant'  # Puedes cambiar esto al módulo que quieras probar

        self.test_thread = OdooTestThread(odoo_path, config_path, db_name, module_name)
        self.test_thread.progress_update.connect(self.update_progress_with_message)
        self.test_thread.result_ready.connect(self.display_odoo_test_result)
        self.test_thread.start()
        
        return f"Ejecutando pruebas de Odoo para el módulo {module_name}..."

    def analyze_environment(self):
        self.progress_bar.setVisible(True)
        self.analysis_thread = EnvironmentAnalysisThread()
        self.analysis_thread.progress_update.connect(self.update_progress)
        self.analysis_thread.result_ready.connect(self.display_environment_analysis)
        self.analysis_thread.start()

    def add_odoo_path(self, command):
        path = command.split("add odoo path", 1)[1].strip()
        if not path:
            path = QFileDialog.getExistingDirectory(self, "Seleccionar directorio de módulos Odoo")
        if path:
            path_id = self.db_manager.save_odoo_path(path)
            return f"Nueva ruta de Odoo añadida: {path}"
        else:
            return "No se seleccionó ninguna ruta."

    def list_odoo_paths(self):
        paths = self.db_manager.get_odoo_paths()
        if paths:
            return "Rutas de Odoo registradas:\n" + "\n".join([f"{id}: {path}" for id, path in paths])
        else:
            return "No hay rutas de Odoo registradas."

    def analyze_all_odoo_paths(self):
        paths = self.db_manager.get_odoo_paths()
        if not paths:
            return "No hay rutas de Odoo registradas. Por favor, añade una ruta primero."
        
        for path_id, path in paths:
            self.progress_bar.setVisible(True)
            self.analysis_thread = self.mahoraga.learn_odoo_structure(path)
            self.analysis_thread.progress_update.connect(self.update_progress_with_message)
            self.analysis_thread.result_ready.connect(self.display_odoo_analysis_result)
            self.analysis_thread.module_analyzed.connect(self.save_odoo_module_with_test)
            self.analysis_thread.start()
        
        return f"Analizando módulos de Odoo en {len(paths)} rutas..."

    def run_odoo_tests(self):
        self.progress_bar.setVisible(True)
        paths = self.db_manager.get_odoo_paths()
        if not paths:
            return "No hay rutas de Odoo registradas. Por favor, añade una ruta primero."
        
        odoo_path = paths[0][1]  # Assuming the first path is the Odoo server path
        
        config_path, ok = QInputDialog.getText(self, "Configuración de Odoo", "Ingrese la ruta del archivo de configuración de Odoo:")
        if not ok or not config_path:
            return "No se proporcionó la ruta del archivo de configuración."
        
        db_name, ok = QInputDialog.getText(self, "Base de datos", "Ingrese el nombre de la base de datos:")
        if not ok or not db_name:
            return "No se proporcionó el nombre de la base de datos."
        
        module_name, ok = QInputDialog.getText(self, "Módulo", "Ingrese el nombre del módulo a probar:")
        if not ok or not module_name:
            return "No se proporcionó el nombre del módulo."

        self.test_thread = OdooTestThread(odoo_path, config_path, db_name, module_name)
        self.test_thread.progress_update.connect(self.update_progress_with_message)
        self.test_thread.result_ready.connect(self.display_odoo_test_result)
        self.test_thread.start()
        
        return f"Ejecutando pruebas de Odoo para el módulo {module_name}..."

    def predict_optimization(self):
        environment_data = self.db_manager.get_last_environment_analysis()
        odoo_data = self.db_manager.get_odoo_modules()
        if not environment_data or not odoo_data:
            return "No hay suficientes datos para realizar una predicción. Por favor, analiza el entorno y los módulos de Odoo primero."
        
        optimization_score = self.mahoraga.predict_optimization(environment_data, odoo_data)
        return f"Predicción de optimización: {optimization_score:.2f}%"

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_progress_with_message(self, value, message):
        self.progress_bar.setValue(value)
        self.response_text.setPlainText(message)

    def display_environment_analysis(self, result):
        self.progress_bar.setVisible(False)
        analysis = json.loads(result)
        self.db_manager.save_environment_analysis(analysis)
        formatted_result = (
            f"Análisis del Entorno:\n\n"
            f"Sistema Operativo: {analysis['os']['system']} {analysis['os']['release']}\n"
            f"Procesador: {analysis['os']['processor']}\n\n"
            f"CPU:\n"
            f"  Núcleos físicos: {analysis['cpu']['physical_cores']}\n"
            f"  Núcleos totales: {analysis['cpu']['total_cores']}\n"
            f"  Frecuencia máxima: {analysis['cpu']['max_frequency']}\n"
            f"  Uso por núcleo: {', '.join(analysis['cpu']['usage_per_core'])}\n\n"
            f"Memoria:\n"
            f"  Total: {analysis['memory']['total']}\n"
            f"  Disponible: {analysis['memory']['available']}\n"
            f"  Usada: {analysis['memory']['used']} ({analysis['memory']['percentage']})\n\n"
            f"Disco:\n"
            f"  Total: {analysis['disk']['total']}\n"
            f"  Usado: {analysis['disk']['used']} ({analysis['disk']['percentage']})\n"
            f"  Libre: {analysis['disk']['free']}\n\n"
            f"Red:\n"
            f"  Datos enviados: {analysis['network']['bytes_sent']}\n"
            f"  Datos recibidos: {analysis['network']['bytes_recv']}\n\n"
            f"Optimización del sistema: {analysis['optimization']}\n"
        )
        self.response_text.setPlainText(formatted_result)
        self.speak("Análisis del entorno completado. Por favor, revisa los resultados en la interfaz.")

        # Entrenar el modelo con los nuevos datos
        odoo_data = self.db_manager.get_odoo_modules()
        self.mahoraga.train_model(analysis, odoo_data)

    def display_odoo_analysis_result(self, result):
        self.progress_bar.setVisible(False)
        self.response_text.setPlainText(result)
        self.speak("Análisis de módulos de Odoo completado.")

    def display_odoo_test_result(self, result):
        self.progress_bar.setVisible(False)
        self.response_text.setPlainText(result)
        self.speak("Ejecución de pruebas de Odoo completada.")
        
        # Save test result to database
        module_name = result.split("para el módulo")[-1].strip().split()[0]
        self.db_manager.update_test_result(module_name, result)

    def save_odoo_module_with_test(self, module_name, module_path, code_content, test_content, version, path_id, test_result):
        self.db_manager.save_odoo_module(module_name, module_path, code_content, test_content, version, path_id)
        self.db_manager.update_test_result(module_name, test_result)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()