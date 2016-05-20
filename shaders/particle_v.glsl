//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrixInverse;
uniform vec2 screen_size;
uniform float  radius;
uniform vec3 camera_pos;

in vec4 p3d_Vertex;
in vec4 color;

out vec4 v_color;
flat out vec2 center;
flat out float point_size;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;    
    float dist =distance(p3d_Vertex.xyz,camera_pos);
    point_size = (radius*screen_size.y*0.3)/ dist;
    gl_PointSize = point_size;
    center = (gl_Position.xy / gl_Position.w * 0.5 + 0.5);
    v_color=color;
    }
