# database_manager.py
import sqlite3
import json
from PyQt6.QtCore import QObject

class DatabaseManager(QObject):
    def __init__(self, db_name='zegion_data.db'):
        super().__init__()
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.update_tables()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands_history
            (id INTEGER PRIMARY KEY, command TEXT, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS environment_analysis
            (id INTEGER PRIMARY KEY, analysis_data TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS odoo_paths
            (id INTEGER PRIMARY KEY, path TEXT UNIQUE)
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS odoo_modules
            (id INTEGER PRIMARY KEY, module_name TEXT, module_path TEXT, code_content TEXT, 
             test_content TEXT, test_result TEXT, version TEXT, path_id INTEGER,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
             FOREIGN KEY(path_id) REFERENCES odoo_paths(id))
        ''')
        self.conn.commit()

    def update_tables(self):
        columns_to_add = ['code_content', 'test_content', 'test_result', 'version', 'path_id']
        for column in columns_to_add:
            self.cursor.execute(f"PRAGMA table_info(odoo_modules)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if column not in columns:
                self.cursor.execute(f"ALTER TABLE odoo_modules ADD COLUMN {column} TEXT")
        self.conn.commit()

    def save_command_history(self, command, response):
        self.cursor.execute('INSERT INTO commands_history (command, response) VALUES (?, ?)', (command, response))
        self.conn.commit()

    def save_environment_analysis(self, analysis_data):
        self.cursor.execute('INSERT INTO environment_analysis (analysis_data) VALUES (?)', (json.dumps(analysis_data),))
        self.conn.commit()

    def save_odoo_path(self, path):
        self.cursor.execute('INSERT OR IGNORE INTO odoo_paths (path) VALUES (?)', (path,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_odoo_paths(self):
        self.cursor.execute('SELECT id, path FROM odoo_paths')
        return self.cursor.fetchall()

    def save_odoo_module(self, module_name, module_path, code_content, test_content, version, path_id):
        self.cursor.execute('''
            INSERT OR REPLACE INTO odoo_modules 
            (module_name, module_path, code_content, test_content, version, path_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (module_name, module_path, code_content, test_content, version, path_id))
        self.conn.commit()

    def update_test_result(self, module_name, test_result):
        self.cursor.execute('''
            UPDATE odoo_modules SET test_result = ? WHERE module_name = ?
        ''', (test_result, module_name))
        self.conn.commit()

    def get_last_environment_analysis(self):
        self.cursor.execute('SELECT analysis_data FROM environment_analysis ORDER BY timestamp DESC LIMIT 1')
        result = self.cursor.fetchone()
        return json.loads(result[0]) if result else None

    def get_odoo_modules(self):
        self.cursor.execute('SELECT module_name, module_path FROM odoo_modules')
        return self.cursor.fetchall()