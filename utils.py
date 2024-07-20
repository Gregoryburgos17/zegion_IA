# utils.py
import os
import sys
import venv
import subprocess

required_modules = ['PyQt6', 'pyttsx3', 'psutil', 'tensorflow', 'numpy']

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