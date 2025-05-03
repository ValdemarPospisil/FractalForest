#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_color;
layout(location = 2) in vec3 in_normal;

out vec4 v_color;
out vec3 v_normal;
out vec3 v_position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    v_color = vec4(in_color, 1.0);
    v_normal = normalize(mat3(model) * in_normal);
    v_position = vec3(model * vec4(in_position, 1.0));
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}
