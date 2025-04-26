# version 330
in vec3 in_position;
uniform mat4 projection;
void main() {
  gl_Position = projection * vec4(in_position, 1.0);
}
