#version 330 core

// Input attributes
in vec3 position;
in vec3 normal;

// Output to fragment shader
out vec3 frag_position;
out vec3 frag_normal;
out vec3 frag_color;  // Added for ground plane coloring

// Uniforms
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Transform position
    vec4 worldPos = model * vec4(position, 1.0);
    frag_position = worldPos.xyz;
    
    // Transform normal
    mat3 normalMatrix = transpose(inverse(mat3(model)));
    frag_normal = normalize(normalMatrix * normal);
    
    
    // Final position
    gl_Position = projection * view * worldPos;
}
