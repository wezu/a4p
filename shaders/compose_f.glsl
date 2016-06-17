//GLSL
#version 140
#pragma include "inc_config.glsl"
uniform sampler2D colorTex;
uniform sampler2D blurTex;
uniform sampler2D auxTex;
uniform sampler2D glareTex;
uniform sampler2D flareTex;
uniform sampler2D starTex;
uniform sampler2D lut;

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
    vec4 blured_color=texture(blurTex, uv);
    vec4 aux=texture(auxTex, uv);

    color+=texture(glareTex,uv);
    color+=texture(flareTex,vec2(1.0, 1.0)-uv)*texture(starTex, rotate_uv);
    color=mix(color, blured_color, aux.r);

    #ifndef DISABLE_LUT
    color.rgb=applyColorLUT(lut, color.rgb);
    #endif

    gl_FragColor =color;
    }
