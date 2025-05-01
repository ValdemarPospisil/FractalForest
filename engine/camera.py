#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import math

class Camera:
    def __init__(self, width, height, position=None, target=None):
        # Výchozí pozice kamery a cíl
        self.position = np.array([0.0, -3.0, 2.0]) if position is None else np.array(position)
        self.target = np.array([0.0, 0.0, 0.5]) if target is None else np.array(target)
        self.up = np.array([0.0, 0.0, 1.0])  # Orientace kamery nahoru (Z+)
        
        # Parametry projekce
        self.fov = 45.0  # Zorný úhel v stupních
        self.aspect_ratio = width / height
        self.near = 0.1
        self.far = 100.0
        
        # Inicializace matic
        self.view_matrix = self._calculate_view_matrix()
        self.projection_matrix = self._calculate_projection_matrix()
    
    def _calculate_view_matrix(self):
        """Vypočítá pohledovou matici kamery"""
        # Směr pohledu kamery
        z_axis = self.position - self.target
        z_axis = z_axis / np.linalg.norm(z_axis)
        
        # Pravá strana kamery (kolmá na pohled a horní směr)
        x_axis = np.cross(self.up, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)
        
        # Oprava horního směru, aby byl kolmý na pohled a pravou stranu
        y_axis = np.cross(z_axis, x_axis)
        
        # Vytvoření rotační části matice pohledu
        rotation = np.identity(4, dtype=np.float32)
        rotation[0, 0:3] = x_axis
        rotation[1, 0:3] = y_axis
        rotation[2, 0:3] = z_axis
        
        # Vytvoření translační části matice pohledu
        translation = np.identity(4, dtype=np.float32)
        translation[0, 3] = -np.dot(x_axis, self.position)
        translation[1, 3] = -np.dot(y_axis, self.position)
        translation[2, 3] = -np.dot(z_axis, self.position)
        
        # Kombinace rotace a translace
        return np.matmul(rotation, translation)
    
    def _calculate_projection_matrix(self):
        """Vypočítá projekční matici kamery (perspektivní)"""
        f = 1.0 / math.tan(math.radians(self.fov) / 2.0)
        
        projection = np.zeros((4, 4), dtype=np.float32)
        projection[0, 0] = f / self.aspect_ratio
        projection[1, 1] = f
        projection[2, 2] = (self.far + self.near) / (self.near - self.far)
        projection[2, 3] = (2.0 * self.far * self.near) / (self.near - self.far)
        projection[3, 2] = -1.0
        
        return projection
    
    def set_projection(self, width, height):
        """Aktualizuje projekční matici na základě nových rozměrů okna"""
        self.aspect_ratio = width / height
        self.projection_matrix = self._calculate_projection_matrix()
    
    def get_view_matrix(self):
        """Vrací pohledovou matici kamery"""
        return self.view_matrix
    
    def get_projection_matrix(self):
        """Vrací projekční matici kamery"""
        return self.projection_matrix
