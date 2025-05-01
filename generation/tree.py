# generation/tree.py
import random
import math
from abc import ABC, abstractmethod
from .lsystem import LSystem # Používáme relativní import

class AbstractTree(ABC):
    """Abstraktní základní třída pro definici typů stromů."""

    @abstractmethod
    def get_lsystem(self) -> LSystem:
        """Vrátí instanci LSystem pro tento typ stromu s náhodnými variacemi."""
        pass

    @abstractmethod
    def get_iterations(self) -> int:
        """Vrátí doporučený počet iterací pro tento strom."""
        pass


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
        angle = math.radians(random.uniform(20, 30)) # Náhodný úhel
        scale = random.uniform(0.75, 0.85)          # Náhodný faktor zmenšení
        initial_length = random.uniform(0.08, 0.12)

        return LSystem(axiom, rules, angle, scale, initial_length=initial_length)

    def get_iterations(self) -> int:
        return random.randint(4, 5) # Náhodný počet iterací


class BushyTree(AbstractTree):
    """Konkrétní typ stromu - keřovitější strom."""

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
        angle = math.radians(random.uniform(22, 35)) # Větší rozptyl úhlu
        scale = random.uniform(0.8, 0.9)             # Menší zmenšování = hustší
        initial_length = random.uniform(0.06, 0.1)   # Kratší počáteční délka

        return LSystem(axiom, rules, angle, scale, initial_length=initial_length)

    def get_iterations(self) -> int:
        return random.randint(3, 4) # Méně iterací pro keř

# Seznam dostupných typů stromů
TREE_TYPES = [StandardTree, BushyTree]

def get_random_tree_type() -> AbstractTree:
    """Vrátí instanci náhodně vybraného typu stromu."""
    chosen_type = random.choice(TREE_TYPES)
    return chosen_type() # Vytvoří instanci vybrané třídy
