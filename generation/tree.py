import random
from abc import ABC, abstractmethod

class TreeDefinition(ABC):
    """Abstraktní třída pro definici různých typů stromů"""
    
    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    @abstractmethod
    def axiom(self):
        pass
    
    @property
    @abstractmethod
    def rules(self):
        pass
    
    @property
    @abstractmethod
    def iterations(self):
        pass
    
    @property
    @abstractmethod
    def angle(self):
        pass
    
    @property
    @abstractmethod
    def thickness_ratio(self):
        pass
    
    @property
    @abstractmethod
    def length_ratio(self):
        pass
    
    @property
    @abstractmethod
    def random_angle_variation(self):
        pass
    
    @property
    @abstractmethod
    def random_length_variation(self):
        pass
    
    @property
    @abstractmethod
    def base_length(self):
        pass
    
    @property
    @abstractmethod
    def base_thickness(self):
        pass
    
    @property
    @abstractmethod
    def color(self):
        pass


class TreeType1(TreeDefinition):
    """Definice prvního typu stromu - podobný bříze"""
    
    @property
    def name(self):
        return "Bříza"
    
    @property
    def axiom(self):
        return "F"
    
    @property
    def rules(self):
        return {
            "F": [
                "F[+F]F[-F]F",
                "F[+F]F",
                "F[-F]F"
            ]
        }
    
    @property
    def iterations(self):
        return random.randint(3, 4)
    
    @property
    def angle(self):
        return random.uniform(20.0, 25.0)
    
    @property
    def thickness_ratio(self):
        return random.uniform(0.75, 0.85)
    
    @property
    def length_ratio(self):
        return random.uniform(0.75, 0.85)
    
    @property
    def random_angle_variation(self):
        return random.uniform(5.0, 10.0)
    
    @property
    def random_length_variation(self):
        return random.uniform(0.1, 0.2)
    
    @property
    def base_length(self):
        return random.uniform(0.4, 0.6)
    
    @property
    def base_thickness(self):
        return random.uniform(0.08, 0.12)
    
    @property
    def color(self):
        # RGBA barva kmene (hnědá)
        return [0.55, 0.35, 0.15, 1.0]


class TreeType2(TreeDefinition):
    """Definice druhého typu stromu - podobný smrku"""
    
    @property
    def name(self):
        return "Smrk"
    
    @property
    def axiom(self):
        return "F"
    
    @property
    def rules(self):
        return {
            "F": [
                "FF-[-F+F+F]+[+F-F-F]",
                "FF+[+F-F-F]-[-F+F+F]"
            ]
        }
    
    @property
    def iterations(self):
        return random.randint(2, 3)
    
    @property
    def angle(self):
        return random.uniform(22.0, 25.0)
    
    @property
    def thickness_ratio(self):
        return random.uniform(0.65, 0.75)
    
    @property
    def length_ratio(self):
        return random.uniform(0.65, 0.75)
    
    @property
    def random_angle_variation(self):
        return random.uniform(2.0, 5.0)
    
    @property
    def random_length_variation(self):
        return random.uniform(0.05, 0.1)
    
    @property
    def base_length(self):
        return random.uniform(0.5, 0.7)
    
    @property
    def base_thickness(self):
        return random.uniform(0.1, 0.15)
    
    @property
    def color(self):
        # RGBA barva kmene (tmavší hnědá)
        return [0.45, 0.25, 0.1, 1.0]
