import math
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import copy
import numpy as np


sirinaProzora = 1024
visinaProzora = 1024

# Zadano ociste
ociste = [-20.0, -10.0, -10.0]

# INPUT ---------------------------------------------------------------------
# Originalni zapisi vrhova i poligona koji se ne mijenjaju tijekom izvodenja
Vorg = []
Forg = []
# Zapisi vrhova i poligona koji se mogu mijenjati tijekom izvodenja
V = []
F = []
# Zapis ucitanih tocaka krivulje
tockeKrivulje = []
# ---------------------------------------------------------------------------

# Pohrana izracunatih tocaka putanje objekta
put = []
putSegmentiran = []
tablica = np.array([
    [-1, 3, -3, 1],
    [3, -6, 3, 0],
    [-3, 0, 3, 0],
    [1, 4, 1, 0]
])

# Pohrana izracunatih smjerova tangenti iz odgovarajucih tocaka putanje objekta
tangenta = []
tablicaTangente = np.array([
    [-1, 3, -3, 1],
    [2, -4, 2, 0],
    [-1, 0, 1, 0]
])


# Ucitavanje objekta -> ispunjava popis vrhova i poligona
def ucitajObjekt(ime):
    file = open(ime, "r").readlines()
    for linija in file:
        linija = linija.strip()
        segmenti = linija.split(" ")
        if segmenti[0] == 'v':
            Vorg.append([float(segmenti[1]), float(segmenti[2]), float(segmenti[3])])
            V.append([float(segmenti[1]), float(segmenti[2]), float(segmenti[3])])
        elif segmenti[0] == 'f':
            Forg.append((int(segmenti[1]), int(segmenti[2]), int(segmenti[3])))
            F.append((int(segmenti[1]), int(segmenti[2]), int(segmenti[3])))


# Ucitavanje tocaka koje definiraju krivulju -> ispunjava popis tocaka krivulje
def ucitajTockeKrivulje(ime):
    file = open(ime, "r").readlines()
    for linija in file:
        segmenti = linija.strip().split(' ')
        tockeKrivulje.append((float(segmenti[0]), float(segmenti[1]), float(segmenti[2])))


# Funkcija koja se poziva jednom na pocetku kako bi se izracunale tocke putanje i smjerovi tangenti u njima
def izracunajPutanju():
    brojSegmenata = len(tockeKrivulje) - 3
    for segment in range(0, brojSegmenata):
        segmenti = []

        # Tocke segmenta
        A = tockeKrivulje[segment]
        B = tockeKrivulje[segment+1]
        C = tockeKrivulje[segment+2]
        D = tockeKrivulje[segment+3]

        # Parametar svakog segmenta, prostorna rezolucija
        for t in np.linspace(0, 1, 100):
            p = [0, 0, 0]
            pTan = [0, 0, 0]
            TT = np.array([[pow(t, 3), pow(t, 2), t, 1]])
            TTTan = np.array([[pow(t, 2), t, 1]])
            # Za svaku os
            for koordinata in range(0, 3):
                BB = (1/6)*tablica
                BBTan = (1/2)*tablicaTangente
                RR = np.array([
                    [A[koordinata]],
                    [B[koordinata]],
                    [C[koordinata]],
                    [D[koordinata]]
                ])
                p[koordinata] = (np.matmul(np.matmul(TT, BB), RR))[0][0]
                pTan[koordinata] = (np.matmul(np.matmul(TTTan, BBTan), RR))[0][0]
            put.append(p)
            tangenta.append(pTan)
            segmenti.append(p)
        putSegmentiran.append(segmenti)
    #print(tangenta)


# Funkcija za iscrtavanje putanje i tocaka kojima je krivulja zadana
def iscrtajPutanju():
    # Iscrtavanje segmenata u razlicitim bojama (manualno namjestanje)
    brojSegmenata = len(tockeKrivulje) - 3
    cnt = len(put)/brojSegmenata

    bojaR = 0
    bojaG = 0
    bojaB = 255
    glBegin(GL_POINTS)
    glColor3ub(bojaR, bojaG, bojaB)
    cntt = 0
    for p in put:
        glVertex3f(p[0], p[1], p[2])
        cntt += 1
        if cnt == cntt:
            bojaB -= 30
            bojaG += 30
            bojaR += 30
            glColor3ub(bojaR, bojaG, bojaB)
            cntt = 0
    glEnd()

    # Zadane tocke koje definiraju krivulju
    glBegin(GL_LINE_LOOP)
    glColor3ub(255, 0, 0)
    for t in tockeKrivulje:
        glVertex3f(t[0], t[1], t[2])
    glEnd()


# Iscrtavanje trenutnog objekta u crvenoj boji
def iscrtajObjekt():
    for f in F:
        A = V[f[0]-1]
        B = V[f[1]-1]
        C = V[f[2]-1]
        glBegin(GL_LINE_LOOP)
        glColor3ub(255, 0, 0)
        glVertex3f(A[0], A[1], A[2])
        glVertex3f(B[0], B[1], B[2])
        glVertex3f(C[0], C[1], C[2])
        glEnd()


