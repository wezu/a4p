//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;

in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec4 p3d_Color;

out vec4 v_color;
out vec2 uv;
out vec4 v_pos;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;    
    uv=p3d_MultiTexCoord0;
    v_color=p3d_Color;
    v_pos=gl_Position;
    }
