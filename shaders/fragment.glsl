#version 330 core

in vec4 v_color;
in vec3 v_normal;
in vec3 v_position;
out vec4 f_color;

uniform vec3 light_direction = vec3(0.5, 1.0, 0.5);

void main() {
    // Základní osvětlení pro lepší plasticitu
    vec3 normal = normalize(v_normal);
    vec3 light_dir = normalize(light_direction);
    
    // Ambientní složka
    float ambient = 0.4;
    
    // Difúzní složka
    float diff = max(dot(normal, light_dir), 0.0);
    float diffuse = diff * 0.6;
    
    // Výsledná barva s osvětlením
    f_color = v_color * vec4(vec3(ambient + diffuse), 1.0);
}
