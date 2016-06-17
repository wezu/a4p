//GLSL
#version 140
#pragma include "inc_config.glsl"

uniform sampler2D p3d_Texture0;

in vec4 v_color;
in vec2 uv;

void main()
    {
    vec4 final_color=texture(p3d_Texture0, uv)*v_color;
    //final_color=v_color;
    vec4 final_aux=vec4(0.0, 0.0, 0.0, final_color.a);

    gl_FragData[0]=final_color;
    gl_FragData[1]=final_aux;
    }
