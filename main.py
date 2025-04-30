from ursina import *
import random
import logging
from generation.lsystem import LSystem
from generation.tree import Tree

# Nastavení logování
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fractalforest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Dostupné typy stromů
TREE_TYPES = ["pine", "oak", "bush", "willow", "palm"]

class FractalForestApp(Ursina):
    def __init__(self):
        super().__init__()
        
        # Nastavení okna
        window.title = 'FractalForest'
        window.borderless = False
        window.exit_button.visible = False
        
        # Vytvoření scény
        self.setup_scene()
        
        # Vytvoření UI
        self.setup_ui()
        
        # Generování prvního stromu
        self.generate_random_tree()
        
    def setup_scene(self):
        """Nastavení 3D scény"""
        # Kamera
        self.camera = EditorCamera()
        self.camera.position = (5, 8, 8)
        self.camera.look_at(Vec3(0, 1.5, 0))
        
        # Základní podložka (zem)
        self.ground = Entity(
            model='plane',
            scale=(50, 1, 50),
            color=color.rgb(76, 51, 25),  # hnědá barva
            texture='white_cube',
            texture_scale=(50, 50),
            collider='box'
        )
        
        # Osvětlení
        self.directional_light = DirectionalLight()
        self.directional_light.look_at(Vec3(-0.5, -1, -0.5))
        
        # Text s instrukcemi
        self.instruction_text = Text(
            text="G - nový strom | ESC - konec | WASD + myš - pohyb",
            origin=(0, 0),
            position=(-0.85, 0.47)
        )
        
    def setup_ui(self):
        """Nastavení uživatelského rozhraní"""
        # Panel s informacemi
        self.info_panel = WindowPanel(
            title='Info',
            content=(
                Text('Vytvořeno pomocí Ursina Engine'),
                Button(text='Nový strom', color=color.azure, on_click=self.generate_random_tree),
                Text('', name='tree_type'),
                Text('', name='tree_height'),
                Text('', name='branch_count'),
            ),
            position=window.top_right - Vec2(0.35, 0.05),
            scale=(0.3, 0.4)
        )
        
    def update(self):
        """Aktualizace při každém snímku"""
        # Ukončení aplikace po stisknutí ESC
        if held_keys['escape']:
            application.quit()
        
        # Generování nového stromu po stisknutí G
        if held_keys['g']:
            held_keys['g'] = False  # Reset klávesy aby nedošlo k vícenásobnému volání
            self.generate_random_tree()
    
    def generate_random_tree(self):
        """Generování náhodného stromu z dostupných typů"""
        # Odstranění předchozího stromu, pokud existuje
        if hasattr(self, 'tree_entity') and self.tree_entity:
            destroy(self.tree_entity)
            
        # Výběr náhodného typu stromu
        tree_type = random.choice(TREE_TYPES)
        logger.info(f"Generování nového stromu typu: {tree_type}")
        
        # Nastavení specifických parametrů podle typu stromu
        if tree_type == "pine":
            iterations = 4
            angle = 22.5
            length = 1.0
            color = color.rgb(25, 102, 25)  # tmavě zelená
        elif tree_type == "oak":
            iterations = 4
            angle = 25.0
            length = 1.2
            color = color.rgb(76, 128, 51)  # středně zelená
        elif tree_type == "bush":
            iterations = 3
            angle = 28.0
            length = 0.8
            color = color.rgb(102, 153, 76)  # světle zelená
        elif tree_type == "willow":
            iterations = 4
            angle = 15.0
            length = 1.3
            color = color.rgb(76, 153, 76)  # žluto-zelená
        elif tree_type == "palm":
            iterations = 3
            angle = 25.0
            length = 1.5
            color = color.rgb(51, 128, 51)  # zelená
            
        # Generování L-systému a stromu
        lsystem = LSystem.create_tree_system(tree_type=tree_type, randomness=0.15)
        instructions = lsystem.generate(iterations)
        self.tree = Tree(instructions, angle=angle, length=length, tree_type=tree_type)
        
        # Vytvoření 3D entity stromu
        self.tree_entity = self.tree.create_entity(color=color)
        
        # Aktualizace informací v UI
        self.info_panel.content[2].text = f"Typ: {tree_type.capitalize()}"
        self.info_panel.content[3].text = f"Výška: {self.tree.height:.2f} m"
        self.info_panel.content[4].text = f"Počet větví: {self.tree.branch_count}"

if __name__ == '__main__':
    app = FractalForestApp()
    app.run()
