import math
import time
import copy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import numpy


global vrijeme
global cestice
global broj_cestica
ociste = [10, 10, 20]

class cestica():
    pozicija = None     # [x, y, z]
    brzina = None       # [brzina_x, brzina_y, brzina_z]

    boja = None         # [Red, Green, Blue, Opacity]

    rodena = None       # Samoinicijalizacija, zapis kada je rodena
    starost = None      # Samoinicijalizacija, trenutna starost
    vijek = None        # Zivotni vijek cestice

    def __init__(self, pozicija, brzina, boja, vijek):
        global vrijeme
        self.pozicija = pozicija
        self.brzina = brzina
        self.boja = boja
        self.vijek = vijek
        self.starost = 0
        self.rodena = vrijeme


# Funkcija koja generira potreban broj cestica do ispunjenja sustava
def generiraj_cestice():
    global cestice, broj_cestica
    ognjiste = [0, 0, 0]    # Centar izvora cestica
    radijus = 3             # Radijus izvora cestica
    for i in range(0, broj_cestica-len(cestice)):
        pozicija = [numpy.random.normal()*radijus+ognjiste[0],
                    numpy.random.normal()*radijus+ognjiste[1],
                    numpy.random.normal()*radijus+ognjiste[2]]
        brzina = [0, 0, 0.1]
        boja = [255, 0, 0, 1]
        vijek = numpy.random.uniform(50,200)
        cestice.append(cestica(pozicija, brzina, boja, vijek))


def ostari_cestice():
    global cestice
    for i in range(0, len(cestice)):
        cestice[i].starost += 1
    return


def ukloni_prestare_cestice():
    global cestice
    prezivjele = []
    for cestica in cestice:
        if cestica.starost <= cestica.vijek:
            prezivjele.append(cestica)
    cestice = prezivjele
    return


def translatiraj_cestice():
    global cestice
    for i in range(0, len(cestice)):
        for j in range(0, 3):
            cestice[i].pozicija[j] += cestice[i].brzina[j]
    return


def iscrtaj_cesticu(cestica):
    velicina = 10
    pozicija = cestica.pozicija
    starosna_boja = cestica.starost / (cestica.vijek+0.001)
    glPointSize(velicina/2.0)
    glBegin(GL_POINTS)
    glColor3ub(255, int(255*starosna_boja), 0)
    glVertex3f(pozicija[0], pozicija[1], pozicija[2])
    glEnd()
    return


def idle():
    global vrijeme, cestice, broj_cestica

    time.sleep(0.01)
    ostari_cestice()
    ukloni_prestare_cestice()
    generiraj_cestice()

    # Takt
    translatiraj_cestice()

    # Brisanje platna
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Iscrtavanje
    for cestica in cestice:
        iscrtaj_cesticu(cestica)

    glutSwapBuffers()
    vrijeme += 1

    updatePerspective()
    glutPostRedisplay()

def myDisplay():
    return


# Inicijalizacija sustava cestica i pogon sustava
def main():
    global vrijeme, cestice, broj_cestica

    # Parametri sustava cestica i inicijalizacija
    vrijeme = 0
    cestice = []
    broj_cestica = 2000

    # Kreiranje i postavljanje prozora
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
    glutInitWindowSize(1024, 1024)
    glutInitWindowPosition(100, 100)
    glutInit()
    window = glutCreateWindow("Racunalna grafika, 2. labos")
    glutReshapeFunc(myReshape)
    glutDisplayFunc(myDisplay)
    glutKeyboardFunc(myKeyboard)
    glutIdleFunc(idle)
    glutMainLoop()


def myReshape(w, h):
    print("Reshape: width =", w, " height =", h)
    glViewport(0, 0, w, h)
    updatePerspective()



def updatePerspective():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(1024/1024), 0.1, 800.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(ociste[0], ociste[1], ociste[2], 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)


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


if __name__ == "__main__":
    main()