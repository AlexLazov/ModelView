import numpy
from OpenGL.GL import *
from PIL import Image

class Loader(object):
  
  def __init__(self, path):
    vertices = []
    normals = []
    texcoords = []
    faces = []
    for line in open(path, "r"):
      if line.startswith('#'): continue
      values = line.split()
      if not values: continue
      if values[0] == 'v':
        vertices.append(tuple(map(float, values[1:4])))
      elif values[0] == 'vn':
        normals.append(tuple(map(float, values[1:4])))
      elif values[0] == 'vt':
        texcoords.append(tuple(map(float, values[1:3])))
      elif values[0] == 'f':
        face = []
        for v in values[1:]:
          w = map(lambda x: int(x) if x else None, v.split('/'))
          w = map(lambda x: x-1 if x != None and x > 0 else x, w)
          face.append(tuple(w))
        faces.append(tuple(face))
    # save result
    self.vertices = vertices
    self.normals = normals
    self.texcoords = texcoords
    self.faces = faces

class Mesh(object):
  
  def __init__(self, path):
    # load file
    loader = Loader(path)
    #
    index_lookup = {}
    num_vertices = 0
    
    # compute how many elements in vertices referenced by indices
    for face in loader.faces:
      for index in face:
        if index not in index_lookup:
          index_lookup[index] = num_vertices
          num_vertices += 1
    
    # build vertex buffer
    if loader.vertices:
      vertex_buffer = numpy.ndarray((num_vertices, 3), numpy.float32)
      for (index, real_index) in index_lookup.items():
        vertex_buffer[real_index] = loader.vertices[index[0]]
      self.vertex_buffer = vertex_buffer
    else:
      self.vertex_buffer = None
    # build normal buffer
    if loader.normals:
      normal_buffer = numpy.ndarray((num_vertices, 3), numpy.float32)
      for (index, real_index) in index_lookup.items():
        normal_buffer[real_index] = loader.normals[index[2]]
      self.normal_buffer = normal_buffer
    else:
      self.normal_buffer = None
    # build texcoord buffer
    if loader.texcoords:
      texcoord_buffer = numpy.ndarray((num_vertices, 2), numpy.float32)
      for (index, real_index) in index_lookup.items():
        texcoord_buffer[real_index] = loader.texcoords[index[1]]
      self.texcoord_buffer = texcoord_buffer
    else:
      self.texcoord_buffer = None
    
    # build index buffer
    index_buffer = numpy.ndarray((len(loader.faces), 3), numpy.uint32)
    count = 0
    for face in loader.faces:
      index_buffer[count] = list(map(lambda x: index_lookup[x], face))
      count += 1
    self.index_buffer = index_buffer
    
    # Texture
    tga_tex = Image.open(r"D:\MyProgram\3dpython\pytkogl-pyopengl_vbo\anka.tga").convert("RGBA").transpose( Image.FLIP_TOP_BOTTOM )
    tga_img = tga_tex.tobytes()

    ix, iy = tga_tex.size
    self.texture_Kd = GLuint(1)
    glGenTextures(1, self.texture_Kd)

    glBindTexture(GL_TEXTURE_2D, self.texture_Kd)

    glTexParameteri(
        GL_TEXTURE_2D,
        GL_TEXTURE_MIN_FILTER,
        GL_LINEAR
    )

    glTexParameteri(
        GL_TEXTURE_2D,
        GL_TEXTURE_MAG_FILTER,
        GL_LINEAR
    )

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        ix,
        iy,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        tga_img
    )

class MeshBuffer(object):
  
  def __init__(self, mesh):
    count = 1
    if mesh.vertex_buffer is not None: count += 1
    if mesh.normal_buffer is not None: count += 1
    if mesh.texcoord_buffer is not None: count += 1
    self.texture_Kd = mesh.texture_Kd
    buffers = list(glGenBuffers(count))
    self._vao = glGenVertexArrays(1)
    #glGenBuffers(1, self._vao);
    glBindVertexArray(self._vao);
    if mesh.vertex_buffer is not None:
      self._vertex_vbo = buffers.pop()
      glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbo)
      glBufferData(GL_ARRAY_BUFFER, 
                   4 * mesh.vertex_buffer.size, 
                   mesh.vertex_buffer, 
                   GL_STATIC_DRAW)
      glEnableVertexAttribArray(0)
      glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    else:
      self._vertex_vbo = 0
    if mesh.normal_buffer is not None:
      self._normal_vbo = buffers.pop()
      glBindBuffer(GL_ARRAY_BUFFER, self._normal_vbo)
      glBufferData(GL_ARRAY_BUFFER, 
                   4 * mesh.normal_buffer.size, 
                   mesh.normal_buffer, 
                   GL_STATIC_DRAW)
      glEnableVertexAttribArray(2)
      glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    else:
      self._normal_vbo = 0
    if mesh.texcoord_buffer is not None:
      self._texcoord_vbo = buffers.pop()
      glBindBuffer(GL_ARRAY_BUFFER, self._texcoord_vbo)
      glBufferData(GL_ARRAY_BUFFER, 
                   4 * mesh.texcoord_buffer.size, 
                   mesh.texcoord_buffer, 
                   GL_STATIC_DRAW)
      glEnableVertexAttribArray(1)
      glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    else:
      self._texcoord_vbo = 0
    # index buffer
    self._index_vbo = buffers.pop()
    self._index_count = mesh.index_buffer.size
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._index_vbo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 4 * mesh.index_buffer.size,
                 mesh.index_buffer, 
                 GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._index_vbo)
    # vertex array object
    # clear state
    # glBindBuffer(GL_ARRAY_BUFFER, 0)
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
  
  def dispose(self):
    glDeleteBuffers([
      self._index_vbo, self._vertex_vbo, self._normal_vbo, self._texcoord_vbo
    ])
    glDeleteVertexArrays([self._vao])
    self._index_vbo = 0
    self._vertex_vbo = 0
    self._normal_vbo = 0
    self._texcoord_vbo = 0
    self._vao = 0
  
  # def _bind_state(self):
    # if self._vertex_vbo is not None:
      # glEnableClientState(GL_VERTEX_ARRAY)
      # glEnableVertexAttribArray(0)
      # glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbo)
      # glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
      # glEnableClientState(GL_VERTEX_ARRAY)
      # glVertexPointer(3, GL_FLOAT, 0, None)
    # if self._texcoord_vbo is not None:
      # glEnableVertexAttribArray(1)
      # glBindBuffer(GL_ARRAY_BUFFER, self._texcoord_vbo)
      # glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    # if self._normal_vbo is not None:
      # glEnableVertexAttribArray(2)
      # glBindBuffer(GL_ARRAY_BUFFER, self._normal_vbo)
      # glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    # index buffer
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._index_vbo)
  
  def draw(self):
    glActiveTexture(GL_TEXTURE0+0);
    glEnableClientState(GL_NORMAL_ARRAY);
    glBindTexture(GL_TEXTURE_2D, self.texture_Kd)
    glBindVertexArray(self._vao)
    # self._bind_state()
    glDrawElements(GL_TRIANGLES, self._index_count, GL_UNSIGNED_INT, None)
    #glDrawArrays(GL_TRIANGLES, 0, self._index_count)
    # glDisableVertexAttribArray(0)
    # glDisableVertexAttribArray(1);
    # glDisableVertexAttribArray(2);

