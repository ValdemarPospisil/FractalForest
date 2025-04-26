#version 330 core

// Vstupní atributy
in vec3 position;
in vec3 normal;

// Výstupní proměnné pro fragment shader
out vec3 frag_position;
out vec3 frag_normal;

// Uniformní proměnné
uniform mat4 model;      // Model matice
uniform mat4 view;       // Pohledová matice
uniform mat4 projection; // Projekční matice

void main() {
    // Transformace pozice
    vec4 worldPos = model * vec4(position, 1.0);
    frag_position = worldPos.xyz;
    
    // Správná transformace normál pomocí inverzně-transponované model matice
    mat3 normalMatrix = transpose(inverse(mat3(model)));
    frag_normal = normalMatrix * normal;
    
    // Výsledná pozice ve clip space
    gl_Position = projection * view * worldPos;
}
