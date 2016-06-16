//GLSL
#version 140
#pragma include "inc_config.glsl"

uniform sampler2D p3d_Texture0;
uniform sampler2D strip;
uniform float osg_FrameTime;

in vec4 v_color;
in vec2 uv;
in vec4 v_pos;

out vec4 final_color;

void main()
    {
    vec4 strip_tex=texture(strip, vec2(v_pos.r*4.0, v_pos.g*0.4+osg_FrameTime*0.3));
    vec2 moved_uv=uv+strip_tex.r*0.02;
    vec4 tex=texture(p3d_Texture0, moved_uv);

    final_color=vec4(v_color.rgb+strip_tex.rgb, tex.a);
    }
