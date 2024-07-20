# main.py
import sys

from PyQt6.QtWidgets import QApplication
from utils import check_and_install_dependencies, is_venv, create_virtual_env, run_in_virtual_env
from zegion import Zegion


if __name__ == '__main__':
    if not is_venv():
        create_virtual_env()
        run_in_virtual_env()

    check_and_install_dependencies()

    app = QApplication(sys.argv)
    zegion = Zegion()
    zegion.show()
    sys.exit(app.exec())