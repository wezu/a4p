//GLSL
#version 140
#pragma include "inc_config.glsl"
uniform vec2 screen_size;
uniform sampler2D tex;

in vec4 v_color;
flat in vec2 center;
flat in float point_size;

void main()
    {
    vec2 uv = (gl_FragCoord.xy / screen_size - center) / (point_size / screen_size) + 0.5;
    vec4 final_color=texture(tex, uv)*v_color;
    //final_color=v_color;


    gl_FragData[0]=final_color;
    #if defined(ENABLE_BLUR) || defined(ENABLE_GLARE)|| defined(ENABLE_FLARE)|| defined(ENABLE_DISTORTION)
    vec4 final_aux=vec4(0.0, 0.10, 0.0, final_color.a);
    gl_FragData[1]=final_aux;
    #endif
    }
