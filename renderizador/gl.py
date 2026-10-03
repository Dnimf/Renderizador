#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=invalid-name

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: <SEU NOME AQUI>
Disciplina: Computação Gráfica
Data: <DATA DE INÍCIO DA IMPLEMENTAÇÃO>
"""

import time         # Para operações com tempo
import gpu          # Simula os recursos de uma GPU
import math         # Funções matemáticas
import numpy as np  # Biblioteca do Numpy

class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    width = 800   # largura da tela
    height = 600  # altura da tela
    near = 0.01   # plano de corte próximo
    far = 1000    # plano de corte distante
    matriz_projecao = []
    matriz_transformacao = [np.identity(4)]
    matriz_camera =[]
    image_texture = []
    posicao_global = 1
    osicao_camera =[]
    # headlight ={}
    directionalL={"ambientIntensity":0, "intensity":0, }
    inversa = [np.identity(4)]
    normal = []
    normais = {}
    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        # print(f"aaaaa {GL.width},{width}")
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far
    def posicao_pixel(alfa, beta, gama, z_s, pontos, Z):  # 3 x 3 (um vértice por linha)'
        pesos = np.array([alfa/z_s[0], beta/z_s[1], gama/z_s[2]])
        # print(pontos)
        
        return (pesos @ pontos) / Z    
    def encontra_normal(p0,p1,p2):
        p0_p1 = np.subtract(p1,p0)
        p0_p2 = np.subtract(p2,p0)
        n = np.cross(p0_p1[:3],p0_p2[:3])
        n = n/np.linalg.norm(n)
        return n
    def transforma_normal(n):
        t = np.array(GL.matriz_transformacao[-1])[:3, :3]
        # inv = np.linalg.inv(t)
        # final = np.transpose(inv)
        final = GL.inversa[-1]
        final = final@n
        final = final/np.linalg.norm(final)
        return final
    def enontra_luz_difusa(k, r, n):
       
        if r == 0:
            a = 1
        else:
            a = 1/(r**2)
        I = GL.directionalL["intensity"]
        if I == 0:
            return [0,0,0],0
        og =GL.directionalL["direction"].copy()
        og.append(0)
        # t = np.array(GL.matriz_transformacao[-1])
        # inv = np.linalg.inv(t)
        
        # final = np.transpose(inv)
        final = GL.inversa[-1]
        og = np.matmul(og, final)
        og = og[:3] / np.linalg.norm(og[:3])
        # print(f"normal {GL.normal}direcao {GL.directionalL["direction"]}")
        ang = np.dot(n,og[:3])
        temp  = np.multiply(k,I)
        temp = np.array(temp)*a
        # print(f"temp {temp}, ---")
        # print(f"ang {ang}")
        
        temp = temp*max(0,-ang)
        # print(temp)
        return temp, ang
    def acha_cor_especular(k,p,s):
        I = GL.directionalL["intensity"]
        # print(I)
        temp = I*np.array(k)
        og =GL.directionalL["direction"].copy()
        # print(p)
        og.append(0)
        t = np.array(GL.matriz_transformacao[-1])
        inv = np.linalg.inv(t)
        final = np.transpose(inv)
        og = np.matmul(og, final)
        og = -og[:3] / np.linalg.norm(og[:3])
        
        cam_local = np.matmul(inv, GL.posicao_camera)
        cam_local = cam_local[:3] / cam_local[3]
        v = cam_local - np.array(p)
        v = v / np.linalg.norm(v)
        
        
        # p = np.array(p)/np.linalg.norm(p)
        bi = (np.array(og))+np.array(v)
        bi = bi/np.linalg.norm(bi)
        # print(bi)
        ang = np.dot(GL.normal,bi)
        # print(ang)
        ang = min(1, max(0,ang))
        
        temp = temp *(ang**(s*128))
        return temp
    
    def acha_cor_especular_1(k):
            I = GL.directionalL["intensity"]
            if I == 0:
                return [0,0,0],0,[0,0,0]
            temp = I*np.array(k)
            og =GL.directionalL["direction"].copy()
            og.append(0)
            t = np.array(GL.matriz_transformacao[-1])
            inv = np.linalg.inv(t)
            final = np.transpose(inv)
            og = np.matmul(og, final)
            og = -og[:3] / np.linalg.norm(og[:3])
            
            cam_local = np.matmul(inv, GL.posicao_camera)
            cam_local = cam_local[:3] / cam_local[3]
            return og,cam_local,temp
    def encontra_normal_pixel(alfa,beta,gama,z_s,pontos,Z):
            pesos = np.array([alfa/z_s[0], beta/z_s[1], gama/z_s[2]])
            normal = (pesos @ pontos) / Z    
            GL.normal = normal / np.linalg.norm(normal)
    def acha_cor_especular_2(cam_local,p,og,s,N,temp):
        if og[0]==0 and og[1]==0 and og[2]==0:
            # print("erro")
            return [0,0,0]
        p = p[:3]
        # print(p)
        v = cam_local - np.array(p)
        v = v / np.linalg.norm(v)
        
        
        # p = np.array(p)/np.linalg.norm(p)
        bi = (np.array(og))+np.array(v)
        bi = bi/np.linalg.norm(bi)
        ang = np.dot(N,bi)
        # print(ang)
        ang = min(1, max(0,ang))
        # print(f"temp1 {temp}")
        temp = temp *(ang**(s*128))
        # print(f"temp {temp}")
        return temp
    @staticmethod
    def polypoint2D(point, colors):
        """Função usada para renderizar Polypoint2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Polypoint2D
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é a
        # coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
        # pelo tamanho da lista e assuma que sempre vira uma quantidade par de valores.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polypoint2D
        # você pode assumir inicialmente o desenho dos pontos com a cor emissiva (emissiveColor).

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("Polypoint2D : pontos = {0}".format(point)) # imprime no terminal pontos
        # print("Polypoint2D : colors = {0}".format(colors)) # imprime no terminal as cores
        cor =colors["emissiveColor"]
        i = 0
        while i<len(point):
            # print("x:",point[i])
            # print("y:",point[i+1])
            x = point[i]
            y= point[i+1]
            r= 255 *cor[0]
            g=255*cor[1]
            b=255*cor[2]
            gpu.GPU.draw_pixel([int(x), int(y)], gpu.GPU.RGB8, [r, g, b])
            i+=2
        # Exemplo:
        # pos_x = GL.width//2
        # pos_y = GL.height//2
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 0])  # altera pixel (u, v, tipo, r, g, b)
        # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)
        
    @staticmethod
    def polyline2D(lineSegments, colors):
        """Função usada para renderizar Polyline2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Polyline2D
        # Nessa função você receberá os pontos de uma linha no parâmetro lineSegments, esses
        # pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o valor da
        # coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é
        # a coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
        # pelo tamanho da lista. A quantidade mínima de pontos são 2 (4 valores), porém a
        # função pode receber mais pontos para desenhar vários segmentos. Assuma que sempre
        # vira uma quantidade par de valores.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polyline2D
        # você pode assumir inicialmente o desenho das linhas com a cor emissiva (emissiveColor).
        # width = gpu.GPU.frame_buffer[gpu.GPU.read_framebuffer].depth.shape
        # print("a",width)
        # print(gpu.FrameBuffer.depth.shape)
        def limite(u,v):
            if u>=0:
                if u< GL.width:
                    if v>=0:
                        if v<GL.height:
                            return True
            return False
        def acha_s(p0,p1):
            s = 0
            if(p1[0]-p0[0]) != 0:
                s = (p1[1]-p0[1])/(p1[0]-p0[0])
            # print(p0, s)
            return s
        def uv(p0,p1):
            if p0[0]<=p1[0]:
                return [p0[0],p0[1],p1[0],p1[1]]
            else:
                return [p1[0],p1[1],p0[0],p0[1]]
        def vu(p0,p1):
            if p0[1]<=p1[1]:
                return [p0[0],p0[1],p1[0],p1[1]]
            else:
                return [p1[0],p1[1],p0[0],p0[1]]
        def preenche_linha(p0,p1,s, r, g, b):
            if s>0.0:
                if s<1:
                    p = uv(p0,p1)
                    u = p[0]
                    v = p[1]
                    while u<= p[2]:
                        if limite(u,v):
                            gpu.GPU.draw_pixel([int(u), int(v)], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
                        u+=1
                        v+=s
            if s<0:
                if s>-1:
                                        # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                    p = uv(p0,p1)
                    u = p[2]
                    v = p[3]
                    while u>= p[0]:
                        if limite(u,v):
                                gpu.GPU.draw_pixel([int(u), int(v)], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
                        u-=1
                        v-=s
            if s>1:
                s = 1/s
                p = vu(p0,p1)
                u = p[0]
                v = p[1]
                while v<= p[3]:
                    if limite(u,v):
                        gpu.GPU.draw_pixel([int(u), int(v)], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
                    u+=s
                    v+=1
            if s<-1:
                s = 1/s
                p = vu(p0,p1)
                u = p[2]
                v = p[3]
                while v>= p[1]:
                    if limite(u,v):
                        # print(u, v)
                        gpu.GPU.draw_pixel([int(u), int(v)], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
                    u-=s
                    v-=1
            if s == 0:
                p = uv(p0,p1)
                i=p[0]
                while i<p[2]:
                    if limite(i,p[1]):
                        gpu.GPU.draw_pixel([int(i), int(p[1])], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
                    i+=1
            if abs(s) == 0:
                p = vu(p0,p1)
                i=p[1]
                while i<p[3]:
                    if limite(p[0],i):
                        gpu.GPU.draw_pixel([int(p[0]), int(i)], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
                    i+=1                   
        cor =colors["emissiveColor"]

        # print("Polyline2D : lineSegments = {0}".format(lineSegments)) # imprime no terminal
        # print("Polyline2D : colors = {0}".format(colors)) # imprime no terminal as cores
        # print(len(lineSegments))
        i =0 
        pontos = []
        r= 255*cor[0]
        g=255*cor[1]
        b=255*cor[2]
        while i<len(lineSegments):
            x = lineSegments[i]
            y = lineSegments[i+1]
            # print("x",x,"y",y,GL.width,GL.height)
            # if x>0:
            #     if y>0:
            #         if x<GL.width:
            #         # y = lineSegments[i+1]
            #             if y<GL.height:
            pontos.append([x,y])
            i+=2
        j =1 
        while j<len(pontos):
            p_0=pontos[j-1]
            p_1=pontos[j]
            s=acha_s(p_0,p_1)
            preenche_linha(p_0,p_1,s, r, g, b)
            # gpu.GPU.draw_pixel([int(p_0[0]), int(p_0[1])], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
            # gpu.GPU.draw_pixel([int(p_1[0]), int(p_1[1])], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
            j+=1
        # Exemplo:
        # pos_x = GL.width//2
        # pos_y = GL.height//2
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 255])  # altera pixel (u, v, tipo, r, g, b)
        # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

    @staticmethod
    def circle2D(radius, colors):
        """Função usada para renderizar Circle2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#Circle2D
        # Nessa função você receberá um valor de raio e deverá desenhar o contorno de
        # um círculo.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Circle2D
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).
        def limite(p):
            u = p[0]
            v = p[1]
            if u>=0:
                if u< GL.width:
                    if v>=0:
                        if v<GL.height:
                            return True
            return False
        # print("Circle2D : radius = {0}".format(radius)) # imprime no terminal
        # print("Circle2D : colors = {0}".format(colors)) # imprime no terminal as cores
        x0 =0
        y0 = 0
        i = 0
        cor = colors["emissiveColor"]
        r = 255*cor[0]
        g = 255*cor[1]
        b = 255*cor[2]
        pontos = []
        while i< 2*math.pi:
            x = x0+radius*math.cos(i)
            y = y0+radius*math.sin(i)
            pontos.append([x,y])
            i+=0.05
        # print(pontos)
        j = 0;
        while j<len(pontos):
            ponto = pontos[j]
            if limite(ponto):
                gpu.GPU.draw_pixel([round(ponto[0]), round(ponto[1])], gpu.GPU.RGB8, [r, g, b])  # altera pixel (u, v, tipo, r, g, b)
            j+=1
        # Exemplo:
        pos_x = GL.width//2
        pos_y = GL.height//2
        # gpu.GPU.draw_pixel([pos_x, pos_y], gpu.GPU.RGB8, [255, 0, 255])  # altera pixel (u, v, tipo, r, g, b)
        # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)


    @staticmethod
    def triangleSet2D(vertices,colors, coordIndex, colorPerVertex, color, colorIndex='',
                       texCoord='', texCoordIndex='', current_texture='', z_s='', z_norm='', pontos =[]):
        """Função usada para renderizar TriangleSet2D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry2D.html#TriangleSet2D
        # Nessa função você receberá os vertices de um triângulo no parâmetro vertices,
        # esses pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o
        # valor da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto.
        # Já point[2] é a coordenada x do segundo ponto e assim por diante. Assuma que a
        # quantidade de pontos é sempre multiplo de 3, ou seja, 6 valores ou 12 valores, etc.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet2D
        # você pode assumir inicialmente o desenho das linhas com a cor emissiva (emissiveColor).
        # print(pontos)
        def limite(u,v):
            if u>=0:
                if u< GL.width:
                    if v>=0:
                        if v<GL.height:
                            return True
            return False
        cor_emissiva = np.array(colors["emissiveColor"])
        cor = cor_emissiva
        transp = colors["transparency"]
        especular = colors["specularColor"]
        s = colors["shininess"]
        difusa = colors["diffuseColor"]
        # pontos_1 = pontos
        pontos_1 = list(zip(pontos[::3], pontos[1::3],pontos[2::3]))
        normais=[]
        d = np.zeros(3)        
        if len(GL.normais) != 0:
            normal_v_1 = np.mean(GL.normais[f"{[pontos[0][0],pontos[0][1],pontos[0][2]]}"],axis=0)
            normal_v_2 = np.mean(GL.normais[f"{[pontos[1][0],pontos[1][1],pontos[1][2]]}"],axis=0)
            normal_v_3 = np.mean(GL.normais[f"{[pontos[2][0],pontos[2][1],pontos[2][2]]}"],axis=0)
            normal_v_1 = normal_v_1/np.linalg.norm(normal_v_1)
            normal_v_2 = normal_v_2/np.linalg.norm(normal_v_2)
            normal_v_3 = normal_v_3/np.linalg.norm(normal_v_3)
            normais = [normal_v_1,normal_v_2,normal_v_3]
        p = np.mean([pontos[0], pontos[1], pontos[2]], axis=0)[:3]
        # if especular != [0,0,0]:
        og,cam_local,temp = GL.acha_cor_especular_1(especular)
        # print(og,cam_local,temp)
        # if cor ==[0,0,0] and difusa !=[0,0,0]:
        if len(GL.normais) != 0:
            d,grau=GL.enontra_luz_difusa(k=difusa,r=0, n=normais[0])
            d1,grau=GL.enontra_luz_difusa(k=difusa,r=0, n=normais[1])
            d2,grau=GL.enontra_luz_difusa(k=difusa,r=0, n=normais[2])
            d = (np.array(d)+np.array(d1)+np.array(d2))/3
        else:
            d,grau=GL.enontra_luz_difusa(k=difusa,r=0, n=GL.normal)
                
        cor = np.array(d)
        cor1 = color
        r=cor[0]
        g=cor[1]
        b=cor[2]
        if not current_texture:
            r*=255
            if r>255:
                r = 255
            g*=255
            if g>255:
                g =255
            b*=255
            if b>255:
                b =255
            # print(f"rgb {r,g,b}")
        r_1 = r
        g_1 = g
        b_1 = b
        cont = 0
        prof = True
        
        def verifica_profundidade(Z_norm,p):
            nonlocal r,g,b, prof , r_1, g_1, b_1
            x = p[0]-0.5
            y = p[1]-0.5
            # print(x,y)
            profundidade = gpu.GPU.read_pixel([int(x), int(y)], gpu.GPU.DEPTH_COMPONENT32F)
            if transp !=0:
                cor = gpu.GPU.read_pixel([int(x), int(y)], gpu.GPU.RGBA8)
        
            # print(cor)
                r_a = cor[0]*transp
                g_a = cor[1]*transp
                b_a = cor[2]*transp
            else:
                r_a = 0
                b_a = 0
                g_a = 0
            if(Z_norm<profundidade):
                r=r_a+(r_1*(1-transp))
                g=g_a+(g_1*(1-transp))
                b=b_a+(b_1*(1-transp))
                gpu.GPU.draw_pixel([int(x), int(y)],gpu.GPU.DEPTH_COMPONENT32F ,[Z_norm])
                return True
            return False
        def verifica_cor_textura(alfa,beta,gama,z,Z_norm,p):
            nonlocal r,g,b, r_1,g_1,b_1
            # print(f"textcoord :{texCoord}")
            # print(f"textcorordindex :{texCoordIndex}")
            u_0 = texCoord[0][0]
            v_0 = texCoord[0][1]
            u_1 = texCoord[1][0]
            v_1 = texCoord[1][1]
            u_2 = texCoord[2][0]
            v_2 = texCoord[2][1]
            # print(len(GL.image_texture[0]),len(GL.image_texture))
            u = ((alfa*(u_0/z_s[0])) + (beta*(u_1/z_s[1])) +(gama*(u_2/z_s[2])))/z                        
            v = ((alfa*(v_0/z_s[0])) + (beta*(v_1/z_s[1])) +(gama*(v_2/z_s[2])))/z
            u_f = (len(GL.image_texture[0])-1)*u                     
            v_f = (len(GL.image_texture)-1)*v
            if u_f>255:
                u_f =255
            if v_f>255:
                v_f =255
            if u_f<0:
                u_f =0
            if v_f<0:
                v_f = 0
            # print(u,v)
            # print(u_f,v_f)
            cor = GL.image_texture[math.floor(u_f),(255-math.floor(v_f))]
            # r = cor[0]                     
            # g = cor[1]                     
            # b = cor[2]
            r_1 = cor[0]                     
            g_1 = cor[1]                     
            b_1 = cor[2]        
            # print(r,g,b)               
        def verifica_cor(alfa,beta,gama,cores,Z,Z_norm,p):
            nonlocal r,g,b,r_1,g_1,b_1
            c1 = cores[0]
            c2 = cores[1]
            c3 = cores[2]
            r_1_1 = alfa*(255*c1[0]/z_s[0])
            r_1_2 = beta*(255*c2[0]/z_s[1])            
            r_1_3 = gama*(255*c3[0]/z_s[2])
            r_1 = (r_1_1+r_1_2+ r_1_3)/Z
            
            g_1_1 = alfa*(255*c1[1]/z_s[0])
            g_1_2 = beta*(255*c2[1]/z_s[1])            
            g_1_3 = gama*(255*c3[1]/z_s[2])
            g_1 = (g_1_1+g_1_2+ g_1_3)/Z
            
            b_1_1 = alfa*(255*c1[2]/z_s[0])
            b_1_2 = beta*(255*c2[2]/z_s[1])            
            b_1_3 = gama*(255*c3[2]/z_s[2])
            b_1 = (b_1_1+b_1_2+ b_1_3)/Z
            r_1 = abs(r_1)
            g_1 = abs(g_1)
            b_1 = abs(b_1)
        def cria_aresta(p,pp):
            return [pp[0]-p[0],pp[1]-p[1]]
        def verifica_individual(a,n):
            a_x = n[0]
            a_y = n[1]
            b_x = a[0]
            b_y = a[1]
            return (a_x*b_y)-(a_y*b_x)
        

        def esta_dentro(p0,p1,p2, p, indice):
            nonlocal cont,a0,a1,a2, alpha2, b_c, beta2, pontos_1,cor,r,g,b, r_1, g_1,b_1

            n0 =cria_aresta(p0,p) # (px-ax)(py-ay)
            n1 =cria_aresta(p1,p) # (px-bx)(py-by)
            n2 =cria_aresta(p2,p) # (px-cx)(py-cy)
            sera = verifica_individual(a0,n0)
            sera1 = verifica_individual(a1,n1)
            sera2 = verifica_individual(a2,n2)
            if sera>=0:
                if sera1>=0: 
                    if sera2>=0:
                        alpha1 = -(n1[0]*a1[1]) + (n1[1]*a1[0])
                        beta1 = -(n2[0]*a2[1])+(n2[1]*a2[0])
                        alpha = alpha1/alpha2
                        beta= beta1/beta2
                        gama = 1-alpha-beta
                        Z_norm = 1/(alpha/z_norm[0] + beta/z_norm[1]+ gama/z_norm[2])
                        Z = (alpha/z_s[0] + beta/z_s[1]+ gama/z_s[2])
                        pix = GL.posicao_pixel(alpha,beta,gama,z_s,pontos_1[indice],Z)
                        # if especular !=[0,0,0]:
                            # print("entrou")
                        if len(GL.normais)!=0:
                            GL.encontra_normal_pixel(alpha,beta,gama,z_s,normais,Z)
                        esp = GL.acha_cor_especular_2(cam_local,pix,og,s,GL.normal,temp)
                        d,grau=GL.enontra_luz_difusa(k=difusa,r=0, n=GL.normal)
                        cor = np.array(cor_emissiva) +np.array(d)+np.array(esp)
                        r = cor[0]*255
                        if r>255:
                            r = 255                                                                 
                        g = cor[1]*255
                        if g >255:
                            g = 255
                        b = cor[2]*255                                                                     
                        if b > 255:     
                            b = 255                                                             
                        r_1 = r
                        g_1 = g
                        b_1 = b
                        if verifica_profundidade(Z_norm,p):
                            if color:
                                verifica_cor(alpha,beta,gama,cor1,Z,Z_norm,p)
                                r = r_1
                                g = g_1
                                b = b_1
                                cont+=1
                            elif current_texture:
                                verifica_cor_textura(alpha,beta,gama,Z,Z_norm,p)
                                r = r_1
                                g = g_1
                                b = b_1
                            return True    
            return False
        def caixa(p0,p1,p2):
            x = [p0[0],p1[0], p2[0]]
            y = [p0[1],p1[1], p2[1]]
            minimo_x = min(x)
            maximo_x = max(x)
            minimo_y =min(y)
            maximo_y = max(y)
            if minimo_x<0:
                minimo_x = 0
            if minimo_y<0:
                minimo_y = 0
            if maximo_x>GL.width:
                maximo_x = GL.width-1
            if maximo_y>GL.height:
                maximo_y =( GL.height-1)            
            return [round(minimo_x),round(minimo_y),round(maximo_x),round(maximo_y )]
        def preenche_triangulo(p0,p1,p2,indice):
            c = caixa(p0,p1,p2)
            j = (c[1])
            while j<=c[3]:
                i = c[0]
                while i<=c[2]:
                    if esta_dentro(p0,p1,p2,[(i+0.5),(j+0.5)], indice):
                        gpu.GPU.draw_pixel([round(i), round(j)], gpu.GPU.RGB8, [round(r), round(g), round(b)])  # altera pixel (u, v, tipo, r, g, b)        
                            
                    i+=1
                j+=1
        i=2
        cont = 0
        pontos =[]
        pontos = list(zip(vertices[::2], vertices[1::2]))
        # print(len(pontos),len(pontos_1))
        while i<len(pontos):
            p0 = pontos[i-2]
            p1 = pontos[i-1]
            p2 = pontos[i]
            a0 = cria_aresta(p0,p1); # (bx-ax)(by-ay)
            a1 = cria_aresta(p1,p2); # (cx-bx)(cy-by)
            a2 = cria_aresta(p2,p0); # (ax-cx)(ay-cy)
            xa_xb = cria_aresta(p1,p0)
            alpha2 = -(xa_xb[0]*a1[1])+ (xa_xb[1]*a1[0])
            b_c = cria_aresta(p2,p1)
            beta2 = -(b_c[0]*a2[1])+(b_c[1]*a2[0])
            if alpha2 ==0:
                return
            
            preenche_triangulo(pontos[i-2],pontos[i-1], pontos[i],cont)
            # print(pontos[i-2],pontos[i-1], pontos[i],cont)
            i+=3
            cont+=1
        # print(cont,i)
    @staticmethod
    def triangleSet(point,colors, coordIndex='', colorPerVertex='', color='', colorIndex='',
                       texCoord='', texCoordIndex='', current_texture=''):
        """Função usada para renderizar TriangleSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/rendering.html#TriangleSet
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
        # assim por diante.
        # No TriangleSet os triângulos são informados individualmente, assim os três
        # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
        # triângulo, e assim por diante.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, você pode assumir
        # inicialmente, para o TriangleSet, o desenho das linhas com a cor emissiva
        # (emissiveColor), conforme implementar novos materias você deverá suportar outros
        # tipos de cores.
        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        ajuste = np.array([[(GL.width/2),0,0,(GL.width/2)],[0,-(GL.height/2),0,(GL.height/2)],[0,0,1,0],[0,0,0,1]])
        pontos = []
        pontos_transformados = []
        i = 2
        while i<len(point):
            pontos.append([point[i-2],point[i-1],point[i],1])
            i+=3
        # print(f"pontos{pontos}\n")
        z=[]
        z_norm = []    


        n = GL.encontra_normal(pontos[0],pontos[1],pontos[2])
        GL.normal = n
        for j in range(len(pontos)):
            transf = np.matmul(GL.matriz_transformacao[-1],pontos[j])
            camera = np.matmul(GL.matriz_camera,transf)
            z.append(camera[2]/camera[3])
            proj = np.matmul(GL.matriz_projecao,camera)
            proj[0] /= proj[3]
            proj[1] /= proj[3]
            proj[2] /= proj[3]
            proj[3] /= proj[3]
            
            z_norm.append(proj[2])
            ajust = np.matmul(ajuste,proj)
            pontos_transformados.append(ajust)
        # print(f"pontos transformados {pontos_transformados}")
        result = []
        for i in pontos_transformados:
            result.append(i[0])
            result.append(i[1])
            # z.append(i[2])
        
        GL.triangleSet2D(result,colors, coordIndex, colorPerVertex, color, colorIndex, texCoord, texCoordIndex, current_texture, z, z_norm,pontos)
        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # for i in pontos_transformados:
        #     # print(f"a {int(i[0]), int(i[1])}")
        #     gpu.GPU.draw_pixel([int(i[0]), int(i[1])], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel
    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.
        # print(position)
        def quartenion(rotation):
            x = rotation[0]
            y = rotation[1]
            z = rotation[2]
            theta = rotation[3]
            qr = math.cos(theta/2)
            qx = math.sin(theta/2)*x
            qy = math.sin(theta/2)*y
            qz = math.sin(theta/2)*z
            a = 1-2*((qy**2)+qz**2)
            b = 2*(qx*qy-qz*qr)
            c = 2*(qx*qz+qy*qr)
            d = 2*(qx*qy+qz*qr)
            e = 1-2*((qx**2)+qz**2)
            f = 2*(qy*qz-qx*qr)
            g = 2*(qx*qz-qy*qr)
            h = 2*(qy*qz+qx*qr)
            i = 1-2*((qx**2)+qy**2)
            return [[a,b,c,0],[d,e,f,0],[g,h,i,0],[0,0,0,1]]
        def translacao(translation):
            l1= [1,0,0,translation[0]]
            l2= [0,1,0,translation[1]]
            l3= [0,0,1,translation[2]]
            l4= [0,0,0,1]
            return [l1,l2,l3,l4]
        def escala(scale):
            x=[scale[0],0,0,0]
            y = [0,scale[1],0,0]
            z=[0,0,scale[2],0]
            w=[0,0,0,1]
            return [x,y,z,w]
        
        GL.posicao_global = position[2]
        GL.posicao_camera = np.append(position, 1) 
        rotacion = quartenion(orientation)
        trans = translacao(position)
        rotacion_inv = np.linalg.inv(rotacion)
        trans_inv = np.linalg.inv(trans)
        GL.matriz_camera = rotacion_inv@trans_inv
        # a orientas;'ao provavlemente quer dizer port onde esta vendo e o quanto teria q rotacionar
        
        top = GL.near*np.tan(fieldOfView/2)
        bottom = -top
        right = top*(GL.width/GL.height)
        left = -right
        a = [(GL.near/right),0,0,0]
        b = [0,(GL.near/top),0,0]
        c = [0,0,-((GL.far+GL.near)/(GL.far-GL.near)),((-2*GL.far*GL.near)/(GL.far-GL.near))]
        d = [0,0,-1,0]
        matriz = [a,b,c,d]               
        GL.matriz_projecao = matriz
        # print(f"testa profundidade: {gpu.GPU.read_pixel([0, 0], gpu.GPU.DEPTH_COMPONENT32F)}")
        
        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("Viewpoint : ", end='')
        # print("position = {0} ".format(position), end='')
        # print("orientation = {0} ".format(orientation), end='')
        # print("fieldOfView = {0} ".format(fieldOfView))

    @staticmethod
    def transform_in(translation, scale, rotation):
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
        # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
        # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
        # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
        # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
        # ESSES NÃO SÃO OS VALORES DE QUATÉRNIOS AS CONTAS AINDA PRECISAM SER FEITAS.
        # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
        # modelos do mundo para depois potencialmente usar em outras chamadas. 
        # Quando começar a usar Transforms dentre de outros Transforms, mais a frente no curso
        # Você precisará usar alguma estrutura de dados pilha para organizar as matrizes.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("Transformacao innnnnnnnn")
        padrao = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        def quartenion(rotation):
            x = rotation[0]
            y = rotation[1]
            z = rotation[2]
            theta = rotation[3]
            qr = math.cos(theta/2)
            qx = math.sin(theta/2)*x
            qy = math.sin(theta/2)*y
            qz = math.sin(theta/2)*z
            a = 1-2*((qy**2)+qz**2)
            b = 2*(qx*qy-qz*qr)
            c = 2*(qx*qz+qy*qr)
            d = 2*(qx*qy+qz*qr)
            e = 1-2*((qx**2)+qz**2)
            f = 2*(qy*qz-qx*qr)
            g = 2*(qx*qz-qy*qr)
            h = 2*(qy*qz+qx*qr)
            i = 1-2*((qx**2)+qy**2)
            return [[a,b,c,0],[d,e,f,0],[g,h,i,0],[0,0,0,1]]
        def translacao(translation):
            l1= [1,0,0,translation[0]]
            l2= [0,1,0,translation[1]]
            l3= [0,0,1,translation[2]]
            l4= [0,0,0,1]
            return [l1,l2,l3,l4]
        def escala(scale):
            x=[scale[0],0,0,0]
            y = [0,scale[1],0,0]
            z=[0,0,scale[2],0]
            w=[0,0,0,1]
            return [x,y,z,w]
        # print("Transform : ", end='')
        if scale:
            # print("scale = {0} ".format(scale), end='') # imprime no terminal
            s=escala(scale)
            padrao = np.matmul(s,padrao)
        if rotation:
            # print("rotation = {0} ".format(rotation), end='')
            q =  quartenion(rotation)# imprime no terminal
            padrao =np.matmul(q,padrao)
        if translation:
            # print("translation = {0} ".format(translation), end='') # imprime no terminal
            t= translacao(translation)
            padrao = np.matmul(t,padrao)
        # print(padrao)
        final = GL.matriz_transformacao[-1]@padrao
        GL.matriz_transformacao.append(final)
        # print(GL.matriz_transformacao)
        inv = np.linalg.inv(final)
        final_1 = np.transpose(inv)
        # return padrao
        GL.inversa.append(final_1)    
        # print("")

    @staticmethod
    def transform_out():
        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.
        del GL.matriz_transformacao[-1]
        del GL.inversa[-1]
        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("Saindo de Transform")

    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        """Função usada para renderizar TriangleStripSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/rendering.html#TriangleStripSet
        # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
        # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
        # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
        # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
        # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
        # em uma lista chamada stripCount (perceba que é uma lista). Ligue os vértices na ordem,
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        pontos =[]
        pontos_dist =[]
        triangulos = []
        
        def pontos_novos(p):
            for pp in p:
                if pp not in pontos_dist:
                    pontos_dist.append(pp)
        # print("TriangleStripSet : pontos = {0} ".format(point), end='')
        # print(stripCount)
        # for i, strip in enumerate(stripCount):
        #     print("strip[{0}] = {1} ".format(i, strip), end='')
        # print("")
        # print("TriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores
        i = 0;
        while i<(len(point)-2):
            pontos.append([point[i],point[i+1],point[i+2]])
            i+=3
        j = 2
        vira =0
        cont = 0
        # print(f" tamanho original {len(point)}, novo tamanho {len(pontos)}\n\n ponto 0: {point[0]},{point[1]},{point[2]} | {pontos[0]} \n\n ultimo ponto: {point[-3]},{point[-2]},{point[-1]}| {pontos[-1]}")
        while j<=(len(pontos)):
            p1 = pontos[j-2]
            p2 = pontos[j-1]
            p3 = pontos[j]
            pontos_novos([p1,p2,p3])
            # print(f"pontos_dist {len(pontos_dist)}")
            if vira:
                triangulos.append([p1[0],p1[1],p1[2],p3[0],p3[1],p3[2],p2[0],p2[1],p2[2]])
                vira =0
            else:
                triangulos.append([p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],p3[0],p3[1],p3[2]])
                vira = 1
            # print(F"Triangulso {triangulos}, tamanho {len(triangulos)*3}")
            j+=1
            if (len(pontos_dist)) >=stripCount[cont]:
                # print(triangulos)
                for k in triangulos:
                    # print(f"triangulos {k}")
                    GL.triangleSet(k,colors)
                triangulos=[]
                pontos_dist=[]
                cont+=1
                if cont  == len(stripCount):
                    break
                vira=0
                j+=2
               
        # Exemplo de desenho de um pixel branco na coordenada 10, 10

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        """Função usada para renderizar IndexedTriangleStripSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/rendering.html#IndexedTriangleStripSet
        # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
        # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
        # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
        # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
        # como conectar os vértices é informada em index, o valor -1 indica que a lista
        # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.
        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
        # print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime as cores
        # print("----------------------------------\n\n\n\n")
        pontos =[]
        
        # x=0.0
        i = 0;
        while i<(len(point)-2):
            pontos.append([point[i],point[i+1],point[i+2]])
            i+=3
        # print(f"pontos : {pontos}")
        j =2
        vira = 0
        triangulos = []
        while j<(len(index)):
            if index[j] == -1:
                # print(len(triangulos))
                for k in triangulos:
                    GL.triangleSet(k,colors)
                vira =0
                triangulos =[]
            else:
                p1 = pontos[index[j-2]]
                p2 = pontos[index[j-1]]
                p3 = pontos[index[j]]               
                if vira == 1:
                    triangulos.append([p1[0],p1[1],p1[2],p3[0],p3[1],p3[2],p2[0],p2[1],p2[2]])
                    n = GL.encontra_normal(p1,p3,p2)
                    
                    vira =0
                else:
                    triangulos.append([p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],p3[0],p3[1],p3[2]])
                    n = GL.encontra_normal(p1,p2,p3)
                    vira = 1
                if f"{p1}" not in GL.normais:
                    GL.normais[f"{p1}"] = [n]
                else:
                    GL.normais[f"{p1}"].append(n)
                if f"{p2}" not in GL.normais:
                    GL.normais[f"{p2}"] = [n]
                else:
                    GL.normais[f"{p2}"].append(n)
                if f"{p3}" not in GL.normais:
                    GL.normais[f"{p3}"] = [n]
                else:
                    GL.normais[f"{p3}"].append(n)
            j+=1
        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel
        # print("----------------------------------\n\n\n\n")

    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):
        """Função usada para renderizar IndexedFaceSet."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#IndexedFaceSet
        # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
        # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
        # Você receberá as coordenadas dos pontos no parâmetro cord, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim coord[0] é o valor
        # da coordenada x do primeiro ponto, coord[1] o valor y do primeiro ponto, coord[2]
        # o valor z da coordenada z do primeiro ponto. Já coord[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedFaceSet uma lista de vértices é informada
        # em coordIndex, o valor -1 indica que a lista acabou.
        # A ordem de conexão não possui uma ordem oficial, mas em geral se o primeiro ponto com os dois
        # seguintes e depois este mesmo primeiro ponto com o terçeiro e quarto ponto. Por exemplo: numa
        # sequencia 0, 1, 2, 3, 4, -1 o primeiro triângulo será com os vértices 0, 1 e 2, depois serão
        # os vértices 0, 2 e 3, e depois 0, 3 e 4, e assim por diante, até chegar no final da lista.
        # Adicionalmente essa implementação do IndexedFace aceita cores por vértices, assim
        # se a flag colorPerVertex estiver habilitada, os vértices também possuirão cores
        # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
        # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
        # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
        # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
        # implementadado um método para a leitura de imagens.
        # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print(f"face: {coord}")
        # print(f"colors asjhsdxtcyvubinoim{colors}")
        i = 0
        pontos =[]
        while i<(len(coord)-2):
            pontos.append([coord[i],coord[i+1],coord[i+2]])
            i+=3
        listas =[]
        temp =[]
        for j in coordIndex:
            if j == -1:
                listas.append(temp)
                temp = []
            else:
                temp.append(j)
        # print(f"listas: {listas}")
        rgb = []
        c=2
        if not current_texture and not color:
            for i in range(len(listas)):
                t = 2
                triangulos = []
                while t<len(listas[i]):
                    i1 = listas[i]
                    p1 = pontos[i1[0]]
                    p2 = pontos[i1[t-1]]
                    p3= pontos[i1[t]]  
                    triangulos = [p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],p3[0],p3[1],p3[2]]
                    n = GL.encontra_normal(p1,p2,p3)
                    if f"{p1}" not in GL.normais:
                        GL.normais[f"{p1}"] = [n]
                    else:
                        GL.normais[f"{p1}"].append(n)
                    if f"{p2}" not in GL.normais:
                        GL.normais[f"{p2}"] = [n]
                    else:
                        GL.normais[f"{p2}"].append(n)
                    if f"{p3}" not in GL.normais:
                        GL.normais[f"{p3}"] = [n]
                    else:
                        GL.normais[f"{p3}"].append(n)   
 
                        # vira = 1
                    t+=1
                    GL.triangleSet(triangulos,colors, coordIndex, colorPerVertex, color, colorIndex,
                        texCoord, texCoordIndex, current_texture)                 
        if not current_texture and color:
            while c<len(color):
                rgb.append([color[c-2],color[c-1],color[c]])
                c+=3
                
            coresId =[]
            if colorPerVertex:
                temp =[]
                for j in colorIndex:
                    if j == -1:
                        coresId.append(temp)
                        temp = []
                    else:
                        temp.append(j)
                cores = []
                for i in coresId:
                    cores.append([rgb[i[0]], rgb[i[1]], rgb[i[2]]])    

            for i in range(len(listas)):
                t = 2
                triangulos = []
                vira = 0
                while t<len(listas[i]):
                    i1 = listas[i]
                    p1 = pontos[i1[0]]
                    p2 = pontos[i1[t-1]]
                    p3= pontos[i1[t]]
                    n = GL.encontra_normal(p1,p2,p3)
                    if f"{p1}" not in GL.normais:
                        GL.normais[f"{p1}"] = [n]
                    else:
                        GL.normais[f"{p1}"].append(n)
                    if f"{p2}" not in GL.normais:
                        GL.normais[f"{p2}"] = [n]
                    else:
                        GL.normais[f"{p2}"].append(n)
                    if f"{p3}" not in GL.normais:
                        GL.normais[f"{p3}"] = [n]
                    else:
                        GL.normais[f"{p3}"].append(n)                    
                    
                    triangulos.append([p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],p3[0],p3[1],p3[2]])
                        # vira = 1
                    t+=1
                for k in range(len(triangulos)):
                    if colorPerVertex:
                    # print(f"triangulos {k}\n")
                        GL.triangleSet(triangulos[k],colors, coordIndex, colorPerVertex, cores[i], colorIndex,
                                texCoord, texCoordIndex, current_texture)         
        if current_texture:
            GL.image_texture = gpu.GPU.load_texture(current_texture[0])
            # print(f"textcoord{texCoord}")
            # print(f"textcoord index{texCoordIndex}")
            textura = []
            c =1        
            while c<len(texCoord):
                textura.append([texCoord[c-1],texCoord[c]])
                c+=2
            temp =[]
            textid = []
            for j in texCoordIndex:
                if j == -1:
                    textid.append(temp)
                    temp = []
                else:
                    temp.append(j)
            tex = []
            # print(textid)
            # print(textura)
            for i in textid:
                tex.append([textura[i[0]], textura[i[1]], textura[i[2]]])             
            for i in range(len(listas)):
                t = 2
                triangulos = []
                vira = 0
                while t<len(listas[i]):
                    i1 = listas[i]
                    p1 = pontos[i1[0]]
                    p2 = pontos[i1[t-1]]
                    p3= pontos[i1[t]]
                    n = GL.encontra_normal(p1,p2,p3)
                    if f"{p1}" not in GL.normais:
                        GL.normais[f"{p1}"] = [n]
                    else:
                        GL.normais[f"{p1}"].append(n)
                    if f"{p2}" not in GL.normais:
                        GL.normais[f"{p2}"] = [n]
                    else:
                        GL.normais[f"{p2}"].append(n)
                    if f"{p3}" not in GL.normais:
                        GL.normais[f"{p3}"] = [n]
                    else:
                        GL.normais[f"{p3}"].append(n)  
                    triangulos.append([p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],p3[0],p3[1],p3[2]])
                        # vira = 1
                    t+=1
                for k in range(len(triangulos)):
                    # print(f"triangulos {k}\n")
                    GL.triangleSet(triangulos[k],colors, coordIndex, colorPerVertex, color, colorIndex,
                        tex[i], texCoordIndex, 1)           


        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def box(size, colors):
        """Função usada para renderizar Boxes."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Box
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Box : size = {0}".format(size)) # imprime no terminal pontos
        print("Box : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        gpu.GPU.draw_pixel([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def sphere(radius, colors):
        """Função usada para renderizar Esferas."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Sphere
        # A função sphere é usada para desenhar esferas na cena. O esfera é centrada no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da esfera que está sendo criada. Para desenha essa esfera você vai
        # precisar tesselar ela em triângulos, para isso encontre os vértices e defina
        # os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Sphere : radius = {0}".format(radius)) # imprime no terminal o raio da esfera
        print("Sphere : colors = {0}".format(colors)) # imprime no terminal as cores

    @staticmethod
    def cone(bottomRadius, height, colors):
        """Função usada para renderizar Cones."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Cone
        # A função cone é usada para desenhar cones na cena. O cone é centrado no
        # (0, 0, 0) no sistema de coordenadas local. O argumento bottomRadius especifica o
        # raio da base do cone e o argumento height especifica a altura do cone.
        # O cone é alinhado com o eixo Y local. O cone é fechado por padrão na base.
        # Para desenha esse cone você vai precisar tesselar ele em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Cone : bottomRadius = {0}".format(bottomRadius)) # imprime no terminal o raio da base do cone
        print("Cone : height = {0}".format(height)) # imprime no terminal a altura do cone
        print("Cone : colors = {0}".format(colors)) # imprime no terminal as cores

    @staticmethod
    def cylinder(radius, height, colors):
        """Função usada para renderizar Cilindros."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/geometry3D.html#Cylinder
        # A função cylinder é usada para desenhar cilindros na cena. O cilindro é centrado no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da base do cilindro e o argumento height especifica a altura do cilindro.
        # O cilindro é alinhado com o eixo Y local. O cilindro é fechado por padrão em ambas as extremidades.
        # Para desenha esse cilindro você vai precisar tesselar ele em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Cylinder : radius = {0}".format(radius)) # imprime no terminal o raio do cilindro
        print("Cylinder : height = {0}".format(height)) # imprime no terminal a altura do cilindro
        print("Cylinder : colors = {0}".format(colors)) # imprime no terminal as cores

    @staticmethod
    def navigationInfo(headlight):
        """Características físicas do avatar do visualizador e do modelo de visualização."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/navigation.html#NavigationInfo
        # O campo do headlight especifica se um navegador deve acender um luz direcional que
        # sempre aponta na direção que o usuário está olhando. Definir este campo como TRUE
        # faz com que o visualizador forneça sempre uma luz do ponto de vista do usuário.
        # A luz headlight deve ser direcional, ter intensidade = 1, cor = (1 1 1),
        # ambientIntensity = 0,0 e direção = (0 0 −1).
        if headlight:
            GL.directionalLight(ambientIntensity=[0,0],color=[1,1,1],intensity=1,direction=[0,0,-1])
        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("NavigationInfo : headlight = {0}".format(headlight)) # imprime no terminal

    @staticmethod
    def directionalLight(ambientIntensity, color, intensity, direction):
        """Luz direcional ou paralela."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/lighting.html#DirectionalLight
        # Define uma fonte de luz direcional que ilumina ao longo de raios paralelos
        # em um determinado vetor tridimensional. Possui os campos básicos ambientIntensity,
        # cor, intensidade. O campo de direção especifica o vetor de direção da iluminação
        # que emana da fonte de luz no sistema de coordenadas local. A luz é emitida ao
        # longo de raios paralelos de uma distância infinita.
        GL.directionalL["ambientIntensity"] = ambientIntensity
        GL.directionalL["color"] = color
        GL.directionalL["intensity"] = intensity
        GL.directionalL["direction"] = direction
        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("DirectionalLight : ambientIntensity = {0}".format(ambientIntensity))
        # print("DirectionalLight : color = {0}".format(color)) # imprime no terminal
        # print("DirectionalLight : intensity = {0}".format(intensity)) # imprime no terminal
        # print("DirectionalLight : direction = {0}".format(direction)) # imprime no terminal

    @staticmethod
    def pointLight(ambientIntensity, color, intensity, location):
        """Luz pontual."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/lighting.html#PointLight
        # Fonte de luz pontual em um local 3D no sistema de coordenadas local. Uma fonte
        # de luz pontual emite luz igualmente em todas as direções; ou seja, é omnidirecional.
        # Possui os campos básicos ambientIntensity, cor, intensidade. Um nó PointLight ilumina
        # a geometria em um raio de sua localização. O campo do raio deve ser maior ou igual a
        # zero. A iluminação do nó PointLight diminui com a distância especificada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.

        
        print("PointLight : ambientIntensity = {0}".format(ambientIntensity))
        print("PointLight : color = {0}".format(color)) # imprime no terminal
        print("PointLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("PointLight : location = {0}".format(location)) # imprime no terminal

    @staticmethod
    def fog(visibilityRange, color):
        """Névoa."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/environmentalEffects.html#Fog
        # O nó Fog fornece uma maneira de simular efeitos atmosféricos combinando objetos
        # com a cor especificada pelo campo de cores com base nas distâncias dos
        # vários objetos ao visualizador. A visibilidadeRange especifica a distância no
        # sistema de coordenadas local na qual os objetos são totalmente obscurecidos
        # pela névoa. Os objetos localizados fora de visibilityRange do visualizador são
        # desenhados com uma cor de cor constante. Objetos muito próximos do visualizador
        # são muito pouco misturados com a cor do nevoeiro.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Fog : color = {0}".format(color)) # imprime no terminal
        print("Fog : visibilityRange = {0}".format(visibilityRange))

    @staticmethod
    def timeSensor(cycleInterval, loop):
        """Gera eventos conforme o tempo passa."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/time.html#TimeSensor
        # Os nós TimeSensor podem ser usados para muitas finalidades, incluindo:
        # Condução de simulações e animações contínuas; Controlar atividades periódicas;
        # iniciar eventos de ocorrência única, como um despertador;
        # Se, no final de um ciclo, o valor do loop for FALSE, a execução é encerrada.
        # Por outro lado, se o loop for TRUE no final de um ciclo, um nó dependente do
        # tempo continua a execução no próximo ciclo. O ciclo de um nó TimeSensor dura
        # cycleInterval segundos. O valor de cycleInterval deve ser maior que zero.

        # Deve retornar a fração de tempo passada em fraction_changed

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("TimeSensor : cycleInterval = {0}".format(cycleInterval)) # imprime no terminal
        # print("TimeSensor : loop = {0}".format(loop))

        # Esse método já está implementado para os alunos como exemplo
        epoch = time.time()  # time in seconds since the epoch as a floating point number.
        fraction_changed = (epoch % cycleInterval) / cycleInterval

        return fraction_changed
    @staticmethod
    def splinePositionInterpolator(set_fraction, key, keyValue, closed):
        """Interpola não linearmente entre uma lista de vetores 3D."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/interpolators.html#SplinePositionInterpolator
        # Interpola não linearmente entre uma lista de vetores 3D. O campo keyValue possui
        # uma lista com os valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantos vetores 3D quanto os
        # quadros-chave no key. O campo closed especifica se o interpolador deve tratar a malha
        # como fechada, com uma transições da última chave para a primeira chave. Se os keyValues
        # na primeira e na última chave não forem idênticos, o campo closed será ignorado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("SplinePositionInterpolator : set_fraction = {0}".format(set_fraction))
        # print("SplinePositionInterpolator : key = {0}".format(key)) # imprime no terminal
        # print("SplinePositionInterpolator : keyValue = {0}".format(keyValue))
        # print("SplinePositionInterpolator : closed = {0}".format(closed))
        vetores = list(zip(keyValue[::3], keyValue[1::3], keyValue[2::3]))
        if set_fraction <= key[0]:
            return list(vetores[0])
        if set_fraction >= key[-1]:
            return list(vetores[-1])
        # dicionario = dict(zip(key, vetores))
        maior = 0
        menor = 0
        while key[maior]<=set_fraction:
            maior+=1
        menor = maior-1
        # print(dicionario)
        # print(maior, menor)
        l1 = [-0.5,1.5,-1.5,0.5]
        l2 = [1,-2.5,2,-0.5]
        l3 = [-0.5,0,0.5,0]
        l4 = [0,1,0,0]
        if closed and vetores[0] ==  vetores[-1]:
    # vizinhos circulares (pulando o ponto repetido)
            n = len(vetores) - 1            # último == primeiro, então ignora um deles
            p0 = vetores[(menor - 1) % n]
            p1 = vetores[menor]
            p2 = vetores[maior % n]
            p3 = vetores[(maior + 1) % n]
        else:
            p0 = vetores[max(menor - 1, 0)]
            p1 = vetores[menor]
            p2 = vetores[maior]
            p3 = vetores[min(maior + 1, len(vetores) - 1)]
        x = [p0[0],p1[0],p2[0],p3[0]]    
        y = [p0[1],p1[1],p2[1],p3[1]]    
        z = [p0[2],p1[2],p2[2],p3[2]]
        t = (set_fraction - key[menor]) / (key[maior] - key[menor])    
        matriz = [l1,l2,l3,l4]
        fracao = [t**3,t**2,t,1]
        temp_x = np.matmul(matriz,x)
        temp_y = np.matmul(matriz,y)
        temp_z = np.matmul(matriz,z)
        vx = np.matmul(fracao,temp_x)
        vy = np.matmul(fracao,temp_y)
        vz = np.matmul(fracao,temp_z)
        # print(vx,vy,vz)
        value_changed = [vx, vy, vz]
        # GL.encontra(set_fraction,key)
        return value_changed

    @staticmethod
    def orientationInterpolator(set_fraction, key, keyValue):
        """Interpola entre uma lista de valores de rotação especificos."""
        # https://www.web3d.org/specifications/X3Dv4/ISO-IEC19775-1v4-IS/Part01/components/interpolators.html#OrientationInterpolator
        # Interpola rotações são absolutas no espaço do objeto e, portanto, não são cumulativas.
        # Uma orientação representa a posição final de um objeto após a aplicação de uma rotação.
        # Um OrientationInterpolator interpola entre duas orientações calculando o caminho mais
        # curto na esfera unitária entre as duas orientações. A interpolação é linear em
        # comprimento de arco ao longo deste caminho. Os resultados são indefinidos se as duas
        # orientações forem diagonalmente opostas. O campo keyValue possui uma lista com os
        # valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantas rotações 3D quanto os
        # quadros-chave no key.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("OrientationInterpolator : set_fraction = {0}".format(set_fraction))
        # print("OrientationInterpolator : key = {0}".format(key)) # imprime no terminal
        # print("OrientationInterpolator : keyValue = {0}".format(keyValue))
        vetores = list(zip(keyValue[::4], keyValue[1::4], keyValue[2::4],keyValue[3::4]))
        if set_fraction <= key[0]:
            return list(vetores[0])
        if set_fraction >= key[-1]:
            return list(vetores[-1])
        # dicionario = dict(zip(key, vetores))

        maior = 0
        menor = 0
        while key[maior]<=set_fraction:
            maior+=1
        menor = maior-1
        p1 = vetores[menor]
        p2 = vetores[maior]
        t = (set_fraction - key[menor]) / (key[maior] - key[menor])
        R1 =[0,0,0,0]
        R2 = [0,0,0,0]
        R1[3] = math.cos(p1[3]/2)    
        R1[0] = math.sin(p1[3]/2)*p1[0]
        R1[1] = math.sin(p1[3]/2)*p1[1]
        R1[2] = math.sin(p1[3]/2)*p1[2]
        
        
        R2[3] = math.cos(p2[3]/2)    
        R2[0] = math.sin(p2[3]/2)*p2[0]
        R2[1] = math.sin(p2[3]/2)*p2[1]
        R2[2] = math.sin(p2[3]/2)*p2[2]
        # falta fazer o slerp
        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0, 0, 1, 0]
        # theta = np.dot(R1,R2)
        # slerp = [math.sin((1-t)*theta) / math.sin(theta) ] * R1  +  [ math.sin(t*theta) / math.sin(theta) ] * R2
        dot = np.dot(R1,R2)
        if dot<0:
            dot = -dot
            R1 = np.array(R1)*-1
        if dot > 0.9995:            # quase iguais: evita divisão por ~0
            r = np.array(R2) + t * (np.array(R2) - np.array(R1))
            return r / np.linalg.norm(r)
        theta = math.acos(dot)
        a = math.sin((1-t)*theta)/math.sin(theta)
        b = math.sin(t*theta)/math.sin(theta)
        slerp = a*np.array(R1) +b*np.array(R2)
        # print(slerp[3])
        value_changed[3] = 2*math.acos(slerp[3])
        value_changed[0] = slerp[0]/(math.sin(value_changed[3]/2))
        value_changed[1] = slerp[1]/(math.sin(value_changed[3]/2))
        value_changed[2] = slerp[2]/(math.sin(value_changed[3]/2))
        return value_changed

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""
