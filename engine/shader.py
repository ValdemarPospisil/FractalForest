"""
Modul pro správu shaderů
"""
import moderngl
import numpy as np

class ShaderProgram:
    """Třída pro správu shader programu"""
    
    def __init__(self, ctx, vertex_shader_path, fragment_shader_path):
        self.ctx = ctx
        
        # Načtení shader kódu ze souborů
        with open(vertex_shader_path, 'r') as file:
            vertex_shader = file.read()
            
        with open(fragment_shader_path, 'r') as file:
            fragment_shader = file.read()
            
        # Vytvoření shader programu
        self.program = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
    def use(self):
        """Aktivuje shader program"""
        # V ModernGL není potřeba explicitně aktivovat program
        # Aktivuje se automaticky při nastavování uniformů nebo při vykreslování
        pass
        
    def set_uniform(self, name, value):
        """Nastaví uniform v shader programu"""
        try:
            # Různé typy hodnot vyžadují různé způsoby nastavení
            if isinstance(value, (int, float)):
                self.program[name] = value
            elif isinstance(value, (list, tuple)):
                if len(value) == 2:
                    self.program[name] = tuple(value)
                elif len(value) == 3:
                    self.program[name] = tuple(value)
                elif len(value) == 4:
                    self.program[name] = tuple(value)
                elif len(value) == 16:  # 4x4 matice
                    self.program[name] = tuple(value)
            elif isinstance(value, np.ndarray):
                if value.shape == (4, 4):
                    # 4x4 matice, převést na tuple of floats v column-major order
                    self.program[name] = tuple(value.flatten('F'))
                else:
                    # Ostatní pole, převést na tuple
                    self.program[name] = tuple(value.flatten())
        except KeyError:
            # Ignorovat uniform, který neexistuje v shaderu
            pass
