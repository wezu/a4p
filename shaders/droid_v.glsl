//GLSL
#version 140

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

in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
//uniform mat4 p3d_ModelMatrixInverseTranspose;
uniform mat4 tpose_model_to_world; //pre 1.10 cg-style input


out vec2 uv;
out vec4 shadow_uv;
out vec4 world_pos;;
out vec3 normal;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    world_pos=p3d_ModelMatrix* p3d_Vertex;
    uv=p3d_MultiTexCoord0;
    //normal=p3d_ModelMatrixInverseTranspose*p3d_Normal;
    normal = (tpose_model_to_world * vec4(p3d_Normal, 0.0)).xyz;
    shadow_uv=shadow_caster.shadowMatrix*p3d_Vertex;
    }
