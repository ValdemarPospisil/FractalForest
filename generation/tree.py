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
        return 0.05 # Default thicker trunk base

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

        logging.info(f"Created {self.name} with angle={self.angle}°, base_length={initial_length:.3f}, iterations={self.iterations}")
        return lsystem

    def get_iterations(self) -> int:
        """Returns the number of iterations for this tree."""
        return self.iterations

# --- UPRAVENÉ Stávající typy stromů ---

class FractalPlant(TreeDefinition):
    """Classic fractal plant L-System - upraveno pro lepší vyvážení"""
    @property
    def name(self): return "Fractal Plant"
    @property
    def rules(self): return {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
    @property
    def angle(self): return 22.0  # Menší úhel pro menší rozpětí
    @property
    def base_length_ratio(self): return 0.3  # Zmenšeno pro menší výšku
    @property
    def trunk_color(self): return (0.4, 0.2, 0.1)
    @property
    def leaf_color(self): return (0.1, 0.7, 0.1)
    @property
    def iterations(self): return 5
    @property
    def initial_width(self) -> float: return 0.06  # Tlustší kmen

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
    """Tree with branches that spiral upwards and form a canopy - upraveno pro menší výšku"""
    @property
    def name(self): return "Spiral Canopy"
    @property
    def rules(self): return {
        "X": "F/[+FX][^FX]F[\\-FX]FX", # Rotate around multiple axes
        "F": "FF"
    }
    @property
    def angle(self): return 25.0  # Zvětšený úhel pro širší korunu
    @property
    def base_length_ratio(self): return 0.3  # Zmenšeno pro nižší výšku
    @property
    def trunk_color(self): return (0.5, 0.3, 0.1)
    @property
    def leaf_color(self): return [(0.1, 0.5, 0.1), (0.3, 0.8, 0.2)] # Lush green range
    @property
    def iterations(self): return 5  
    @property
    def scale(self): return 0.75  # Menší měřítko pro hustší korunu
    @property
    def initial_width(self) -> float: return 0.06  # Tlustší kmen


class SakuraBlossom(TreeDefinition):
    """Vylepšený Sakura strom s charakteristickým tvarem a hustější korunou"""
    @property
    def name(self): return "Sakura Blossom"
    @property
    def rules(self): return {
        # Mnohem víc větvení s variabilitou do všech směrů
        "X": [
            "F[++X][--X][-X][+X][&&&X][^^^X]FX",
            "F[+X][-X][\\X][/X][&X][^X]FX"
        ],
        # Výrazně složitější větvení pro typickou deštníkovitou korunu
        "F": [
            "FF",
            "F[+F-X][-F+X]F", 
            "F[^FX][&FX][/FX][\\FX]F"  # Přidané větvení do všech směrů
        ]
    }
    @property
    def angle(self): return 22.0  # Menší úhel pro hustší korunu
    @property
    def base_length_ratio(self): return 0.25  # Kratší větve pro kompaktnější vzhled
    @property
    def trunk_color(self): return (0.45, 0.3, 0.25)
    @property
    def leaf_color(self): return [(0.95, 0.75, 0.85), (1.0, 0.85, 0.95)]  # Světlejší růžová pro jarní květy
    @property
    def iterations(self): return 3  # Méně iterací při složitějších pravidlech
    @property
    def scale(self): return 0.8  # Pomalejší zmenšování větví pro lepší hustotu
    @property
    def initial_width(self) -> float: return 0.055


class DenseConifer(TreeDefinition):
    """A dense conifer-like tree - upraveno pro lepší proporce"""
    @property
    def name(self): return "Dense Conifer"
    @property
    def rules(self): return {
        "X": "F-[[X]+X]+F[+FX]-X",
        "F": "FF"
    }
    @property
    def angle(self): return 22.0  # Menší úhel
    @property
    def base_length_ratio(self): return 0.32  # Zmenšená výška
    @property
    def trunk_color(self): return (0.3, 0.15, 0.05)
    @property
    def leaf_color(self): return (0.0, 0.5, 0.1) # Dark green
    @property
    def iterations(self): return 5  # Méně iterací pro menší výšku
    @property
    def scale(self): return 0.78  # Pomalejší zmenšování pro hustší vzhled
    @property
    def initial_width(self) -> float: return 0.06

# ---- NOVÉ TYPY STROMŮ ----


class OakTree(TreeDefinition):
    """Klasický dub s širokou, rozložitou korunou a hustším větvením"""
    @property
    def name(self): return "Oak Tree"
    @property
    def rules(self): return {
        # Výrazně více větvení v různých směrech pro typicky rozložitou korunu dubu
        "X": [
            "F[+++X][---X][+X][-X][&X][^X]FX", 
            "F[++X][--X][&&&X][^^^X]FX"
        ],
        # Stohasticita ve větvích a více větvení
        "F": [
            "FF", 
            "F[+F]F[-F]F",
            "F[/F]F[\\F]F"  # Přidané kroucení kolem Z
        ] 
    }
    @property
    def angle(self): return 25.0  # Větší úhel pro širší korunu
    @property
    def base_length_ratio(self): return 0.32
    @property
    def trunk_color(self): return (0.4, 0.25, 0.12)
    @property
    def leaf_color(self): return [(0.15, 0.55, 0.1), (0.35, 0.65, 0.2)]  # Tmavější zelené variace
    @property
    def iterations(self): return 4  # 4 iterace stačí při složitějších pravidlech
    @property
    def scale(self): return 0.75  # Rychlejší zmenšování pro kompaktnější korunu
    @property
    def initial_width(self) -> float: return 0.07  # Velmi silný kmen typický pro dub


class PineTree(TreeDefinition):
    """Borovice s charakteristickým kónickým tvarem a hustším větvením"""
    @property
    def name(self): return "Pine Tree"
    @property
    def rules(self): return {
        # Víc větvení směrem nahoru a do stran, také s různou hustotou
        "X": [
            "F[++X][--X][&X]F[+X][-X]FX",
            "F[^FX][&FX][+FX][-FX]FX"
        ],
        # Stohasticita ve větvích
        "F": ["FF", "F[+F]F[-F]", "F"]
    }
    @property
    def angle(self): return 20.0  # Menší úhel pro hustší větvení
    @property
    def base_length_ratio(self): return 0.38
    @property
    def trunk_color(self): return (0.35, 0.18, 0.08)
    @property
    def leaf_color(self): return (0.0, 0.5, 0.15)  # Tmavší zelená pro jehličí
    @property
    def iterations(self): return 4  # 4 iterace jsou dostatečné pro hustotu
    @property
    def scale(self): return 0.75  # Rychlejší zmenšování pro kónický tvar
    @property
    def initial_width(self) -> float: return 0.06  # Silnější kmen



class BirchTree(TreeDefinition):
    """Vylepšená bříza s typickým štíhlým tvarem a jemnými větvemi"""
    @property
    def name(self): return "Birch Tree"
    @property
    def rules(self): return {
        # Více větvení do stran s důrazem na vzhůru typický pro břízu
        "X": [
            "F[-X][+X][^X][/X][\\X]FX",
            "F[--X][++X][^X]F[-X][+X]FX"
        ],
        # Přidáno více jemného větvení
        "F": [
            "FF", 
            "F[-F][+F]F",
            "F[^F][&F]F",  # Větvení nahoru/dolů
            "F[/F][\\F]F"  # Větvení s kroucením
        ]
    }
    @property
    def angle(self): return 20.0  # Menší úhel pro jemnější vzhled
    @property
    def base_length_ratio(self): return 0.4  # Delší větve pro štíhlý vzhled
    @property
    def trunk_color(self): return (0.9, 0.9, 0.85)  # Bříza má světlý kmen s jemným nádechem
    @property
    def leaf_color(self): return [(0.5, 0.85, 0.2), (0.7, 0.95, 0.3)]  # Světlejší svěží zelená
    @property
    def iterations(self): return 4
    @property
    def scale(self): return 0.8
    @property
    def initial_width(self) -> float: return 0.04  # Tenčí kmen typický pro břízu


class MapleTree(TreeDefinition):
    """Javor s charakteristickou širokou korunou"""
    @property
    def name(self): return "Maple Tree"
    @property
    def rules(self): return {
        "X": ["F[+++X][---X][+X][-X][^X][&X]FX", "F[++X][--X][&X][^X]FX"],
        "F": ["FF", "F[+F][-F]F"]
    }
    @property
    def angle(self): return 23.0
    @property
    def base_length_ratio(self): return 0.3
    @property
    def trunk_color(self): return (0.4, 0.25, 0.15)
    @property
    def leaf_color(self): return [(0.7, 0.2, 0.1), (0.8, 0.3, 0.0)]  # Podzimní červená
    @property
    def iterations(self): return 4
    @property
    def scale(self): return 0.78
    @property
    def initial_width(self) -> float: return 0.06


class WillowTree(TreeDefinition):
    """Vylepšená vrba s typickými převislými větvemi"""
    @property
    def name(self): return "Willow Tree"
    @property
    def rules(self): return {
        # Více větvení s výrazným sklonem dolů (&&&) a kroucením
        "X": [
            "F[&&&X][&&&\\X][&&&/X][&X]FX",
            "F[&&&+X][&&&-X][&X]FX"
        ],
        # Delší větve s převislým charakterem
        "F": [
            "FF", 
            "F[&F]F[&F]F",  # Více převislých větví
            "F[&\\F]F[&/F]F"  # S kroucením pro přirozený vzhled
        ]
    }
    @property
    def angle(self): return 20.0  # Menší úhel pro hustší převislé větvení
    @property
    def base_length_ratio(self): return 0.38
    @property
    def trunk_color(self): return (0.35, 0.22, 0.1)
    @property
    def leaf_color(self): return (0.5, 0.75, 0.3)  # Světlejší zelená typická pro vrbu
    @property
    def iterations(self): return 4
    @property
    def scale(self): return 0.85  # Pomalejší zmenšování pro delší převislé větve
    @property
    def initial_width(self) -> float: return 0.065  # Silnější kmen pro vyvážení převislých větví


class DeadTree(TreeDefinition):
    """Uschlý strom bez listí"""
    @property
    def name(self): return "Dead Tree"
    @property
    def rules(self): return {
        "X": "F[+X][-X][\\X][/X]X",
        "F": ["FF", "F[+F][-F]F"]
    }
    @property
    def angle(self): return 30.0
    @property
    def base_length_ratio(self): return 0.32
    @property
    def trunk_color(self): return (0.3, 0.25, 0.2)
    @property
    def leaf_color(self): return (0.4, 0.35, 0.3)  # Bez listů, jen suché větve
    @property
    def iterations(self): return 4
    @property
    def scale(self): return 0.78
    @property
    def initial_width(self) -> float: return 0.055

# List of available tree types - Updated with new classes
TREE_TYPES = [
    FractalPlant,
    SwampTree,
    CrystalGrowth,
    SpiralCanopy,
    SakuraBlossom,
    DenseConifer,
    OakTree,
    PineTree,
    BirchTree,
    MapleTree,
    WillowTree,
    DeadTree
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
