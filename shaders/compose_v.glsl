//GLSL
#version 140
in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float osg_FrameTime;
uniform vec2 screen_size;

out vec2 uv;
out vec2 time_uv;
out vec2 rotate_uv;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex; 
    uv = gl_Position.xy*0.5+0.5;
    //the noise texture is 512x512, we want to repeat it if the screen is bigger
    vec2 factor=screen_size/vec2(512.0, 512.0);
    time_uv = uv*factor+vec2(0.0, osg_FrameTime*0.2);
    
    //mat2 RotationMatrix = mat2( vec2(cos(osg_FrameTime*0.04), -sin(osg_FrameTime*0.04) ), vec2(sin(osg_FrameTime*0.04),  cos(osg_FrameTime*0.04) ) );
    
    rotate_uv= gl_Position.xy;//*RotationMatrix;
    //rotate_uv*=0.77;
    }
