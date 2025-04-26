"""
Modul pro správu kamery
"""
import math
import numpy as np
import pyrr

class Camera:
    """Třída representující kameru ve 3D prostoru"""
    
    def __init__(self, width, height):
        # Pozice kamery
        self.position = pyrr.Vector3([0.0, 10.0, 0.0])
        
        # Směr pohledu (forward vektor)
        self.forward = pyrr.Vector3([0.0, 0.0, -1.0])
        self.up = pyrr.Vector3([0.0, 1.0, 0.0])
        self.right = pyrr.Vector3([1.0, 0.0, 0.0])
        
        # Úhly natočení
        self.yaw = -90.0  # horizontální úhel
        self.pitch = 0.0  # vertikální úhel
        
        # Rychlost pohybu a citlivost myši
        self.movement_speed = 0.5
        self.mouse_sensitivity = 0.1
        
        # Matice pohledu a projekce
        self.view_matrix = pyrr.matrix44.create_identity()
        self.update_projection(width, height)
        self.update_vectors()
        
    def update_projection(self, width, height):
        """Aktualizuje projekční matici při změně velikosti okna"""
        aspect_ratio = width / height
        self.projection_matrix = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=aspect_ratio, near=0.1, far=1000.0
        )
        
    def update_vectors(self):
        """Aktualizuje vektory směru pohledu na základě úhlů"""
        # Výpočet nového forward vektoru
        self.forward[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.forward[1] = math.sin(math.radians(self.pitch))
        self.forward[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.forward = pyrr.vector.normalise(self.forward)
        
        # Přepočítání right a up vektorů
        self.right = pyrr.vector3.cross(self.forward, pyrr.Vector3([0.0, 1.0, 0.0]))
        self.right = pyrr.vector.normalise(self.right)
        
        self.up = pyrr.vector3.cross(self.right, self.forward)
        self.up = pyrr.vector.normalise(self.up)
        
        # Aktualizace view matice
        self.update_view_matrix()
        
    def update_view_matrix(self):
        """Aktualizuje pohledovou matici"""
        self.view_matrix = pyrr.matrix44.create_look_at(
            eye=self.position,
            target=self.position + self.forward,
            up=self.up
        )
        
    def rotate(self, dx, dy):
        """Rotace kamery na základě pohybu myši"""
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity
        
        # Omezení úhlu pohledu nahoru a dolů
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
            
        self.update_vectors()
        
    def move_forward(self):
        """Pohyb kamery dopředu"""
        self.position += self.forward * self.movement_speed
        self.update_view_matrix()
        
    def move_backward(self):
        """Pohyb kamery dozadu"""
        self.position -= self.forward * self.movement_speed
        self.update_view_matrix()
        
    def move_left(self):
        """Pohyb kamery doleva"""
        self.position -= self.right * self.movement_speed
        self.update_view_matrix()
        
    def move_right(self):
        """Pohyb kamery doprava"""
        self.position += self.right * self.movement_speed
        self.update_view_matrix()
        
    def set_walk_mode(self):
        """Nastavení režimu chůze (kamera se pohybuje pouze po povrchu)"""
        self.movement_speed = 0.3
        # Zde by byla implementace omezení kamery na výšku terénu
        
    def set_fly_mode(self):
        """Nastavení režimu létání (kamera se může volně pohybovat)"""
        self.movement_speed = 0.5
