"""
Základní třída pro herní entity
"""
import pyrr

class Entity:
    """Základní třída pro objekty ve scéně"""
    
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        """
        Inicializace entity
        
        Parametry:
        - position: pozice entity v prostoru (x, y, z)
        - rotation: rotace entity v Eulerových úhlech (pitch, yaw, roll)
        - scale: měřítko entity (sx, sy, sz)
        """
        self.position = pyrr.Vector3(position)
        self.rotation = pyrr.Vector3(rotation)
        self.scale = pyrr.Vector3(scale)
        
    def get_model_matrix(self):
        """
        Vrací modelovou matici entity
        
        Vrací:
        - 4x4 modelová matice
        """
        # Vytvoření matic transformací
        translation = pyrr.matrix44.create_from_translation(self.position)
        
        # Rotace podle os x, y, z (pitch, yaw, roll)
        rotation_x = pyrr.matrix44.create_from_x_rotation(self.rotation.x)
        rotation_y = pyrr.matrix44.create_from_y_rotation(self.rotation.y)
        rotation_z = pyrr.matrix44.create_from_z_rotation(self.rotation.z)
        
        # Kombinace rotačních matic (nejprve kolem z, pak kolem y, pak kolem x)
        rotation = pyrr.matrix44.multiply(rotation_z, rotation_y)
        rotation = pyrr.matrix44.multiply(rotation, rotation_x)
        
        # Matice pro změnu měřítka
        scale = pyrr.matrix44.create_from_scale(self.scale)
        
        # Kombinace všech transformací: nejprve měřítko, pak rotace, nakonec posunutí
        model_matrix = pyrr.matrix44.multiply(scale, rotation)
        model_matrix = pyrr.matrix44.multiply(model_matrix, translation)
        
        return model_matrix
    
    def move(self, dx, dy, dz):
        """
        Posune entitu o zadaný vektor
        
        Parametry:
        - dx, dy, dz: složky vektoru posunutí
        """
        self.position.x += dx
        self.position.y += dy
        self.position.z += dz
        
    def rotate(self, dpitch, dyaw, droll):
        """
        Otočí entitu o zadané úhly
        
        Parametry:
        - dpitch, dyaw, droll: změny úhlů v radiánech
        """
        self.rotation.x += dpitch
        self.rotation.y += dyaw
        self.rotation.z += droll
