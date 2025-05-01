import random
import math
import logging
from abc import ABC, abstractmethod
from .lsystem import LSystem # Používáme relativní import

class TreeParams:
    """Třída pro definici parametrů stromu."""
    def __init__(self, 
                 min_angle=20, max_angle=30,      # Rozsah úhlů
                 min_scale=0.75, max_scale=0.85,  # Rozsah škálování
                 min_length=0.08, max_length=0.12, # Rozsah počáteční délky
                 min_width=0.02, max_width=0.04,  # Rozsah počáteční šířky
                 min_iterations=4, max_iterations=5, # Rozsah iterací
                 trunk_color=(0.55, 0.27, 0.07),  # Barva kmene (hnědá)
                 leaf_color_range=((0.0, 0.6, 0.0), (0.0, 0.9, 0.0)) # Rozsah barev listů
                ):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.min_length = min_length
        self.max_length = max_length
        self.min_width = min_width
        self.max_width = max_width
        self.min_iterations = min_iterations
        self.max_iterations = max_iterations
        self.trunk_color = trunk_color
        self.leaf_color_range = leaf_color_range

class AbstractTree(ABC):
    """Abstraktní základní třída pro definici typů stromů."""

    def __init__(self, params=None):
        """Inicializuje strom s danými parametry nebo výchozími hodnotami."""
        self.params = params if params else TreeParams()
        logging.debug(f"Tree initialized with angle range: {self.params.min_angle}-{self.params.max_angle}")

    @abstractmethod
    def get_lsystem(self) -> LSystem:
        """Vrátí instanci LSystem pro tento typ stromu s náhodnými variacemi."""
        pass

    def get_iterations(self) -> int:
        """Vrátí doporučený počet iterací pro tento strom."""
        iterations = random.randint(self.params.min_iterations, self.params.max_iterations)
        logging.debug(f"Using {iterations} iterations for tree")
        return iterations

    def _get_random_values(self):
        """Vrátí náhodné hodnoty pro parametry stromu."""
        angle = math.radians(random.uniform(self.params.min_angle, self.params.max_angle))
        scale = random.uniform(self.params.min_scale, self.params.max_scale)
        length = random.uniform(self.params.min_length, self.params.max_length)
        width = random.uniform(self.params.min_width, self.params.max_width)
        
        logging.debug(f"Generated random tree values: angle={angle}, scale={scale}, length={length}, width={width}")
        return angle, scale, length, width


class StandardTree(AbstractTree):
    """Konkrétní typ stromu - standardní rozvětvený strom."""

    def get_lsystem(self) -> LSystem:
        axiom = "X"
        rules = {
            # Více pravidel pro variabilitu větvení
            "X": random.choice([
                "F-[[X]+X]+F[+FX]-X",
                "F[+X]F[-X]+X",
                "F[/X][\\X]F[^X]&X",
                "F[&X][^X]F[+X]-X"
            ]),
            "F": random.choice(["FF", "F"]) # Někdy se větev neprodlouží
        }
        
        angle, scale, length, width = self._get_random_values()
        
        logging.info(f"Created StandardTree with angle={math.degrees(angle):.1f}°, scale={scale:.2f}")
        return LSystem(axiom, rules, angle, scale, initial_length=length, initial_width=width)


class BushyTree(AbstractTree):
    """Konkrétní typ stromu - keřovitější strom."""

    def __init__(self, params=None):
        """Inicializuje keřovitý strom s vlastními nebo výchozími parametry."""
        # Vlastní parametry pro keřovitý strom, pokud nejsou zadány
        if not params:
            params = TreeParams(
                min_angle=22, max_angle=35,     # Větší rozptyl úhlu
                min_scale=0.8, max_scale=0.9,   # Menší zmenšování = hustší
                min_length=0.06, max_length=0.1, # Kratší počáteční délka
                min_iterations=3, max_iterations=4 # Méně iterací pro keř
            )
        super().__init__(params)

    def get_lsystem(self) -> LSystem:
        axiom = "F" # Začínáme rovnou kmenem
        rules = {
            # Jednodušší pravidlo, více přímého větvení
            "F": random.choice([
                "F[+F][-F][/F][\\F]F", # Větvení do více směrů
                "FF-[-F+F+F]+[+F-F-F]",
                "F[&F][^F]F[+F]-F"
                ]),
            # Můžeme přidat i pravidlo pro X, pokud ho použijeme v F
            # "X": "..."
        }
        
        angle, scale, length, width = self._get_random_values()
        
        logging.info(f"Created BushyTree with angle={math.degrees(angle):.1f}°, scale={scale:.2f}")
        return LSystem(axiom, rules, angle, scale, initial_length=length, initial_width=width)


