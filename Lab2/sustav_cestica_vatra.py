import math
import random
import numpy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image


global vrijeme
global cestice
global broj_cestica

ognjiste = [0, 0, -10]
ociste = [30, 30, 10]


# Razred koji predstavlja jednu cesticu
class cestica():
    pozicija = None     # [x, y, z]
    brzina = None       # [brzina_x, brzina_y, brzina_z]

    rodena = None       # Samoinicijalizacija, zapis kada je rodena
    starost = None      # Samoinicijalizacija, trenutna starost
    vijek = None        # Zivotni vijek cestice

    def __init__(self, pozicija, brzina, vijek):
        global vrijeme
        self.pozicija = pozicija
        self.brzina = brzina
        self.vijek = vijek
        self.starost = 0
        self.rodena = vrijeme


# Generira potreban broj cestica do ispunjenja sustava
def generiraj_cestice():
    global cestice, broj_cestica, ognjiste
    radijus = 2.5               # Radijus izvora cestica
    dev = 0.5                   # Devijacija izvora cestica

    # parametri generirane cestice, eksperimentalno dobiveni
    for i in range(0, broj_cestica-len(cestice)):
        pozicija = [numpy.random.normal(0, dev)*radijus,
                    numpy.random.normal(0, dev)*radijus,
                    max(0, numpy.random.normal(0, dev)*radijus)]
        brzina = [0.0, 0, random.uniform(0.18, 0.22)]
        vijek = numpy.random.uniform(1, 100)

        cestice.append(cestica(pozicija, brzina, vijek))


# Azurira trajanje zivota svih cestica
def ostari_cestice():
    global cestice
    for i in range(0, len(cestice)):
        cestice[i].starost += 1
    return


# Uklanja sve odumrle cestice
def ukloni_prestare_cestice():
    global cestice
    prezivjele = []
    for cestica in cestice:
        if cestica.starost <= cestica.vijek:
            prezivjele.append(cestica)
    cestice = prezivjele
    return


# Obavlja kretanje cestica prema njihovoj brzini
def translatiraj_cestice():
    global cestice
    for i in range(0, len(cestice)):
        for j in range(0, 3):
            cestice[i].pozicija[j] += cestice[i].brzina[j]
    return


# Iscrtava jednu cesticu, translatira na ognjiste i rotira prema ocistu
def iscrtaj_cesticu(cestica):
    # Odredivanje stadija zivota cestice
    stadij = 63 * (cestica.starost / cestica.vijek)
    neprozirnost = max(0.1, 1-(stadij/63))

    velicina = 1 - stadij/1000      # Velicina cestice
    pozicija = cestica.pozicija     # Pozicija cestice
    centar = [pozicija[0]+velicina/2, pozicija[1], pozicija[2]+velicina/2]  # Centar cestice

    # Translacija i rotacija poligona
    glPushMatrix()
    glTranslatef(centar[0]+ognjiste[0], centar[1]+ognjiste[1], centar[2]+ognjiste[2])
    glTranslatef(-centar[0], -centar[1], -centar[2])

    # Cestica mijenja izgled s obzirom na stadij svog zivota
    redak = int(stadij / 8)
    stupac = int(stadij % 8)
    redak8 = redak/8
    stupac8 = stupac/8

    # Iscrtavanje teksturiranih poligona
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glColor4f(1, 1, 1, neprozirnost)

    glTexCoord2f(1/8 + stupac8, 1/8 + redak8)   # donji desni
    glVertex3f(pozicija[0], pozicija[1], pozicija[2])

    glTexCoord2f(stupac8, 1/8 + redak8)         # donji lijevi
    glVertex3f(pozicija[0]+velicina, pozicija[1], pozicija[2])

    glTexCoord2f(stupac8, redak8)               # gornji lijevi
    glVertex3f(pozicija[0]+velicina, pozicija[1], pozicija[2]+velicina)

    glTexCoord2f(1/8 + stupac8, redak8)         # gornji desni
    glVertex3f(pozicija[0], pozicija[1], pozicija[2]+velicina)

    glEnd()
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()

    return


# Pogon sustava cestica
def idle():
    global vrijeme, cestice, broj_cestica

    ostari_cestice()            # Azuriranje starosti cestica
    ukloni_prestare_cestice()   # Uklanjanje odumrlih cestica
    generiraj_cestice()         # Generiranje novih cestica

    # Takt
    translatiraj_cestice()      # Pomicanje cestica s obzirom na njihovu brzinu

    # Brisanje platna
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Iscrtavanje
    for cestica in cestice:
        iscrtaj_cesticu(cestica)

    # Prikaz
    glutSwapBuffers()
    # Prolazi vrijeme
    vrijeme += 1

    updatePerspective()
    glutPostRedisplay()


def myDisplay():
    return


# Inicijalizacija sustava cestica i pustanje sustava u pogon
def main():
    global vrijeme, cestice, broj_cestica

    # Parametri sustava cestica i inicijalizacija
    vrijeme = 0
    cestice = []
    broj_cestica = 1000

    # Kreiranje i postavljanje prozora
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
    glutInitWindowSize(1024, 1024)
    glutInitWindowPosition(100, 100)
    glutInit()
    window = glutCreateWindow("Racunalna grafika, 2. labos")
    # Transparentnost
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Registracija funkcija
    glutReshapeFunc(myReshape)
    glutDisplayFunc(myDisplay)
    glutKeyboardFunc(myKeyboard)
    glutIdleFunc(idle)

    # Ucitavanje teksture
    ucitaj_teksturu("vatra.jpg")
    glutMainLoop()


# Oblikovanje prozora
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


# Utjecaj vjetra, tipka 'u' daje nasumicne vrijednosti za "pravi" vjetar
def vjetar(tipka):
    global cestice
    vjetar = 0.05
    if tipka == 'q':
        promjena = [vjetar, 0, 0]
    if tipka == 'w':
        promjena = [-vjetar, 0, 0]
    if tipka == 'e':
        promjena = [0, vjetar, 0]
    if tipka == 'r':
        promjena = [0, -vjetar, 0]
    if tipka == 't':
        promjena = [0, 0, vjetar]
    if tipka == 'z':
        promjena = [0, 0, -vjetar]
    if tipka == 'u':
        k = 100
        promjena = [random.uniform(0, 1)/k, random.uniform(0, 1)/k, random.uniform(0, 0.5)/k]
    for i in range(0, len(cestice)):
        for j in range(0, 3):
            cestice[i].brzina[j] += promjena[j]
    return


# Barata inputom tipkovnice - promjena ocista i vjetra
def myKeyboard(theKey, mouseX, mouseY):
    global broj_cestica
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
    elif theKey == 'a':
        ociste[0] = 30.0
        ociste[1] = 30.0
        ociste[2] = 10.0
    elif theKey == 's':
        broj_cestica = max(0, broj_cestica - 200)
    elif theKey == 'd':
        broj_cestica = min(10000, broj_cestica + 200)
    elif theKey == 'f':
        for i in range(0, 3):
            ociste[i] = ognjiste[i]
    else:
        vjetar(theKey)

    updatePerspective()
    glutPostRedisplay()


# Ucitavanje teksture
def ucitaj_teksturu(tekstura):
    sprite = Image.open(tekstura)
    spriteData = numpy.array(list(sprite.getdata()), numpy.uint8)

    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, sprite.size[0], sprite.size[1],
                 0, GL_RGB, GL_UNSIGNED_BYTE, spriteData)

    sprite.close()
    return textureID


if __name__ == "__main__":
    main()
