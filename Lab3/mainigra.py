import math
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import winsound
import numpy
from PIL import Image

# 'vrabac' ili 'sokol' ili 'bot'
trigger = 'bot'
# Perspektiva vrapca ili sokola // 'vrabac' ili 'sokol'
perspektiva = 'vrabac'



########################### SUSTAV ČESTICA - KIŠA ###############################

cestice = []
broj_cestica = 1000
oblak = [15, 35, 15]    # Položaj kišnog oblaka
razina_tla = -20        # z koordinata razine tla
# Razred koji predstavlja jednu česticu, odnosno kapljicu kiše
class cestica():
    pozicija = None     # [x, y, z]
    brzina = None       # [brzina_x, brzina_y, brzina_z]
    kolizija = None     # Je li čestica pogodila vrabca, odnosno brojač koliko još ima uspravnog leta

    def __init__(self, pozicija, brzina):
        global vrijeme
        self.pozicija = pozicija
        self.brzina = brzina
        self.kolizija = 0


# Generira potreban broj cestica do ispunjenja sustava
def generiraj_cestice():
    global cestice, broj_cestica
    radijus = 30               # Radijus izvora cestica
    dev = 1                   # Devijacija izvora cestica

    # parametri generirane cestice, eksperimentalno dobiveni
    for i in range(0, broj_cestica-len(cestice)):
        pozicija = [numpy.random.normal(0, dev)*radijus,
                    numpy.random.normal(0, dev)*radijus,
                    max(0, numpy.random.normal(0, dev)*radijus)]
        #brzina = [0.0, -random.uniform(0.18, 0.22), 0]
        brzina = [0, -0.2, 0]
        cestice.append(cestica(pozicija, brzina))


# Uklanja sve odumrle cestice
def ukloni_prestare_cestice():
    global cestice, razina_tla, oblak
    prezivjele = []
    for cestica in cestice:
        if cestica.pozicija[1] + oblak[1] >= razina_tla:
            prezivjele.append(cestica)
    cestice = prezivjele
    return


# Obavlja kretanje cestica prema njihovoj brzini
def translatiraj_cestice():
    global cestice
    kolizijaCestica()
    for i in range(0, len(cestice)):
        for j in range(0, 3):
            cestice[i].pozicija[j] += cestice[i].brzina[j]
        cestice[i].pozicija[1] += funkcijaOdbijanja(cestice[i].kolizija)
        cestice[i].kolizija = max(cestice[i].kolizija-1, 0)
    return


# Iterativno se poziva za svaku česticu više puta tokom odbijanja
def funkcijaOdbijanja(counter):
    return counter/4


# Vraća normu proslijeđenog vektora
def normaVektora(v):
    return math.sqrt(pow(v[0], 2) + pow(v[1], 2) + pow(v[2], 2))


# Funkcija koja postavlja odbijanje čestice ako je pala na vrabca
def kolizijaCestica():
    global cestice, kugla_vrabac_radijus, polozaj_vrabac, oblak
    for i in range(0, len(cestice)):
        if normaVektora(razlikaVektora(polozaj_vrabac, zbrojVektora(cestice[i].pozicija, oblak))) <= kugla_vrabac_radijus:
            cestice[i].kolizija = 5
            print("kol")
    return


# Iscrtava jednu česticu, translatira na položaj oblaka
def iscrtaj_cesticu(cestica):
    global oblak
    pozicija = cestica.pozicija     # Pozicija cestice

    # Iscrtavanje teksturiranih poligona
    glLineWidth(3)
    glBegin(GL_LINES)
    glColor4f(0, 0, 1, 0.8)
    glVertex3f(pozicija[0] + oblak[0], pozicija[1] + oblak[1], pozicija[2] + oblak[2])
    glVertex3f(pozicija[0] + oblak[0], pozicija[1]-1+oblak[1], pozicija[2] + oblak[2])
    glEnd()
    glLineWidth(1)
    return


#################### GOTOV SUSTAV ČESTICA ####################


##################### PROZOR I SAMA IGRA #####################

sirinaProzora = 1024
visinaProzora = 1024

kugla_sokol_radijus = 3
kugla_vrabac_radijus = 1

