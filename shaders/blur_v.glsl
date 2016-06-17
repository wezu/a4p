//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;

out vec2 uv;
out vec4 uv01;
out vec4 uv23;
out vec4 uv45;
out vec4 uv67;
out vec4 uv89;
out vec4 uv1011;

uniform float sharpness;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv=gl_Position.xy*0.5+0.5;
    uv01= vec4(uv+vec2(-0.326212,-0.405805)*sharpness, uv + vec2(-0.840144, -0.073580)*sharpness);
    uv23=vec4( uv+vec2(-0.695914,0.457137)*sharpness, uv+vec2(-0.203345,0.620716)*sharpness);
    uv45=vec4( uv+vec2(0.962340,-0.194983)*sharpness, uv+vec2(0.473434,-0.480026)*sharpness);
    uv67=vec4( uv+vec2(0.519456,0.767022)*sharpness, uv+vec2(0.185461,-0.893124)*sharpness);
    uv89=vec4( uv+vec2(0.507431,0.064425)*sharpness, uv+vec2(0.896420,0.412458)*sharpness);
    uv1011=vec4( uv+vec2(-0.321940,-0.932615)*sharpness, uv+vec2(-0.791559,-0.597705)*sharpness);
    }
