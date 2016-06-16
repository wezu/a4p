//GLSL
#version 140
#pragma include "inc_config.glsl"
uniform sampler2D p3d_Texture0; //clouds.r, stars.g nothing.b, sun.a

in vec3 vpos;
in vec2 uv0;
in vec2 uv1;
in vec2 uv2;
in vec2 uv3;

uniform vec4 sunColor;
uniform vec4 skyColor;
uniform vec4 cloudColor;
uniform vec4 fog;

out vec4 final_color;

void main()
    {
    float blend=clamp((vpos.z-20.0)*0.01, 0.0, 1.0);
    float blend2=clamp((vpos.z)*0.033, 0.0, 1.0);

    vec4 tex1=texture(p3d_Texture0,uv0.xy);//clouds 1
    vec4 tex2=texture(p3d_Texture0,uv1.xy);//clouds 2
    vec4 tex3=texture(p3d_Texture0,uv2.xy); //sun
    vec4 tex4=texture(p3d_Texture0,uv3.xy); //stars
    float stars=tex4.g*(1.0-skyColor.a);
    vec4 out_color=mix(vec4(fog.rgb, 1.0),vec4(skyColor.rgb, 1.0),blend) +stars;
    float cloud_alpha=clamp(cloudColor.a, 0.0, 0.7);
    vec4 cloud=((cloudColor-out_color)*(tex1.r*tex2.r)*blend)*cloud_alpha;
    float sun=tex3.a*(1.0-(tex1.r*tex2.r)*blend);
    out_color+=cloud;
    out_color=mix(out_color, sunColor*2.5, sun);
    out_color=mix(fog, out_color, blend2);
    sun=mix(0.0, sun, blend2);
    out_color.a=1.0;
    final_color=out_color;
    //gl_FragData[1]=vec4(0.0, 1.0,pow(sun*0.9, 5.0),0.5);
    }

