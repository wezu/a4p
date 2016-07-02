//GLSL
#version 140
uniform sampler2D input_map;
in vec2 uv;


void main()
    {
    vec2 pixel = vec2(1.0, 1.0)/textureSize(input_map, 0).xy;
    vec2 pixel2 = vec2(pixel.x, -pixel.y);
    vec2 pixel3 = vec2(-pixel.x, pixel.y);
    vec2 pixel4 = -pixel;

    vec4 base_tex=texture(input_map, uv);
    base_tex+=vec4(0.5, 0.5, 0.5, 0.5);
    base_tex*=vec4(0.5, 0.5, 0.5, 0.5);

    //vec4 out_tex =base_tex*0.5;

    vec4 out_tex=base_tex*texture(input_map, uv+pixel);
    out_tex+=base_tex*texture(input_map, uv+pixel2);
    out_tex+=base_tex*texture(input_map, uv+pixel3);
    out_tex+=base_tex*texture(input_map, uv+pixel4);

    out_tex+=base_tex*texture(input_map, uv+pixel*4.0);
    out_tex+=base_tex*texture(input_map, uv+pixel2*4.0);
    out_tex+=base_tex*texture(input_map, uv+pixel3*4.0);
    out_tex+=base_tex*texture(input_map, uv+pixel4*4.0);

    out_tex+=base_tex*texture(input_map, uv+pixel*8.0);
    out_tex+=base_tex*texture(input_map, uv+pixel2*8.0);
    out_tex+=base_tex*texture(input_map, uv+pixel3*8.0);
    out_tex+=base_tex*texture(input_map, uv+pixel4*8.0);



    gl_FragColor = out_tex;
    }

