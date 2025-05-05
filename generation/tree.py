import random
import math
import logging
from abc import ABC, abstractmethod
from .lsystem import LSystem

class TreeDefinition(ABC):
    """Abstract base class for defining different tree types"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tree type name"""
        pass

    @property
    @abstractmethod
    def rules(self) -> dict:
        """Production rules for L-system"""
        pass

    @property
    @abstractmethod
    def angle(self) -> float:
        """Base angle for branches in degrees"""
        pass

    @property
    @abstractmethod
    def base_length_ratio(self) -> float:
        """Base length ratio influencing initial branch length relative to viewport height"""
        pass

    @property
    @abstractmethod
    def trunk_color(self) -> tuple:
        """Base trunk color in RGB format (0.0-1.0)"""
        pass

    @property
    @abstractmethod
    def leaf_color(self) -> tuple | list[tuple]:
        """Leaf color in RGB format or a list [min_color, max_color] for range"""
        pass

    @property
    def axiom(self) -> str:
        """Default axiom for all trees"""
        return "X" # Starting with 'X' often encourages initial branching

    @property
    def iterations(self) -> int:
        """Default iterations - increased for density"""
        return 5 # Default increased to 5

    @property
    def scale(self) -> float:
        """Default scale ratio for branch length reduction"""
        return 0.75 # Slightly smaller scale can make trees bushier

    @property
    def initial_width(self) -> float:
        """Initial width of the trunk base"""
        return 5.5 # Default thicker trunk base

    def get_lsystem(self) -> LSystem:
        """Returns an LSystem instance for this tree type with consistent sizing."""
        selected_rules = {}
        for symbol, rule_options in self.rules.items():
            if isinstance(rule_options, list):
                selected_rules[symbol] = random.choice(rule_options)
            else:
                selected_rules[symbol] = rule_options

        final_angle = math.radians(self.angle)

        # Adjust initial length based on iterations for better consistency
        # Trees with more iterations naturally become taller if length isn't adjusted
        initial_length = 0.6 * self.base_length_ratio / (self.iterations * 0.8)

        lsystem = LSystem(
            axiom=self.axiom,
            rules=selected_rules,
            angle=final_angle,
            scale=self.scale,
            initial_length=initial_length,
            initial_width=self.initial_width, # Pass initial width
            trunk_color=self.trunk_color,
            leaf_color=self.leaf_color
        )

        logging.info(f"Created {self.name} with angle={self.angle}°, base_length={initial_length:.3f}, initial_width={self.initial_width:.3f}, iterations={self.iterations}")
        return lsystem

    def get_iterations(self) -> int:
        """Returns the number of iterations for this tree."""
        return self.iterations

# --- New Tree Definitions ---

