from pyrr import Matrix44, Vector3
import numpy as np

class Camera:
    """Třída pro správu kamery a jejích matic."""
    def __init__(self, width, height, fov=45.0, near=0.1, far=100.0):
        self.aspect_ratio = width / height
        self.fov = fov
        self.near = near
        self.far = far

        self.position = Vector3([0.0, 0.0, 3.0])  # Posunuta dozadu
        self.target = Vector3([0.0, 0.5, 0.0])    # Míří na střed
        
        # Základní směrové vektory
        self.up = Vector3([0.0, 1.0, 0.0])        # Y osa je nahoru
        self.down = Vector3([0.0, -1.0, 0.0])
        self.back = Vector3([0.0, 0.0, 1.0])
        self.front = Vector3([0.0, 0.0, -1.0])
        self.right = Vector3([1.0, 0.0, 0.0])
        self.left = Vector3([-1.0, 0.0, 0.0])
        
        # Vektor, který udává směr pohledu kamery (od position k target)
        self.direction = self.target - self.position
        
        self.view_matrix = Matrix44.identity()
        self.projection_matrix = Matrix44.identity()

        self.update_projection_matrix()
        self.update_view_matrix()

    def update_view_matrix(self):
        """Aktualizuje pohledovou matici."""
        self.view_matrix = Matrix44.look_at(self.position, self.target, np.array(self.up, dtype=np.float32))
        # Aktualizujeme směrový vektor
        _direction = np.array(self.target, dtype=np.float32) - np.array(self.position, dtype=np.float32)
        norm_direction = np.linalg.norm(_direction)
        if norm_direction > 0.0001:
            self.direction = _direction / norm_direction # self.direction je nyní np.ndarray
        else:
            self.direction = np.array([0.0, 0.0, -1.0], dtype=np.float32) # Fallback

        _up = np.array(self.up, dtype=np.float32) # Začni s původním 'up' jako np.array

        
         # Aktualizujeme ostatní směrové vektory
        _right = np.cross(self.direction, _up)
        norm_right = np.linalg.norm(_right)
        if norm_right > 0.0001:
            self.right = _right / norm_right # self.right je np.ndarray
        else:
            # Pokud je direction a up kolineární, zvolíme nějaký arbitrární right
            # Např. pokud direction je [0,1,0], cross s [0,1,0] je [0,0,0]
            # Musíme se vyhnout této situaci, camera.up by neměl být kolineární s camera.direction
            # V takovém případě je lepší camera.up zvolit jinak, např. [1,0,0] pokud direction je [0,1,0]
            # Pro obecný případ:
            if np.allclose(self.direction, np.array([0.0, 1.0, 0.0])) or np.allclose(self.direction, np.array([0.0, -1.0, 0.0])):
                self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
            else:
                self.right = np.cross(self.direction, np.array([0.0, 1.0, 0.0], dtype=np.float32)) # Křížový součin s globální osou Y
                norm_r = np.linalg.norm(self.right)
                if norm_r > 0.0001: self.right /= norm_r
                else: self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32) # Absolutní fallback


        # Skutečný up vektor (kolmý na right a direction)
        # Ujisti se, že self.right a self.direction jsou normalizované před tímto cross productem
        _true_up = np.cross(self.right, self.direction) 
        norm_true_up = np.linalg.norm(_true_up)
        if norm_true_up > 0.0001:
            self.up = _true_up / norm_true_up # self.up je np.ndarray
        else:
            # Toto by se nemělo stát, pokud right a direction jsou ortogonální a nenulové
            self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32) # Fallback

        
        # Odvození ostatních směrových vektorů
        self.left = -self.right
        self.front = self.direction  # Front je stejný jako direction
        self.back = -self.direction
        self.down = -self.up

    def update_projection_matrix(self):
        """Aktualizuje projekční matici."""
        self.projection_matrix = Matrix44.perspective_projection(
            self.fov, self.aspect_ratio, self.near, self.far
        )

    def move(self, direction_vector, distance):
        """Posune kameru a její cíl ve směru vektoru."""
        movement = direction_vector * distance
        self.position += movement
        self.target += movement
        self.update_view_matrix()
        
    def move_forward(self, distance):
        """Posune kameru dopředu."""
        self.position += self.front * distance
        self.target += self.front * distance
        self.update_view_matrix()
        
    def move_backward(self, distance):
        """Posune kameru dozadu."""
        self.position += self.back * distance
        self.target += self.back * distance
        self.update_view_matrix()
        
    def get_view_matrix_bytes(self):
        """Vrátí pohledovou matici jako byty."""
        return self.view_matrix.astype('f4').tobytes()

    def get_projection_matrix_bytes(self):
        """Vrátí projekční matici jako byty."""
        return self.projection_matrix.astype('f4').tobytes()
