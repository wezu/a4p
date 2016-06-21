//GLSL
#version 140
uniform sampler2D auxTex;
uniform sampler2D colorTex;
uniform sampler2D blurAuxTex;

in vec2 uv;

void main()
    {
    vec4 blured_aux=texture(blurAuxTex,uv);
    vec4 aux=texture(auxTex, uv);
    vec4 color=texture(colorTex, uv);

    float specfactor=blured_aux.g+aux.g;

    vec3 gray = vec3(dot(vec3(0.2126,0.7152,0.0722), color.rgb));
    color= vec4(mix(color.rgb, gray, 0.5), 1.0);
    //color-=0.2;
    color=clamp(color, 0.0, 1.0);
    //color*=2.0;
    gl_FragColor =color*specfactor;
    }