class FractalPlant(TreeDefinition):
    """Classic fractal plant L-System"""
    @property
    def name(self): return "Fractal Plant"
    @property
    def rules(self): return {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
    @property
    def angle(self): return 25.0
    @property
    def base_length_ratio(self): return 0.45
    @property
    def trunk_color(self): return (0.4, 0.2, 0.1)
    @property
    def leaf_color(self): return (0.1, 0.7, 0.1)
    @property
    def iterations(self): return 5 # Needs more iterations
    @property
    def initial_width(self) -> float: return 0.04

class SwampTree(TreeDefinition):
    """A tree with downward and twisting branches, like a mangrove or swamp tree"""
    @property
    def name(self): return "Swamp Tree"
    @property
    def rules(self): return {
        "X": "F[&X][\\X]F[/X]FX",
        "F": ["FF", "F[&F]F", "F[\\F]F"] # Stochastic growth
    }
    @property
    def angle(self): return 30.0
    @property
    def base_length_ratio(self): return 0.35
    @property
    def trunk_color(self): return (0.35, 0.25, 0.15)
    @property
    def leaf_color(self): return [(0.2, 0.4, 0.1), (0.4, 0.6, 0.2)] # Range of swampy greens
    @property
    def iterations(self): return 5
    @property
    def scale(self): return 0.8
    @property
    def initial_width(self) -> float: return 0.06

class CrystalGrowth(TreeDefinition):
    """Tree resembling crystal structures with sharp angles"""
    @property
    def name(self): return "Crystal Growth"
    @property
    def rules(self): return {
        "X": "F[+X]F[-X]F[/X]F[\\X]FX", # More branching directions
        "F": "F" # Keep branches thin
    }
    @property
    def angle(self): return 45.0 # Sharper angles
    @property
    def base_length_ratio(self): return 0.25
    @property
    def trunk_color(self): return (0.6, 0.6, 0.8) # Bluish tint
    @property
    def leaf_color(self): return (0.8, 0.8, 1.0) # Light blue/white "crystals"
    @property
    def iterations(self): return 4 # Fewer iterations, structure is key
    @property
    def scale(self): return 0.7
    @property
    def initial_width(self) -> float: return 0.03

class SpiralCanopy(TreeDefinition):
    """Tree with branches that spiral upwards and form a canopy"""
    @property
    def name(self): return "Spiral Canopy"
    @property
    def rules(self): return {
        "X": "F/[+FX][^FX]F[\\-FX]FX", # Rotate around multiple axes
        "F": "FF"
    }
    @property
    def angle(self): return 22.5
    @property
    def base_length_ratio(self): return 0.40
    @property
    def trunk_color(self): return (0.5, 0.3, 0.1)
    @property
    def leaf_color(self): return [(0.1, 0.5, 0.1), (0.3, 0.8, 0.2)] # Lush green range
    @property
    def iterations(self): return 5
    @property
    def scale(self): return 0.8
    @property
    def initial_width(self) -> float: return 0.055

class SakuraBlossom(TreeDefinition):
    """Inspired by cherry blossoms, more 'X' (leaves/flowers) at the end"""
    @property
    def name(self): return "Sakura Blossom"
    @property
    def rules(self): return {
        "X": "F[+X][-X]FX",
        "F": ["FF", "F[+F-X][-F+X]F"] # Encourage 'X' at branch ends
    }
    @property
    def angle(self): return 28.0
    @property
    def base_length_ratio(self): return 0.38
    @property
    def trunk_color(self): return (0.45, 0.3, 0.25)
    @property
    def leaf_color(self): return [(0.9, 0.7, 0.8), (1.0, 0.8, 0.9)] # Pinkish range
    @property
    def iterations(self): return 5
    @property
    def scale(self): return 0.78
    @property
    def initial_width(self) -> float: return 0.045


class DenseConifer(TreeDefinition):
    """A dense conifer-like tree"""
    @property
    def name(self): return "Dense Conifer"
    @property
    def rules(self): return {
        "X": "F-[[X]+X]+F[+FX]-X",
        "F": "FF"
    }
    @property
    def angle(self): return 25.7
    @property
    def base_length_ratio(self): return 0.42
    @property
    def trunk_color(self): return (0.3, 0.15, 0.05)
    @property
    def leaf_color(self): return (0.0, 0.5, 0.1) # Dark green
    @property
    def iterations(self): return 6 # More iterations for density
    @property
    def scale(self): return 0.75
    @property
    def initial_width(self) -> float: return 0.06


# List of available tree types - Updated with new classes
TREE_TYPES = [
    FractalPlant,
    SwampTree,
    CrystalGrowth,
    SpiralCanopy,
    SakuraBlossom,
    DenseConifer
]

def get_random_tree_type() -> TreeDefinition:
    """Returns an instance of a randomly selected tree type."""
    chosen_type = random.choice(TREE_TYPES)
    tree = chosen_type()
    return tree

def get_tree_by_name(name: str) -> TreeDefinition:
    """Returns a tree instance by name."""
    for tree_class in TREE_TYPES:
        tree_instance = tree_class()
        if tree_instance.name.lower() == name.lower():
            logging.info(f"Created tree by name: {name}")
            return tree_instance

    # Fallback to a default if name not found
    logging.warning(f"Unknown tree type: '{name}', using random tree.")
    return get_random_tree_type() # Return random instead of a fixed default
