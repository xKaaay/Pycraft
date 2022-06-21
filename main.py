from pyglet.gl import *
from pyglet.window import key
import math

world = []
save = {'POSITION' : [], 'GRASS' : [], 'OAK_TREE' : [], 'OAK_LEAF' : [], 'STONE' : [], 'DIRT' : []}
tex_coords = [0,1,0,0,1,0,1,1]
CHUNK = 1


def get_tex(file):
    tex = pyglet.image.load(file).get_texture()
    glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
    return pyglet.graphics.TextureGroup(tex)

texture = {
'GRASS' : ['texture/env/grass/top.png', 'texture/env/grass/side.png',],
'DIRT' : ['texture/env/common/dirt.png'],
'STONE' : ['texture/env/common/stone.png'],

'OAK_TREE' : ['texture/env/trees/oak/root.png', 'texture/env/trees/oak/side.png'], 
'OAK_LEAF' : ['texture/env/trees/oak/test.png'],
}

texpass = []
for n in texture:
    for i in texture[n]:
        texpass.append(get_tex(i))
    texture[n] = texpass
    texpass = []

# TOP, BOTTOM, SIDE
cube = {
    'GRASS' : [texture['GRASS'][0], texture['DIRT'][0], texture['GRASS'][1]],

    'OAK_TREE' : [texture['OAK_TREE'][0], texture['OAK_TREE'][0], texture['OAK_TREE'][1]], 
    'OAK_LEAF' : [texture['OAK_LEAF'][0]]
}


def cube_vertices(x=0, y=0, z=0, n=1):
    #TOP[0], BOTTOM[1], SIDES[2], WORLD POSITION DATA[3]
    return [
        [x+n,y,z, x,y,z, x,y,z+n, x+n,y,z+n],
        [x+n,y-n,z, x,y-n,z, x,y-n,z+n, x+n,y-n,z+n],
        [x,y,z, x,y-n,z, x,y-n,z+n, x,y,z+n,
        x+n,y,z, x+n,y-n,z, x+n,y-n,z+n, x+n,y,z+n, 
        x,y,z+n, x,y-n,z+n, x+n,y-n,z+n, x+n,y,z+n, 
        x,y,z, x,y-n,z, x+n,y-n,z, x+n,y,z,],
        [x,y,z]
    ]


class Model:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self._initialize()
        #print("WORLD\n", world)
        #print("\nSAVE\n", save)

    def generate(self, BLOCK, x=0, y=0, z=0, TYPE='M'):
        axis = cube_vertices(x, y, z)
        if TYPE == 'M':
            if axis[3] not in world:
                world.append(axis[3])
                self.batch.add(4, GL_QUADS,cube[BLOCK][0],('v3f', axis[0]),('t2f', tex_coords))
                self.batch.add(4, GL_QUADS,cube[BLOCK][1],('v3f', axis[1]),('t2f', tex_coords))
                self.batch.add(16, GL_QUADS,cube[BLOCK][2],('v3f', axis[2]),('t2f', tex_coords * 4))
                save[BLOCK].append(axis[3])
        else:
            if axis[3] not in world:
                world.append(axis[3])
                self.batch.add(4, GL_QUADS,cube[BLOCK][0],('v3f', axis[0]),('t2f', tex_coords))
                self.batch.add(4, GL_QUADS,cube[BLOCK][0],('v3f', axis[1]),('t2f', tex_coords))
                self.batch.add(16, GL_QUADS,cube[BLOCK][0],('v3f', axis[2]),('t2f', tex_coords * 4))
                save[BLOCK].append(axis[3])

    def _initialize(self):
        print("Generating world")
        for x in range(CHUNK, -CHUNK-1, -1):
            for z in range(CHUNK, -CHUNK-1, -1):
                for y in range(-1, -CHUNK-1, -1):
                    self.generate('GRASS', x, y, z)
        self.oak_tree(0, 0, 0)
        
    
    def oak_tree(self, x=0, y=0, z=0):
        for Y in range(5): 
            self.generate('OAK_TREE', x, y+Y, z)

        for X in range(2-x, -3-x, -1):
            for Z in range(2+z, -3-z, -1):
                for Y in range(y+2, y+2+2):
                    self.generate('OAK_LEAF', x+X, y+Y, z+Z, 'S')

        for X in range(1-x, -2-x, -1):
                for Y in range(y+2+2, y+2+2+2):
                    self.generate('OAK_LEAF', x+X, y+Y, z, 'S')

        for Z in range(1+z, -2-z, -1):
            for Y in range(y+2+2, y+2+2+2):
                    self.generate('OAK_LEAF', x, y+Y, z+Z, 'S')

    def draw(self):
        self.batch.draw()



class Player:
    def __init__(self,pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)

    def mouse_motion(self,dx,dy):
        dx/=8; dy/=8; self.rot[0]+=dy; self.rot[1]-=dx
        if self.rot[0]>90: self.rot[0] = 90
        elif self.rot[0]<-90: self.rot[0] = -90

    def update(self,dt,keys):
        s = dt*10
        rotY = -self.rot[1]/180*math.pi
        dx,dz = s*math.sin(rotY),s*math.cos(rotY)
        if keys[key.W]: self.pos[0]+=dx; self.pos[2]-=dz
        if keys[key.S]: self.pos[0]-=dx; self.pos[2]+=dz
        if keys[key.A]: self.pos[0]-=dz; self.pos[2]-=dx
        if keys[key.D]: self.pos[0]+=dz; self.pos[2]+=dx

        if keys[key.SPACE]: self.pos[1]+=s
        if keys[key.LSHIFT]: self.pos[1]-= s


class Window(pyglet.window.Window):

    def push(self,pos,rot): glPushMatrix(); glRotatef(-rot[0],1,0,0); glRotatef(-rot[1],0,1,0); glTranslatef(-pos[0],-pos[1],-pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set2d(self): self.Projection(); gluOrtho2D(0,self.width,0,self.height); self.Model()
    def set3d(self): self.Projection(); gluPerspective(70,self.width/self.height,0.05,1000); self.Model()

    def setLock(self,state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False; mouse_lock = property(lambda self:self.lock,setLock)

    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)

        self.set_minimum_size(300,200)
        self.keys = key.KeyStateHandler()
        
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.model = Model()
        self.player = Player((8,.8,8),(0,45))

    def on_mouse_motion(self,x,y,dx,dy):
        if self.mouse_lock: self.player.mouse_motion(dx,dy)

    def on_key_press(self,KEY,MOD):
        if KEY == key.ESCAPE: self.close()
        elif KEY == key.E: self.mouse_lock = not self.mouse_lock
        if KEY == key.F11: self.set_fullscreen(True)

    def update(self,dt):
        self.player.update(dt,self.keys)

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos,self.player.rot)
        self.model.draw()
        glPopMatrix()

if __name__ == '__main__':
    window = Window(width=1336,height=720,caption='Minecraft',resizable=True)
    glClearColor(0.5,0.7,1,1)
    glEnable(GL_DEPTH_TEST)
    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    #glEnable(GL_CULL_FACE)
    pyglet.app.run()


