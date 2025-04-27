import numpy as np
import math
import pyglet
from pyglet.window import key

class Camera:
    def __init__(self, window):
        self.window = window
        
        # Camera settings
        self.position = np.array([0.0, 1.0, 5.0], dtype='f4')  # Start a bit higher and further back
        self.front = np.array([0.0, 0.0, -1.0], dtype='f4')
        self.up = np.array([0.0, 1.0, 0.0], dtype='f4')
        self.right = np.array([1.0, 0.0, 0.0], dtype='f4')
        
        # Camera angles
        self.yaw = -90.0  # Facing -Z direction
        self.pitch = 0.0
        
        # Mouse handling
        self.last_x = window.width / 2
        self.last_y = window.height / 2
        self.first_mouse = True
        self.mouse_sensitivity = 0.1
        
        # Movement
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)
        self.speed = 2.5  # Units per second
        
        # Mouse capture
        self.mouse_captured = False
        
        # Update vectors
        self._update_camera_vectors()
    
    def _update_camera_vectors(self):
        """Calculate the front, right and up vectors"""
        # Calculate new front vector
        front = np.zeros(3, dtype='f4')
        front[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front[1] = math.sin(math.radians(self.pitch))
        front[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = front / np.linalg.norm(front)
        
        # Recalculate right and up vectors
        self.right = np.cross(self.front, np.array([0.0, 1.0, 0.0], dtype='f4'))
        self.right = self.right / np.linalg.norm(self.right)
        
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def process_mouse_movement(self, x, y, dx, dy):
        """Process mouse movement for camera rotation"""
        if not self.mouse_captured:
            return
            
        dx *= self.mouse_sensitivity
        dy *= self.mouse_sensitivity
        
        self.yaw += dx
        self.pitch -= dy
        
        # Constrain pitch
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
            
        # Update camera vectors
        self._update_camera_vectors()
    
    def process_keyboard(self, dt):
        """Process keyboard input for camera movement"""
        velocity = self.speed * dt
        
        if self.keys[key.W]:
            self.position += self.front * velocity
        if self.keys[key.S]:
            self.position -= self.front * velocity
        if self.keys[key.A]:
            self.position -= self.right * velocity
        if self.keys[key.D]:
            self.position += self.right * velocity
        if self.keys[key.SPACE]:
            self.position += np.array([0.0, 1.0, 0.0], dtype='f4') * velocity
        if self.keys[key.LSHIFT]:
            self.position -= np.array([0.0, 1.0, 0.0], dtype='f4') * velocity
    
    def toggle_mouse_capture(self):
        """Toggle mouse capture state"""
        self.mouse_captured = not self.mouse_captured
        self.window.set_exclusive_mouse(self.mouse_captured)
    
    def get_view_matrix(self):
        """Create a view matrix from camera position, target and up vector"""
        target = self.position + self.front
        return self._look_at(self.position, target, self.up)
    
    def _look_at(self, eye, target, up):
        """Create a look-at matrix"""
        eye = np.array(eye, dtype='f4')
        target = np.array(target, dtype='f4')
        up = np.array(up, dtype='f4')
        
        f = target - eye
        f = f / np.linalg.norm(f)
        
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        
        u = np.cross(s, f)
        
        result = np.identity(4, dtype='f4')
        result[0, 0] = s[0]
        result[0, 1] = s[1]
        result[0, 2] = s[2]
        result[1, 0] = u[0]
        result[1, 1] = u[1]
        result[1, 2] = u[2]
        result[2, 0] = -f[0]
        result[2, 1] = -f[1]
        result[2, 2] = -f[2]
        result[0, 3] = -np.dot(s, eye)
        result[1, 3] = -np.dot(u, eye)
        result[2, 3] = np.dot(f, eye)
        
        return result
