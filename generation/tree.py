import random
import math
import logging
from abc import ABC, abstractmethod
from .lsystem import LSystem

class TreeDefinition(ABC):
    """Abstract base class for defining different tree types"""
    
    @property
    @abstractmethod
    def name(self):
        """Tree type name"""
        pass
    
    @property
    @abstractmethod
    def axiom(self):
        """Starting axiom for L-system"""
        pass
    
    @property
    @abstractmethod
    def rules(self):
        """Production rules for L-system"""
        pass
    
    @property
    @abstractmethod
    def iterations(self):
        """Number of iterations to generate the tree"""
        pass
    
    @property
    @abstractmethod
    def angle(self):
        """Base angle for branches in degrees"""
        pass
    
    @property
    @abstractmethod
    def thickness_ratio(self):
        """Ratio for branch thickness reduction"""
        pass
    
    @property
    @abstractmethod
    def length_ratio(self):
        """Ratio for branch length reduction"""
        pass
    
    @property
    @abstractmethod
    def random_angle_variation(self):
        """Maximum random variation in angle (degrees)"""
        pass
    
    @property
    @abstractmethod
    def random_length_variation(self):
        """Maximum random variation in length (proportion)"""
        pass
    
    @property
    @abstractmethod
    def base_length(self):
        """Base length of the trunk"""
        pass
    
    @property
    @abstractmethod
    def base_thickness(self):
        """Base thickness of the trunk"""
        pass
    
    @property
    @abstractmethod
    def color(self):
        """Trunk color in RGBA format"""
        pass
    
    def get_lsystem(self) -> LSystem:
        """Returns an LSystem instance for this tree type with random variations."""
        # Select a random rule from available options for each symbol
        selected_rules = {}
        for symbol, rule_options in self.rules.items():
            if isinstance(rule_options, list):
                selected_rules[symbol] = random.choice(rule_options)
            else:
                selected_rules[symbol] = rule_options
        
        # Apply random variations to angle
        final_angle = math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
        
        # Apply random variations to length
        final_length = self.base_length * (1 + random.uniform(-self.random_length_variation, self.random_length_variation))
        
        # Create L-system with selected parameters
        lsystem = LSystem(
            axiom=self.axiom,
            rules=selected_rules,
            angle=final_angle,
            scale=self.length_ratio,
            initial_length=final_length,
            initial_width=self.base_thickness,
            trunk_color=self.color[:3]  # Only RGB components for trunk
        )
        
        logging.info(f"Created {self.name} with angle={math.degrees(final_angle):.1f}°, scale={self.length_ratio:.2f}")
        return lsystem
    
    def get_iterations(self) -> int:
        """Returns the number of iterations for this tree."""
        return self.iterations
    
    def get_properties(self) -> dict:
        """Returns a dictionary of tree properties for display purposes."""
        properties = {
            "name": self.name,
            "axiom": self.axiom,
            "iterations": self.iterations,
            "angle": self.angle,
            "thickness_ratio": self.thickness_ratio,
            "length_ratio": self.length_ratio,
            "base_length": self.base_length,
            "base_thickness": self.base_thickness,
            "color": self.color
        }
        return properties


class StandardTree(TreeDefinition):
    """Definition of a standard tree"""
    
    @property
    def name(self):
        return "Standard Tree"
    
    @property
    def axiom(self):
        return "X"
    
    @property
    def rules(self):
        return {
            "X": [
                "F-[[X]+X]+F[+FX]-X",
                "F[+X]F[-X]+X",
                "F[/X][\\X]F[^X]&X",
                "F[&X][^X]F[+X]-X"
            ],
            "F": ["FF", "F"]
        }
    
    @property
    def iterations(self):
        return random.randint(3, 4)
    
    @property
    def angle(self):
        return random.uniform(20.0, 30.0)
    
    @property
    def thickness_ratio(self):
        return random.uniform(0.75, 0.85)
    
    @property
    def length_ratio(self):
        return random.uniform(0.75, 0.85)
    
    @property
    def random_angle_variation(self):
        return 1.0
    
    @property
    def random_length_variation(self):
        return 0.1
    
    @property
    def base_length(self):
        return random.uniform(0.08, 0.12)
    
    @property
    def base_thickness(self):
        return random.uniform(0.02, 0.04)
    
    @property
    def color(self):
        return [0.65, 0.35, 0.15, 1.0]


