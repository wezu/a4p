//GLSL
#version 140
#pragma include "inc_config.glsl"
uniform vec2 screen_size;
uniform sampler2D tex;

in vec4 v_color;
flat in vec2 center;
flat in float point_size;

out vec4 final_color;

void main()
    {
    vec2 uv = (gl_FragCoord.xy / screen_size - center) / (point_size / screen_size) + 0.5;
    final_color=texture(tex, uv)*v_color;
    //final_color=v_color;
    }