def myDisplay():
    print("Pozvan myDisplay")

    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Namjestanje centra objekta
    centroid = [0, 0, 0]
    for i in range(0, len(V)):
        for j in range(0, 3):
            centroid[j] += V[i][j]
    for j in range(0, 3):
        centroid[j] /= len(V)

    for i in range(0, len(V)):
        for j in range(0, 3):
            V[i][j] -= centroid[j]

    # Pocetna orijentacija i ciljna orijentacija u smjeru tangente prve tocke puta
    s = [0, 0, 1]
    e = tangenta[0]
    # Izračun osi i kuta rotacije
    os = [s[1] * e[2] - e[1] * s[2], -(s[0] * e[2] - e[0] * s[2]), s[0] * e[1] - s[1] * e[0]]
    kosinus = (s[0] * e[0] + s[1] * e[1] + s[2] * e[2]) / (np.linalg.norm(s) * np.linalg.norm(e))
    stupnjevi = (math.acos(kosinus) * 180) / math.pi  # Preračun u stupnjeve

    glPushMatrix()
    glTranslatef(put[0][0], put[0][1], put[0][2])
    glRotatef(stupnjevi, os[0], os[1], os[2])
    iscrtajObjekt()
    glPopMatrix()
    iscrtajPutanju()
    glutSwapBuffers()


def updatePerspective():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(sirinaProzora/visinaProzora), 0.1, 800.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(ociste[0], ociste[1], ociste[2], 5.0, 5.0, 30.0, 0.0, 1.0, 0.0)


# Funkcija updateanja prozora
def myReshape(w, h):
    print("Reshape: width =", w, " height =", h)
    glViewport(0, 0, w, h)
    updatePerspective()


# Funkcija koja translatira trenutne vrijednosti vrhova
def translatirajTockeObjekta(start, cilj):
    d = [cilj[0] - start[0], cilj[1] - start[1], cilj[2] - start[2]]
    for i in range(0, len(V)):
        V[i][0] = V[i][0] + d[0]
        V[i][1] = V[i][1] + d[1]
        V[i][2] = V[i][2] + d[2]


# Funkcija koji vrti animaciju, pokrece se pritiskom na 'p'
def animacija():
    # Namjestanje polozaja objekta na njegov centar
    centroid = [0, 0, 0]
    for i in range(0, len(V)):
        for j in range(0, 3):
            centroid[j] += V[i][j]
    for j in range(0, 3):
        centroid[j] /= len(V)

    for i in range(0, len(V)):
        for j in range(0, 3):
            V[i][j] -= centroid[j]

    # Pocetna orijentacija
    s = [0, 0, 1]
    cnt = 0
    k = 1   # Koeficijent duljine tangente
    for e in tangenta:
        # Vremenska rezolucija
        time.sleep(0.001)

        # Izračun osi i kuta rotacije
        os = [s[1]*e[2] - e[1]*s[2], -(s[0]*e[2] - e[0]*s[2]), s[0]*e[1] - s[1]*e[0]]
        kosinus = (s[0]*e[0] + s[1]*e[1] + s[2]*e[2])/(np.linalg.norm(s) * np.linalg.norm(e))
        stupnjevi = (math.acos(kosinus) * 180) / math.pi  # Preračun u stupnjeve

        # Brisanje platna i iscrtavanje putanje
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        iscrtajPutanju()

        # Iscrtavanje tangente
        glBegin(GL_LINE_LOOP)
        glColor3ub(255, 0, 0)
        glVertex3f(put[cnt][0], put[cnt][1], put[cnt][2])
        glVertex3f(put[cnt][0] + k*e[0], put[cnt][1] + k*e[1], put[cnt][2] + k*e[2])
        glEnd()
        # --------------------

        # Translatiranje objekta na tocku puta i rotiranje oko izracunate osi rotacije za izracunati kut
        glPushMatrix()
        glTranslatef(put[cnt][0], put[cnt][1], put[cnt][2])
        glRotatef(stupnjevi, os[0], os[1], os[2])
        iscrtajObjekt()
        glPopMatrix()

        cnt += 1

        glutSwapBuffers()




# Funkcija koja obuhvaca kontrolu tipkovnicom za pomicanje ocista
def myKeyboard(theKey, mouseX, mouseY):
    theKey = str(theKey).strip('')[-2]
    pomak = 1
    if theKey == 'y':
        ociste[0] = ociste[0]-pomak
    elif theKey == 'x':
        ociste[0] = ociste[0]+pomak
    elif theKey == 'c':
        ociste[1] = ociste[1]-pomak
    elif theKey == 'v':
        ociste[1] = ociste[1]+pomak
    elif theKey == 'b':
        ociste[2] = ociste[2]-pomak
    elif theKey == 'n':
        ociste[2] = ociste[2]+pomak
    elif theKey == 'r':
        ociste[0] = 0.0
        ociste[1] = 0.0
        ociste[2] = 0.0
    elif theKey == 'p':
        animacija()
    updatePerspective()
    glutPostRedisplay()


# Translatira objekt na prvu tocku putanje
def inicijalnaTranslacija():
    cilj = put[0]

    # Računanje centroida vrhova objekta
    centroid = [0, 0, 0]
    for vrh in Vorg:
        for i in range(0, 3):
            centroid[i] += vrh[i]
    for i in range(0, 3):
        centroid[i] /= len(Vorg)

    # Translacija trenutnih vrhova
    pomak = [cilj[0]-centroid[0], cilj[1]-centroid[1], cilj[2]-centroid[2]]
    for i in range(0, len(V)):
        for j in range(0, 3):
            V[i][j] += pomak[j]

# Izvodenje glavnog dijela programa
ucitajObjekt("bird.obj")
ucitajTockeKrivulje("krivulja.txt")
izracunajPutanju()
#inicijalnaTranslacija()

# Kreiranje prozora
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
glutInitWindowSize(sirinaProzora, visinaProzora)
glutInitWindowPosition(100, 100)
glutInit()
window = glutCreateWindow("Racunalna grafika, 1. labos")
# Zadavanje funkcija
glutReshapeFunc(myReshape)
glutDisplayFunc(myDisplay)
glutKeyboardFunc(myKeyboard)

glutMainLoop()
