#version 120

uniform sampler2DShadow texture0;

void main() {
  gl_FragDepth = shadow2D(texture0, gl_TexCoord[0].xyz).r;
}
