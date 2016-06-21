//GLSL
#version 140
#pragma include "inc_config.glsl"
uniform sampler2D colorTex;
#if defined(ENABLE_BLUR) || defined(ENABLE_GLARE)|| defined(ENABLE_FLARE)|| defined(ENABLE_DISTORTION)
uniform sampler2D auxTex;
#endif
#ifdef ENABLE_BLUR
uniform sampler2D blurTex;
uniform sampler2D dofTex;
#endif

#ifdef ENABLE_GLARE
uniform sampler2D glareTex;
#endif

#ifdef ENABLE_FLARE
uniform sampler2D flareTex;
uniform sampler2D starTex;
#endif

#ifdef ENABLE_LUT
uniform sampler2D lut;
#endif

in vec2 uv;
in vec2 time_uv;
in vec2 rotate_uv;

vec3 applyColorLUT(sampler2D lut, vec3 color)
    {
    float lutSize = float(textureSize(lut, 0).y);
    color = clamp(color, vec3(0.5 / lutSize), vec3(1.0 - 0.5 / lutSize));
    vec2 texcXY = vec2(color.r * 1.0 / lutSize, 1.0 - color.g);

    int frameZ = int(color.b * lutSize);
    float offsZ = fract(color.b * lutSize);

    vec3 sample1 = textureLod(lut, texcXY + vec2((frameZ) / lutSize, 0), 0).rgb;
    vec3 sample2 = textureLod(lut, texcXY + vec2( (frameZ + 1) / lutSize, 0), 0).rgb;

    return mix(sample1, sample2, offsZ);
    }

void main()
    {
    vec4 color=texture(colorTex,uv);
    #if defined(ENABLE_BLUR) || defined(ENABLE_GLARE)|| defined(ENABLE_FLARE)|| defined(ENABLE_DISTORTION)
    vec4 aux=texture(auxTex, uv);
    #endif


    #ifdef ENABLE_GLARE
    color+=texture(glareTex,uv);
    #endif

    #ifdef ENABLE_FLARE
    color+=texture(flareTex,vec2(1.0, 1.0)-uv)*texture(starTex, rotate_uv);
    #endif

    #ifdef ENABLE_BLUR
    vec4 blured_color=texture(blurTex, uv);
    float dof=texture(dofTex, rotate_uv).r;
    color=mix(color, blured_color, aux.r*dof);
    #endif

    #ifdef ENABLE_LUT
    color.rgb=applyColorLUT(lut, color.rgb);
    #endif

    gl_FragColor =color;
    }
