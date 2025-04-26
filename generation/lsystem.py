"""
Implementace L-systémů pro generování stromů
"""
import random
import logging

logger = logging.getLogger(__name__)

class LSystem:
    """
    Třída pro implementaci L-systémů
    L-systémy jsou formální gramatiky používané pro modelování růstu rostlin
    """
    
    def __init__(self, axiom="F", rules=None, angle=25.0):
        """
        Inicializace L-systému
        
        Parametry:
        - axiom: počáteční řetězec
        - rules: slovník pravidel pro přepisování, např. {"F": "F[+F]F[-F]F"}
        - angle: úhel natočení v stupních (používá se při interpretaci symbolů + a -)
        """
        self.axiom = axiom
        self.rules = rules or {}
        self.angle = angle
        
    def generate(self, iterations):
        """
        Generuje řetězec aplikováním pravidel na axiom ve stanoveném počtu iterací
        
        Parametry:
        - iterations: počet iterací přepisování
        
        Vrací:
        - výsledný řetězec po aplikaci pravidel
        """
        result = self.axiom
        for i in range(iterations):
            logger.debug(f"L-System iteration {i+1}/{iterations}, length: {len(result)}")
            result = self._apply_rules(result)
        
        logger.debug(f"Final L-System string length: {len(result)}")
        return result
    
    def _apply_rules(self, string):
        """
        Aplikuje přepisovací pravidla na vstupní řetězec
        
        Parametry:
        - string: vstupní řetězec
        
        Vrací:
        - nový řetězec po aplikaci pravidel
        """
        result = ""
        for char in string:
            # Pokud pro znak existuje pravidlo, použije ho, jinak zachová znak
            result += self.rules.get(char, char)
        return result
    
    def add_randomness(self, amount=0.2):
        """
        Přidá náhodnost do pravidel L-systému
        
        Parametry:
        - amount: míra náhodnosti (0.0 - 1.0)
        """
        new_rules = {}
        for symbol, replacement in self.rules.items():
            # Pro každý znak v pravidlech přidáme varianty
            variants = []
            variants.append(replacement)  # Původní pravidlo
            
            # Vytvoření variací pravidla
            if "+" in replacement and "-" in replacement:
                # Prohození + a - v některých částech
                varied = ""
                for c in replacement:
                    if c == "+" and random.random() < amount:
                        varied += "-"
                    elif c == "-" and random.random() < amount:
                        varied += "+"
                    else:
                        varied += c
                variants.append(varied)
                
            # Přidání náhodného natočení
            varied = ""
            for c in replacement:
                if c == "F" and random.random() < amount:
                    # Přidání náhodného natočení před F
                    if random.random() < 0.5:
                        varied += "+"
                    else:
                        varied += "-"
                varied += c
            variants.append(varied)
            
            # Výběr náhodné varianty jako nového pravidla
            new_rules[symbol] = random.choice(variants)
            
        self.rules = new_rules
        
    @classmethod
    def create_tree_system(cls, tree_type="pine", randomness=0.1):
        """
        Vytvoří L-systém pro konkrétní typ stromu
        
        Parametry:
        - tree_type: typ stromu (pine, oak, bush, ...)
        - randomness: míra náhodnosti v pravidlech (0.0 - 1.0)
        
        Vrací:
        - instance LSystem pro daný typ stromu
        """
        if tree_type == "pine":
            # Jehličnan - vysoký s pravidelnými větvemi
            system = cls(
                axiom="F",
                rules={
                    "F": "FF[+F][-F][+++F][---F]F",
                    "X": "F[-FX]+FX"
                },
                angle=20.0
            )
        elif tree_type == "oak":
            # Listnatý strom - široká koruna
            system = cls(
                axiom="F",
                rules={
                    "F": "FF[++F][-F][--F]F",
                    "X": "F-[[X]+X]+F[+FX]-X"
                },
                angle=25.0
            )
        elif tree_type == "bush":
            # Keř - nízký s hustými větvemi
            system = cls(
                axiom="FFFFF",  # Start with a short trunk
                rules={
                    "F": "F[+F]F[-F][+++F][---F]F"
                },
                angle=35.0  # Wider angle for more spread-out branches
            )
        elif tree_type == "willow":
            # Vrba - dlouhé převislé větve
            system = cls(
                axiom="F",
                rules={
                    "F": "FF[-F][-F][-F][-F]"
                },
                angle=15.0
            )
        elif tree_type == "palm":
            # Palma - vysoký kmen s korunou nahoře
            system = cls(
                axiom="FFFFF[X]",
                rules={
                    "F": "FF",
                    "X": "[-FX][+FX][--FX][++FX]"
                },
                angle=25.0
            )
        else:
            # Výchozí strom
            system = cls(
                axiom="F",
                rules={
                    "F": "FF[+F]F[-F]F"
                },
                angle=25.0
            )
            
        # Log the selected tree type and rules
        logger.info(f"Created L-system for tree type: {tree_type}")
        logger.info(f"Starting rules: {system.rules}")
            
        # Přidání náhodnosti
        if randomness > 0:
            system.add_randomness(randomness)
            logger.info(f"Applied randomness ({randomness}). Updated rules: {system.rules}")
            
        return system
