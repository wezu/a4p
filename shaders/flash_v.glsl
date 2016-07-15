//GLSL
#version 140
#pragma include "inc_config.glsl"

in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelMatrixInverseTranspose;


out vec2 uv;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv=p3d_MultiTexCoord0;
    }
