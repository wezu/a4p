#version 150

#pragma include "inc_config.glsl"

#ifndef DISABLE_SHADOW_SIZE
struct p3d_LightSourceParameters {
  // Primary light color.
  vec4 color;

  // Light color broken up into components, for compatibility with legacy shaders.
  vec4 ambient;
  vec4 diffuse;
  vec4 specular;

  // View-space position.  If w=0, this is a directional light, with
  // the xyz being -direction.
  vec4 position;

  // Spotlight-only settings
  vec3 spotDirection;
  float spotExponent;
  float spotCutoff;
  float spotCosCutoff;

  // Individual attenuation constants
  float constantAttenuation;
  float linearAttenuation;
  float quadraticAttenuation;

  // constant, linear, quadratic attenuation in one vector
  vec3 attenuation;

  // Shadow map for this light source
  sampler2DShadow shadowMap;

  // Transforms vertex coordinates to shadow map coordinates
  mat4 shadowMatrix;
};

uniform p3d_LightSourceParameters shadow_caster;
#endif

uniform vec4 light_color[100];
uniform vec4 light_pos[100];
uniform vec4 light_att[100];
uniform int num_lights;
uniform vec3 camera_pos;
uniform vec3 ambient;
uniform vec3 light_vec;
uniform vec3 light_vec_color;
uniform vec4 fog;


uniform sampler2D p3d_Texture0; //rgba color texture
uniform sampler2D p3d_Texture1; //rgba normal+gloss texture

in vec2 uv;
in vec4 world_pos;
in vec3 normal;

#ifndef DISABLE_SHADOW_SIZE
in vec4 shadow_uv;
#endif


float textureProjSoft(sampler2DShadow tex, vec4 uv, float bias, float blur)
                    {
                    float result = textureProj(tex, uv, bias);
                    result += textureProj(tex, vec4(uv.xy + vec2( -0.326212, -0.405805)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(-0.840144, -0.073580)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(-0.695914, 0.457137)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(-0.203345, 0.620716)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(0.962340, -0.194983)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(0.473434, -0.480026)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(0.519456, 0.767022)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(0.185461, -0.893124)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(0.507431, 0.064425)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(0.896420, 0.412458)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(-0.321940, -0.932615)*blur, uv.z-bias, uv.w));
                    result += textureProj(tex, vec4(uv.xy + vec2(-0.791559, -0.597705)*blur, uv.z-bias, uv.w));
                    return result/13.0;
                    }

//TBN by Chris­t­ian Schuler from http://www.thetenthplanet.de/archives/1180
mat3 cotangent_frame( vec3 N, vec3 p, vec2 uv )
    {
    // get edge vectors of the pixel triangle
    vec3 dp1 = dFdx( p );
    vec3 dp2 = dFdy( p );
    vec2 duv1 = dFdx( uv );
    vec2 duv2 = dFdy( uv );

    // solve the linear system
    vec3 dp2perp = cross( dp2, N );
    vec3 dp1perp = cross( N, dp1 );
    vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
    vec3 B = dp2perp * duv1.y + dp1perp * duv2.y;

    // construct a scale-invariant frame
    float invmax = inversesqrt( max( dot(T,T), dot(B,B) ) );
    return mat3( T * invmax, B * invmax, N );
    }

vec3 perturb_normal( vec3 N, vec3 V, vec2 texcoord )
    {
    // assume N, the interpolated vertex normal and
    // V, the view vector (vertex to eye)
    vec3 map = (texture( p3d_Texture1, texcoord ).xyz)*2.0-1.0;
    mat3 TBN = cotangent_frame( N, -V, texcoord );
    return normalize( TBN * map );
    }


void main()
    {
    vec3 color=vec3(0.0, 0.0, 0.0);
    vec4 color_map=texture(p3d_Texture0,uv);
    //vec4 color_map=vec4(1.0, 1.0, 1.0, 1.0);
    float gloss=texture(p3d_Texture1,uv).a;
    vec3 up= vec3(0.0,0.0,1.0);
    float specular =0.0;
    vec3 N=normalize(normal);
    vec3 V = normalize(world_pos.xyz - camera_pos);

    N = perturb_normal( N, V, uv);

    //lights...
    //...directional
    color+=light_vec_color*max(dot(N,light_vec), 0.0);
    specular +=pow(max(dot(reflect(light_vec,N), V), 0.0), 100.0)*gloss;
    //..point
    vec3 L;
    vec3 R;
    float att;
    float ldist;
    for (int i=0; i<num_lights; ++i)
        {
        //diffuse
        L = normalize(light_pos[i].xyz-world_pos.xyz);
        att=pow(distance(world_pos.xyz, light_pos[i].xyz), 2.0);
        att =clamp(1.0 - att/(light_pos[i].w), 0.0, 1.0);
        //lambert
        color+=light_color[i].rgb*max(dot(N,L), 0.0)*att;
        //half lambert
        //color+=light_color[i].rgb*pow((dot(N,L)*0.5)+0.5, 2.0)*att;
        //specular
        R=reflect(L,N)*att;
        specular +=pow(max(dot(R, V), 0.0), 128.0)*light_color[i].a*gloss;
        }

    //...spot
    //no spotlights!

    //add spec to dif
    color+=specular;

    //shadows
    #ifndef DISABLE_SHADOW_SIZE
        #ifndef SHADOW_BLUR
        color*= textureProj(shadow_caster.shadowMap,vec4(shadow_uv.xy, shadow_uv.z-0.0001, shadow_uv.w));
        #else
        color*=textureProjSoft(shadow_caster.shadowMap, shadow_uv, 0.0001, SHADOW_BLUR);
        #endif
    #endif

    //...ambient
    //color+= ambient;
    color+= ambient+max(dot(N,up), -0.2)*ambient;

    //fog
    float fog_factor=distance(world_pos.xyz,camera_pos);
    float blur_factor=clamp((fog_factor*0.01), 0.0, 1.0);
    fog_factor=clamp((fog_factor*0.003)-0.1, 0.0, 1.0);
    //final color with fog
    vec4 final_color=vec4(mix(color*color_map.rgb, fog.rgb, fog_factor), color_map.a);
    vec4 final_aux=vec4(blur_factor, specular, 0.0,final_color.a);
    gl_FragData[0]=final_color;
    gl_FragData[1]=final_aux;
    }
