#version 330 core

// Inputs from vertex shader
in vec3 frag_position;
in vec3 frag_normal;
in vec3 frag_color;  // Color passed from vertex shader

// Output
out vec4 out_color;

// Lighting uniforms
uniform vec3 light_position = vec3(2.0, 5.0, 2.0);
uniform vec3 light_color = vec3(1.0, 1.0, 1.0);
uniform float ambient_strength = 0.2;

// Ground-specific uniforms
uniform bool is_ground = false;
uniform vec3 ground_color1 = vec3(0.3, 0.3, 0.3);
uniform vec3 ground_color2 = vec3(0.5, 0.5, 0.5);

void main() {
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_position - frag_position);
    
    // Ambient
    vec3 ambient = ambient_strength * light_color;
    
    // Diffuse
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;
    
    // Special ground rendering
    if (is_ground) {
        // Create grid pattern
        float grid_size = 1.0;
        vec2 coord = frag_position.xz / grid_size;
        vec2 grid = abs(fract(coord - 0.5) - 0.5) / fwidth(coord);
        float line = min(grid.x, grid.y);
        float grid_intensity = 1.0 - min(line, 1.0);
        
        // Mix between ground colors
        vec3 base_color = mix(ground_color1, ground_color2, grid_intensity);
        out_color = vec4((ambient + diffuse) * base_color, 1.0);
    } 
    // Regular object rendering
    else {
        out_color = vec4((ambient + diffuse) * frag_color, 1.0);
    }
}
