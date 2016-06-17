//GLSL
#version 140
uniform sampler2D input_map;
in vec2 uv;
in vec4 uv01;
in vec4 uv23;
in vec4 uv45;
in vec4 uv67;
in vec4 uv89;
in vec4 uv1011;

void main()
    {
    vec4 out_tex= texture(input_map, uv);
    //Hardcoded blur
    out_tex += texture(input_map, uv01.xy);
    out_tex += texture(input_map, uv01.zw);
    out_tex += texture(input_map, uv23.xy);
    out_tex += texture(input_map, uv23.zw);
    out_tex += texture(input_map, uv45.xy);
    out_tex += texture(input_map, uv45.zw);
    out_tex += texture(input_map, uv67.xy);
    out_tex += texture(input_map, uv67.zw);
    out_tex += texture(input_map, uv89.xy);
    out_tex += texture(input_map, uv89.zw);
    out_tex += texture(input_map, uv1011.xy);
    out_tex += texture(input_map, uv1011.zw);
    out_tex/=13.0;
    gl_FragColor = out_tex;
    }