class WeepingTree(AbstractTree):
    """Nový typ stromu - převislý strom s větvemi klesajícími dolů."""
    
    def __init__(self, params=None):
        """Inicializuje převislý strom s vlastními nebo výchozími parametry."""
        if not params:
            params = TreeParams(
                min_angle=15, max_angle=25,      # Menší úhly pro dlouhé převislé větve
                min_scale=0.8, max_scale=0.9,    # Pomalejší zmenšování pro delší větve
                min_length=0.1, max_length=0.15, # Delší větve
                min_iterations=4, max_iterations=5,
                leaf_color_range=((0.0, 0.5, 0.0), (0.1, 0.7, 0.1)) # Tmavší zelená
            )
        super().__init__(params)
    
    def get_lsystem(self) -> LSystem:
        axiom = "F" # Začínáme kmenem
        rules = {
            # Pravidla pro převislý strom - větve se stáčejí dolů
            "F": random.choice([
                "F[+&F][-&F][/&F][\\&F]F",  # Větvení do stran a dolů
                "FF[+&F][-&F]F",            # Jednodušší převislé větvení
                "F[\\&F][/&F]F"             # Symetrické převislé větvení
            ])
        }
        
        angle, scale, length, width = self._get_random_values()
        
        logging.info(f"Created WeepingTree with angle={math.degrees(angle):.1f}°, scale={scale:.2f}")
        return LSystem(axiom, rules, angle, scale, initial_length=length, initial_width=width)


class TallTree(AbstractTree):
    """Nový typ stromu - vysoký tenký strom s omezeným větvením."""
    
    def __init__(self, params=None):
        """Inicializuje vysoký strom s vlastními nebo výchozími parametry."""
        if not params:
            params = TreeParams(
                min_angle=10, max_angle=20,      # Menší úhly pro užší korunu
                min_scale=0.7, max_scale=0.8,    # Rychlejší zmenšování
                min_length=0.15, max_length=0.2, # Delší počáteční kmen
                min_width=0.02, max_width=0.03,  # Tenčí
                min_iterations=5, max_iterations=6 # Více iterací
            )
        super().__init__(params)
    
    def get_lsystem(self) -> LSystem:
        axiom = "F" # Začínáme kmenem
        rules = {
            # Pravidla pro vysoký štíhlý strom
            "F": random.choice([
                "FF[+F][-F]",                # Jednodušší větvení
                "FFF[+F][-F]F",              # Delší kmen
                "FF[+F]F[-F]"                # Asymetrické větvení
            ])
        }
        
        angle, scale, length, width = self._get_random_values()
        
        logging.info(f"Created TallTree with angle={math.degrees(angle):.1f}°, scale={scale:.2f}")
        return LSystem(axiom, rules, angle, scale, initial_length=length, initial_width=width)


# Seznam dostupných typů stromů
TREE_TYPES = [StandardTree, BushyTree, WeepingTree, TallTree]

def get_random_tree_type() -> AbstractTree:
    """Vrátí instanci náhodně vybraného typu stromu."""
    chosen_type = random.choice(TREE_TYPES)
    tree = chosen_type() # Vytvoří instanci vybrané třídy
    logging.info(f"Selected tree type: {tree.__class__.__name__}")
    return tree


def get_tree_by_name(name: str) -> AbstractTree:
    """Vrátí instanci stromu podle jména třídy."""
    tree_map = {cls.__name__: cls for cls in TREE_TYPES}
    if name in tree_map:
        tree = tree_map[name]()
        logging.info(f"Created tree by name: {name}")
        return tree
    else:
        logging.warning(f"Unknown tree type: {name}, using StandardTree")
        return StandardTree()
