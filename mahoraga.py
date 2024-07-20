# mahoraga.py

import numpy as np
from odoo_analysis import OdooAnalysisThread
import tensorflow as tf
class Mahoraga:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.model = self.create_model()

    def create_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def learn_odoo_structure(self, odoo_path):
        path_id = self.db_manager.save_odoo_path(odoo_path)
        return OdooAnalysisThread(odoo_path, path_id)

    def train_model(self, environment_data, odoo_data):
        X = self.preprocess_data(environment_data, odoo_data)
        y = np.array([float(environment_data['optimization'][:-1])])
        self.model.fit(X, y, epochs=100, verbose=0)

    def predict_optimization(self, environment_data, odoo_data):
        X = self.preprocess_data(environment_data, odoo_data)
        return self.model.predict(X)[0][0]

    def preprocess_data(self, environment_data, odoo_data):
        cpu_cores = environment_data['cpu']['total_cores']
        cpu_freq = float(environment_data['cpu']['max_frequency'][:-3])
        memory_total = float(environment_data['memory']['total'][:-3])
        disk_total = float(environment_data['disk']['total'][:-3])
        disk_used_percent = float(environment_data['disk']['percentage'][:-1])
        num_modules = len(odoo_data)

        X = np.array([
            cpu_cores / 16,
            cpu_freq / 5000,
            memory_total / 64,
            disk_total / 1000,
            disk_used_percent / 100,
            num_modules / 100
        ])

        return X.reshape(1, -1)