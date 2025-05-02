import random
import math
import logging
from abc import ABC, abstractmethod
from .lsystem import LSystem # Používáme relativní import

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
    
    def get_lsystem(self) -> LSystem:
        """Vrátí instanci LSystem pro tento typ stromu s náhodnými variacemi."""
        # Vyber náhodné pravidlo z dostupných možností pro každý symbol
        selected_rules = {}
        for symbol, rule_options in self.rules.items():
            if isinstance(rule_options, list):
                selected_rules[symbol] = random.choice(rule_options)
            else:
                selected_rules[symbol] = rule_options
        
        # Aplikuj náhodné variace na úhel
        final_angle = math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
        
        # Aplikuj náhodné variace na délku
        final_length = self.base_length * (1 + random.uniform(-self.random_length_variation, self.random_length_variation))
        
        # Vytvoř L-systém s vybranými parametry
        lsystem = LSystem(
            axiom=self.axiom,
            rules=selected_rules,
            angle=final_angle,
            scale=self.length_ratio,
            initial_length=final_length,
            initial_width=self.base_thickness,
            trunk_color=self.color[:3]  # Jen RGB komponenty pro kmen
        )
        
        logging.info(f"Created {self.name} with angle={math.degrees(final_angle):.1f}°, scale={self.length_ratio:.2f}")
        return lsystem
    
    def get_iterations(self) -> int:
        """Vrátí počet iterací pro tento strom."""
        return self.iterations


class StandardTree(TreeDefinition):
    """Definice standardního stromu"""
    
    @property
    def name(self):
        return "Standardní strom"
    
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
        return random.randint(4, 5)
    
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
        return 3.0
    
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
        return [0.55, 0.27, 0.07, 1.0]


class BushyTree(TreeDefinition):
    """Definice keřovitého stromu"""
    
    @property
    def name(self):
        return "Keřovitý strom"
    
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
        return 4.0
    
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
        return [0.55, 0.27, 0.07, 1.0]


class WeepingTree(TreeDefinition):
    """Definice převislého stromu"""
    
    @property
    def name(self):
        return "Převislý strom"
    
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
        return random.randint(4, 5)
    
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
        return 3.0
    
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
        return [0.55, 0.27, 0.07, 1.0]


# Přidejte nové typy stromů podle předlohy
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
        return [0.45, 0.25, 0.1, 1.0]


# Seznam dostupných typů stromů
TREE_TYPES = [StandardTree, BushyTree, WeepingTree, TreeType1, TreeType2]

def get_random_tree_type() -> TreeDefinition:
    """Vrátí instanci náhodně vybraného typu stromu."""
    chosen_type = random.choice(TREE_TYPES)
    tree = chosen_type() # Vytvoří instanci vybrané třídy
    logging.info(f"Selected tree type: {tree.name}")
    return tree


def get_tree_by_name(name: str) -> TreeDefinition:
    """Vrátí instanci stromu podle jména."""
    for tree_class in TREE_TYPES:
        tree_instance = tree_class()
        if tree_instance.name.lower() == name.lower():
            logging.info(f"Created tree by name: {name}")
            return tree_instance
    
    # Pokud nenajdeme strom s daným jménem, vrátíme standardní strom
    logging.warning(f"Unknown tree type: {name}, using StandardTree")
    return StandardTree()
