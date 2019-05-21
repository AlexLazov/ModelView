# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
import vbo

#     layout (location = 1) in vec2 aTexCoord;
# out vec2 TexCoord;
def build_shader():
    s155 = """
    //#version 330 core
    #version 410 compatibility
    layout (location = 0) in vec3 Position;
    layout (location = 1) in vec2 vertexUV;
    
    out vec2 UV;
    
    void main(){
       //gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
       //gl_Position = MVP*vec4(Position.x, Position.y, Position.z, 1.0);
       //gl_Position.xyz = vertexPos;
       //gl_Position.w = 1.0;
       
       gl_Position = gl_ModelViewProjectionMatrix * vec4(Position.x, Position.y, Position.z, 1.0);
       UV = vertexUV;
       
       }
    """
    
    s1 = """
    //#version 330 core
    #version 410 compatibility
    layout (location = 0) in vec3 Position;
    layout (location = 1) in vec2 vertexUV;
    layout(location = 2) in vec3 VertexNormal;
    
    out vec2 UV;
    
    void main(){
       //gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
       //gl_Position = MVP*vec4(Position.x, Position.y, Position.z, 1.0);
       //gl_Position.xyz = vertexPos;
       //gl_Position.w = 1.0;
       
       gl_Position = gl_ModelViewProjectionMatrix * vec4(Position.x, Position.y, Position.z, 1.0);
       gl_Normal = gl_ModelViewProjectionMatrix * vec4(VertexNormal.x, VertexNormal.y, VertexNormal.z, 1.0);
       UV = vertexUV;
       
       }
    """

    shader1 = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(shader1, s1)
    glCompileShader(shader1)
    print(glGetShaderInfoLog(shader1))

    s2 = """
    #version 330 core
    //#version 410 compatibility
    //in vec3 ourColor;
    in vec2 UV;
    uniform sampler2D textureSampler;
    out vec3 color;

    void main()
    {
        // linearly interpolate between both textures (80% container, 20% awesomeface)
        //FragColor = mix(texture(texture1, TexCoord), texture(texture2, TexCoord), 0.2);
        //gl_FragColor = vec4(0.5,0.5,0.5,1.0);
        color = texture(textureSampler, UV).rgb;
    }
    """

    shader2 = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(shader2, s2)
    glCompileShader(shader2)
    
    program = glCreateProgram()
    glAttachShader(program, shader1)
    glAttachShader(program, shader2)
    glLinkProgram(program)
    
    glDeleteShader(shader1); 
    glDeleteShader(shader2); 

    
    return program

pygame.init()
viewport = (800,600)
hx = viewport[0]/2
hy = viewport[1]/2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)
glEnable(GL_TEXTURE_2D)
# glEnable(GL_NORMALIZE)

# LOAD OBJECT AFTER PYGAME INIT
obj = vbo.Mesh(r"D:\MyProgram\3dpython\pygame_vbo\anka.obj")
mesh = vbo.MeshBuffer(obj)

program = build_shader()
glUseProgram(program)

tex_id = glGetUniformLocation(program, "textureSampler")
glUniform1i(tex_id, 0)

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(45.0, width/float(height), 0.1, 1000.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

rx, ry = (0,0)
tx, ty = (0,0)
zpos = 0
rotate = move = False
while 1:
    clock.tick(30)
    
    for e in pygame.event.get():
        if e.type == QUIT:
            mesh.dispose()
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            mesh.dispose()
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            elif e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j
                

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(100, 100, 100, 0, 0, 0, 0, 1, 0)
    # RENDER OBJECT
    glTranslate(tx/20., ty/20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    mesh.draw()
    

    pygame.display.flip()