class BushyTree(TreeDefinition):
    """Definition of a bushy tree"""
    
    @property
    def name(self):
        return "Bushy Tree"
    
    @property
    def axiom(self):
        return "F"
    
    @property
    def rules(self):
        return {
            "F": [
                "F[+F][-F][/F][\\F]F",
                "FF-[-F+F+F]+[+F-F-F]",
                "F[&F][^F]F[+F]-F"
            ]
        }
    
    @property
    def iterations(self):
        return random.randint(3, 4)
    
    @property
    def angle(self):
        return random.uniform(22.0, 35.0)
    
    @property
    def thickness_ratio(self):
        return random.uniform(0.8, 0.9)
    
    @property
    def length_ratio(self):
        return random.uniform(0.8, 0.9)
    
    @property
    def random_angle_variation(self):
        return 1.0
    
    @property
    def random_length_variation(self):
        return 0.1
    
    @property
    def base_length(self):
        return random.uniform(0.06, 0.1)
    
    @property
    def base_thickness(self):
        return random.uniform(0.02, 0.04)
    
    @property
    def color(self):
        return [0.47, 0.35, 0.2, 1.0]


class WeepingTree(TreeDefinition):
    """Definition of a weeping tree"""
    
    @property
    def name(self):
        return "Weeping Tree"
    
    @property
    def axiom(self):
        return "F"
    
    @property
    def rules(self):
        return {
            "F": [
                "F[+&F][-&F][/&F][\\&F]F",
                "FF[+&F][-&F]F",
                "F[\\&F][/&F]F"
            ]
        }
    
    @property
    def iterations(self):
        return random.randint(3, 4)
    
    @property
    def angle(self):
        return random.uniform(15.0, 25.0)
    
    @property
    def thickness_ratio(self):
        return random.uniform(0.8, 0.9)
    
    @property
    def length_ratio(self):
        return random.uniform(0.8, 0.9)
    
    @property
    def random_angle_variation(self):
        return 1.5
    
    @property
    def random_length_variation(self):
        return 0.1
    
    @property
    def base_length(self):
        return random.uniform(0.1, 0.15)
    
    @property
    def base_thickness(self):
        return random.uniform(0.02, 0.04)
    
    @property
    def color(self):
        return [0.6, 0.35, 0.2, 1.0]


class BirchTree(TreeDefinition):
    """Definition of a birch tree"""
    
    @property
    def name(self):
        return "Birch Tree"
    
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
        return 1.0
    
    @property
    def random_length_variation(self):
        return 0.1
    
    @property
    def base_length(self):
        return random.uniform(0.2, 0.3)
    
    @property
    def base_thickness(self):
        return random.uniform(0.02, 0.04)
    
    @property
    def color(self):
        return [0.9, 0.88, 0.8, 1.0]


class PineTree(TreeDefinition):
    """Definition of a pine tree"""
    
    @property
    def name(self):
        return "Pine Tree"
    
    @property
    def axiom(self):
        return "F"
    
    @property
    def rules(self):
        return {
            "F": [
                "FF-[-F+F+F]",
                "[+F-F-F]",
                "FF+[+F-F-F]",
                "[-F+F+F]"
            ]
        }
    
    @property
    def iterations(self):
        return random.randint(3, 4)
    
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
        return 1.0
    
    @property
    def random_length_variation(self):
        return 0.05
    
    @property
    def base_length(self):
        return random.uniform(0.3, 0.4)
    
    @property
    def base_thickness(self):
        return random.uniform(0.03, 0.05)
    
    @property
    def color(self):
        return [0.38, 0.2, 0.12, 1.0]


# List of available tree types
TREE_TYPES = [StandardTree, BushyTree, WeepingTree, BirchTree, PineTree]

def get_random_tree_type() -> TreeDefinition:
    """Returns an instance of a randomly selected tree type."""
    chosen_type = random.choice(TREE_TYPES)
    tree = chosen_type()  # Create instance of the selected class
    logging.info(f"Selected tree type: {tree.name}")
    return tree


def get_tree_by_name(name: str) -> TreeDefinition:
    """Returns a tree instance by name."""
    for tree_class in TREE_TYPES:
        tree_instance = tree_class()
        if tree_instance.name.lower() == name.lower():
            logging.info(f"Created tree by name: {name}")
            return tree_instance
    
    # If we don't find a tree with the given name, return the standard tree
    logging.warning(f"Unknown tree type: {name}, using StandardTree")
    return StandardTree()
