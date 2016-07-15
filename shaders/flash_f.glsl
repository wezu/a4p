#version 150

#pragma include "inc_config.glsl"


uniform sampler2D p3d_Texture0; //rgba color texture

in vec2 uv;

void main()
    {
    vec4 color_map=texture(p3d_Texture0,uv);

    gl_FragData[0]=color_map;


    #if defined(ENABLE_BLUR) || defined(ENABLE_GLARE)|| defined(ENABLE_FLARE)|| defined(ENABLE_DISTORTION)
    float glow=dot(vec3(1.0, 1.0, 1.0), color_map.rgb);
    vec4 final_aux=vec4(0.0, glow, 0.0,color_map.a);
    gl_FragData[1]=final_aux;
    #endif
    }