# Zadano ociste i glediste
ociste = [-30.0, -20.0, -20.0]
glediste = [5.0, 5.0, 30.0]
up_vektor = [0, 1, 0]

polozaj_vrabac = [0, 0, 0]
polozaj_sokol = [0, 0, 0]
brzina_sokol = 0.2
trenutni_smjer_sokola = [0.5, 0, 0.5]

glediste_vrabac = [0, 0, 0]
glediste_sokol = [0, 0, 0]
glediste_mis = [0, 0, 0]


screech_limit = 5   # Koliko puta sokol može zakreštati kako bi povećao svoju brzinu

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

normala =[]
tablicaNormale = np.array([
    [-1, 3, -3, 1],
    [2, -4, 2, 0]
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
            pNorm = [0, 0, 0]
            TT = np.array([[pow(t, 3), pow(t, 2), t, 1]])
            TTTan = np.array([[pow(t, 2), t, 1]])
            TTNorm = np.array([[2*t, 1]])
            # Za svaku os
            for koordinata in range(0, 3):
                BB = (1/6)*tablica
                BBTan = (1/2)*tablicaTangente
                BBNorm = (1/2)*tablicaNormale
                RR = np.array([
                    [A[koordinata]],
                    [B[koordinata]],
                    [C[koordinata]],
                    [D[koordinata]]
                ])
                p[koordinata] = (np.matmul(np.matmul(TT, BB), RR))[0][0]
                pTan[koordinata] = (np.matmul(np.matmul(TTTan, BBTan), RR))[0][0]
                pNorm[koordinata] = (np.matmul(np.matmul(TTNorm, BBNorm), RR))[0][0]
            put.append(p)
            tangenta.append(pTan)
            normala.append(pNorm)
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
    glPointSize(10)
    glBegin(GL_POINTS)
    glColor3ub(bojaR, bojaG, bojaB)
    cntt = 0
    svakih_koliko_counter = -1
    for p in put:
        svakih_koliko_counter += 1
        if svakih_koliko_counter % 15 == 0:
            glVertex3f(p[0], p[1], p[2])
        cntt += 1
        if cnt == cntt:
            bojaB -= 30
            bojaG += 30
            bojaR += 30
            glColor3ub(bojaR, bojaG, bojaB)
            cntt = 0
    glEnd()
    glPointSize(1)

    # Zadane tocke koje definiraju krivulju
    glBegin(GL_POINTS)
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
    return


def updatePerspective():
    global trigger, perspektiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(sirinaProzora/visinaProzora), 0.1, 800.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if trigger != 'sokol':
        gluLookAt(ociste[0], ociste[1], ociste[2], glediste[0], glediste[1], glediste[2], up_vektor[0], up_vektor[1], up_vektor[2])
    if trigger == 'sokol':
        gluLookAt(ociste[0], ociste[1], ociste[2], glediste_mis[0], glediste_mis[1], glediste_mis[2], up_vektor[0], up_vektor[1], up_vektor[2])


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


# Vraća razliku vektora
def razlikaVektora(start, cilj):
    return [cilj[0]-start[0], cilj[1]-start[1], cilj[2]-start[2]]


# Vraća zbroj vektora
def zbrojVektora(a, b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]


# Vraća, za konstantu, skalirani vektor
def skaliranjeVektora(v, k):
    return [v[0]*k, v[1]*k, v[2]*k]


# Vraća normalizirani proslijeđeni vektor
def normaliziraj(v):
    n = normaVektora(v)
    return [v[0]/n, v[1]/n, v[2]/n]


# Funkcija koja pomoću aproksimacije puta i zadane udaljenosti vraća vektor pogleda
def aproksimacijaPuta(cnt, udaljenost):
    global polozaj_vrabac, tangenta, put
    tocke = [put[cnt]]
    provjera = 0
    for i in range(int(cnt)+1, len(put)):
        provjera += normaVektora(razlikaVektora(put[i], put[i-1]))
    if provjera <= udaljenost:
        return put[-1]
    local_cnt = cnt + 1
    kumulativna_udaljenost = 0
    while kumulativna_udaljenost < udaljenost:
        tocke.append(put[local_cnt])
        kumulativna_udaljenost += normaVektora(razlikaVektora(put[local_cnt], put[local_cnt-1]))
        local_cnt += 1
    posljednja_udaljenost = normaVektora(razlikaVektora(tocke[-1], tocke[-2]))
    sve_do_zadnje = kumulativna_udaljenost - posljednja_udaljenost
    ostatak = udaljenost - sve_do_zadnje

    omjer = ostatak / posljednja_udaljenost
    posljednji_skraceni_vektor = skaliranjeVektora(razlikaVektora(tocke[-1], tocke[-2]), omjer)
    return zbrojVektora(zbrojVektora(polozaj_vrabac, razlikaVektora(polozaj_vrabac, tocke[-2])), posljednji_skraceni_vektor)


# Funkcija koji vrti animaciju, pokrece se pritiskom na 'p'
def animacija():
    global vrijeme, cestice, broj_cestica
    global perspektiva, up_vektor
    global polozaj_vrabac, polozaj_sokol, glediste_vrabac, glediste_sokol, brzina_sokol, trenutni_smjer_sokola
    global ociste, glediste, put
    global vrijeme, cestice, broj_cestica
    global kugla_vrabac_radijus, kugla_sokol_radijus
    global s, loopcnt, k, polozaj_vrabac, polozaj_sokol, put
    global glediste_mis
    global razina_tla
    global screech_limit

    cnt = loopcnt

    # Vrijednost tangente u trenutnoj točki
    e = tangenta[cnt]

    ukloni_prestare_cestice()  # Uklanjanje kiše koja je pala na tlo
    generiraj_cestice()  # Generiranje novih kapljica
    translatiraj_cestice()  # Pomicanje čestica s obzirom na njihovu brzinu

    polozaj_vrabac = put[cnt]
    #glediste_vrabac = [polozaj_vrabac[0] + e[0], polozaj_vrabac[1] + e[1], polozaj_vrabac[2] + e[2]]
    glediste_vrabac = aproksimacijaPuta(cnt, 3)

    # Kretanje sokola
    if trigger == 'bot':
        vektor_spojnica = razlikaVektora(polozaj_sokol, polozaj_vrabac)
        polozaj_sokol = zbrojVektora(polozaj_sokol, skaliranjeVektora(normaliziraj(vektor_spojnica), brzina_sokol))
        # Ovisnost brzine o promjeni smjera kretanja
        brzina_sokol += -vektor_spojnica[1]/2000
        brzina_sokol += -abs(vektor_spojnica[0] + vektor_spojnica[1])/4000
        brzina_sokol = min(1, max(-0.2, brzina_sokol))

    if trigger == 'sokol':
        polozaj_sokol = zbrojVektora(polozaj_sokol, skaliranjeVektora(normaliziraj(trenutni_smjer_sokola), brzina_sokol))

    # Odabir perspektive
    if perspektiva == 'vrabac':
        ociste = polozaj_vrabac
        glediste = glediste_vrabac
        up_vektor = [0, 1, 0]
    else:
        ociste = polozaj_sokol
        glediste = polozaj_vrabac
        up_vektor = [0, 1, 0]

    # Vremenska rezolucija
    time.sleep(0.001)


    # Uvođenje nedeterminizma u brzinu sokola kao što je vjetar
    brzina_sokol += numpy.random.normal(0, 1)/200

    # Kreštanje bot sokola
    if trigger == 'bot' and cnt % 1000 == 0 and screech_limit > 0:
        winsound.PlaySound("Falcon.wav", winsound.SND_ASYNC | winsound.SND_ALIAS)
        brzina_sokol += 0.05
        screech_limit -= 1

    # Izračun osi i kuta rotacije vrapca po svojoj putanji
    os = [s[1]*e[2] - e[1]*s[2], -(s[0]*e[2] - e[0]*s[2]), s[0]*e[1] - s[1]*e[0]]
    kosinus = (s[0]*e[0] + s[1]*e[1] + s[2]*e[2])/(np.linalg.norm(s) * np.linalg.norm(e))
    stupnjevi = (math.acos(kosinus) * 180) / math.pi  # Preračun u stupnjeve


    # Brisanje platna i iscrtavanje putanje
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Iscrtavanje teksturiranih poligona
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glColor4f(1, 1, 1, 1)

    glTexCoord2f(1, 0)  # donji desni
    glVertex3f(500, razina_tla, 500)

    glTexCoord2f(0, 0)  # donji lijevi
    glVertex3f(500, razina_tla, -100)

    glTexCoord2f(0, 1)  # gornji lijevi
    glVertex3f(-100, razina_tla, -100)

    glTexCoord2f(1, 1)  # gornji desni
    glVertex3f(-100, razina_tla, 500)

    glEnd()
    glDisable(GL_TEXTURE_2D)

    # Iscrtavanje kiše
    for cestica in cestice:
        iscrtaj_cesticu(cestica)
        vrijeme += 1

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

    gotovo = False
    # Provjera kolizije sokola i vrabca
    if normaVektora(razlikaVektora(polozaj_vrabac, polozaj_sokol)) <= max(kugla_vrabac_radijus, kugla_sokol_radijus):
        print("Kolizija vrabca i sokola")
        gotovo = True
        razlika = skaliranjeVektora(normaliziraj(razlikaVektora(polozaj_sokol, polozaj_vrabac)), kugla_sokol_radijus-kugla_vrabac_radijus)
        tocka = zbrojVektora(razlika, polozaj_sokol)
        glColor4f(1, 1, 0, 0.8)
        glPointSize(50)
        glBegin(GL_POINTS)
        glVertex3f(tocka[0], tocka[1], tocka[2])
        glEnd()
    # Kraj petlje
    loopcnt += 1
    updatePerspective()
    glutSwapBuffers()
    if gotovo:
        time.sleep(5)


# Vrača vektorski produkt
def vektorskiProdukt(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


# Funkcija koja obuhvaca kontrolu tipkovnicom za pomicanje ocista
def myKeyboard(theKey, mouseX, mouseY):
    global brzina_sokol, polozaj_sokol, trenutni_smjer_sokola, polozaj_vrabac
    global up_vektor, trenutni_smjer_sokola
    global screech_limit

    theKey = str(theKey).strip('')[-2]
    pomak = 0.1
    if theKey == 'a':
        trenutni_smjer_sokola[0] = trenutni_smjer_sokola[0]  - pomak
    elif theKey == 'q':
        trenutni_smjer_sokola[0] = trenutni_smjer_sokola[0]  + pomak
    elif theKey == 's':
        trenutni_smjer_sokola[1] = trenutni_smjer_sokola[1]  - pomak
    elif theKey == 'w':
        trenutni_smjer_sokola[1] = trenutni_smjer_sokola[1]  + pomak
    elif theKey == 'd':
        trenutni_smjer_sokola[2] = trenutni_smjer_sokola[2]  - pomak
    elif theKey == 'e':
        trenutni_smjer_sokola[2] = trenutni_smjer_sokola[2]  + pomak

    elif theKey == 'g':
        smjer = razlikaVektora(polozaj_sokol, polozaj_vrabac)
        x = normaliziraj(vektorskiProdukt(normaliziraj(smjer), normaliziraj(up_vektor)))
        trenutni_smjer_sokola = zbrojVektora(trenutni_smjer_sokola, x)
        #polozaj_sokol = zbrojVektora(polozaj_sokol, x)
    elif theKey == 'j':
        smjer = razlikaVektora(polozaj_sokol, polozaj_vrabac)
        x = normaliziraj(vektorskiProdukt(normaliziraj(smjer), normaliziraj(up_vektor)))
        #polozaj_sokol = zbrojVektora(polozaj_sokol, skaliranjeVektora(x, -1))
        trenutni_smjer_sokola = zbrojVektora(trenutni_smjer_sokola, skaliranjeVektora(x, -1))
    elif theKey == 't':
        #polozaj_sokol = zbrojVektora(polozaj_sokol, normaliziraj(up_vektor))
        trenutni_smjer_sokola = zbrojVektora(trenutni_smjer_sokola, normaliziraj(up_vektor))
    elif theKey == 'u':
        polozaj_sokol = zbrojVektora(polozaj_sokol, normaliziraj(skaliranjeVektora(up_vektor, -1)))
        #trenutni_smjer_sokola = zbrojVektora(trenutni_smjer_sokola, normaliziraj(skaliranjeVektora(up_vektor, -1)))
    elif theKey == 'z':
        smjer = razlikaVektora(polozaj_sokol, polozaj_vrabac)
        polozaj_sokol = zbrojVektora(polozaj_sokol, normaliziraj(smjer))
    elif theKey == 'h':
        smjer = razlikaVektora(polozaj_sokol, polozaj_vrabac)
        polozaj_sokol = zbrojVektora(polozaj_sokol, normaliziraj(skaliranjeVektora(smjer, -1)))



    elif theKey == 'o':
        brzina_sokol = brzina_sokol -0.1
    elif theKey == 'p':
        brzina_sokol = brzina_sokol +0.1

    elif theKey == 'y':
        if screech_limit > 0:
            winsound.PlaySound("Falcon.wav", winsound.SND_ASYNC | winsound.SND_ALIAS)
            brzina_sokol += 0.05
            screech_limit -= 1
    elif theKey == 'r':
        trenutni_smjer_sokola = razlikaVektora(polozaj_sokol, polozaj_vrabac)

    updatePerspective()
    glutPostRedisplay()


# Kontroliranje gledišta mišem, koristi se samo u modu "sokol"
dugi_x = -1
dugi_y = -1
def myMouse(x, y):
    global dugi_x, dugi_y, glediste_mis, up_vektor, trenutni_smjer_sokola, brzina_sokol
    if dugi_x == -1 and dugi_y == -1:
        dugi_x = x
        dugi_y = y
        return
    zz = vektorskiProdukt(glediste_mis, up_vektor)
    dx = x-dugi_x
    dy = y-dugi_y
    dugi_x = x
    dugi_y = y

    # Ovisnost brzine o promjeni smjera kretanja
    brzina_sokol += min(0.01, max(-0.01, dy/50))
    brzina_sokol -= abs(min(dx/2000, 0.002))
    brzina_sokol = min(1, max(-0.5, brzina_sokol))


    glediste_mis = zbrojVektora(glediste_mis, skaliranjeVektora(zz, dx/100))
    glediste_mis = zbrojVektora(glediste_mis, skaliranjeVektora(up_vektor, -dy/10))
    trenutni_smjer_sokola = normaliziraj(glediste_mis)
    return


# Učitavanje teksture
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

##################    MAIN     #######################

# Izvodenje glavnog dijela programa
ucitajObjekt("bird.obj")
ucitajTockeKrivulje("krivulja.txt")
izracunajPutanju()


with open('config.txt') as f:
    dat = f.read().splitlines()
trigger = dat[0].split(' = ')[1].strip()
perspektiva = dat[1].split(' = ')[1].strip()

print("Trigger =", trigger)
print("perspektiva =", perspektiva)

vrijeme = 0

# Kreiranje prozora
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
glutInitWindowSize(sirinaProzora, visinaProzora)
glutInitWindowPosition(100, 100)
glutInit()
window = glutCreateWindow("Sokol i vrabac")

# Transparentnost
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Zadavanje funkcija
glutReshapeFunc(myReshape)
glutDisplayFunc(myDisplay)
if trigger == 'sokol':
    glutKeyboardFunc(myKeyboard)
    glutPassiveMotionFunc(myMouse)
if trigger == 'bot':
    glutKeyboardFunc(myKeyboard)
glutIdleFunc(animacija)
ucitaj_teksturu("landscape5.jpg")

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

# Početni položaj sokola i vrabca
polozaj_vrabac = put[0]
#polozaj_sokol = [polozaj_vrabac[0]-20, polozaj_vrabac[1]+5, polozaj_vrabac[2]-20]
polozaj_sokol = [polozaj_vrabac[0]-abs(np.random.uniform(0, 1))*50, polozaj_vrabac[1]+abs(np.random.uniform(0, 1))*15, polozaj_vrabac[2]-abs(np.random.uniform(0, 1))*50]
glediste_mis = razlikaVektora(polozaj_sokol, polozaj_vrabac)
# Početna orijentacija
s = [0, 0, 1]
loopcnt = 0
k = 1   # Koeficijent duljine tangente


glutMainLoop()
