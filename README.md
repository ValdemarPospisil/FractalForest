# FractalForest

Procedurální generátor 3D lesů s využitím L-systémů.

## Popis

FractalForest je aplikace napsaná v Pythonu, která demonstruje procedurální generování stromů a lesů pomocí L-systémů. Aplikace umožňuje generovat různé typy stromů (jehličnany, listnaté stromy, keře) a vytvářet z nich lesy s nastavitelnou hustotou a velikostí.

## Instalace

### Požadavky
- Python 3.7 nebo novější
- pip

### Postup instalace

1. Naklonujte repozitář:
```
git clone https://github.com/ValdemarPospisil/FractalForest.git
cd FractalForest
```

2. Vytvořte virtuální prostředí:
```
python -m venv venv
source venv/bin/activate  # Pro Linux/Mac
# NEBO
venv\Scripts\activate  # Pro Windows
```

3. Nainstalujte závislosti:
```
pip install -r requirements.txt
```

## Spuštění

```
python main.py
```

## Ovládání

- **WASD** - pohyb kamery
- **Myš** - rozhlížení (v režimu chůze)
- **TAB** - přepínání mezi režimem létání a chůze
- **G** - generování nového lesa
- **ESC** - ukončení aplikace

## Implementace

### L-systémy

L-systémy jsou formální gramatiky používané pro modelování růstu rostlin. V tomto projektu jsou použity pro generování struktury stromů. Každý L-systém je definován:

- **Axiomem** - počátečním řetězcem
- **Pravidly** - pravidly pro přepisování znaků
- **Úhlem** - úhlem pro interpretaci příkazů rotace

### Interpretace L-systémů

Řetězce generované L-systémy jsou interpretovány následovně:

- **F** - tvorba větve (posunutí vpřed)
- **+** - otočení doleva o daný úhel
- **-** - otočení doprava o daný úhel
- **[** - uložení aktuální pozice a orientace na zásobník
- **]** - obnovení pozice a orientace ze zásobníku

### 3D Rendering

Pro vykreslování 3D scény je použit ModernGL, což je moderní Python wrapper pro OpenGL. Stromy jsou reprezentovány jako 3D modely složené z válcových segmentů.

## Struktura projektu

```
FractalForest/
├── engine/         # Renderovací engine
├── generation/     # Generování stromů a lesů
├── shaders/        # GLSL shadery
├── ui/             # Uživatelské rozhraní
├── main.py         # Hlavní soubor aplikace
└── requirements.txt
```

## Licence

Tento projekt je licencován pod MIT licencí - viz soubor LICENSE pro více informací.
