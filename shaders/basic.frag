#version 330 core

// Vstupní proměnné z vertex shaderu
in vec3 frag_position;
in vec3 frag_normal;

// Výstupní proměnná - barva fragmentu
out vec4 frag_color;

// Uniformní proměnné pro osvětlení
uniform vec3 light_position;  // Pozice světla
uniform vec3 light_color;     // Barva světla
uniform float ambient_strength;  // Síla ambientního světla

// Parametry materiálu (později mohou být uniformy)
vec3 object_color = vec3(0.3, 0.5, 0.2);  // Základní barva objektu (zelená pro stromy)

void main() {
    // Normalizace normály (mohla být změněna interpolací)
    vec3 norm = normalize(frag_normal);
    
    // Výpočet směru světla
    vec3 light_dir = normalize(light_position - frag_position);
    
    // Ambientní složka
    vec3 ambient = ambient_strength * light_color;
    
    // Difuzní složka (Lambert)
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;
    
    // Kombinace složek světla
    vec3 result = (ambient + diffuse) * object_color;
    
    // Výsledná barva fragmentu
    frag_color = vec4(result, 1.0);
}
