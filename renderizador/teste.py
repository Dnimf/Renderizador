import gl 
import numpy as np    
import math# Recupera rotinas de suporte ao X3D
ponto = [0,0,1,1]
rotation = [0,1,0,math.pi/2]
escala = [0,1,2]
translation = [0,1,1]
print(ponto)
# q = gl.GL.transform_in(0,0,rotation)
q = gl.GL.transform_in(translation,0,rotation)


a =(np.matmul(q,ponto))
print(f"a{a}")
