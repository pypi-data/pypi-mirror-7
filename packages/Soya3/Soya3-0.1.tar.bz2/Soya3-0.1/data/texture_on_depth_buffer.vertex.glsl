#version 120

uniform int lighting_mode;
uniform int fog_type;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  gl_TexCoord[0] = gl_MultiTexCoord0;
}
