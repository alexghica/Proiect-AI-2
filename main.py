"""
Dati enter dupa fiecare solutie afisata.

Presupunem ca avem costul de mutare al unui bloc egal cu indicele in alfabet, cu indicii incepănd de la 1 (care se calculează prin 1+ diferenta dintre valoarea codului ascii al literei blocului de mutat si codul ascii al literei "a" ) . Astfel A* are trebui sa prefere drumurile in care se muta intai blocurile cu infomatie mai mica lexicografic pentru a ajunge la una dintre starile scop
"""

import copy
import sys
import time


# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, timpStart, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        nr_nod = 1
        for nod in l:
            if nr_nod!= 1:
                print("\n")
            print(str(nr_nod) + ")")
            print(str(nod))
            nr_nod = nr_nod+1
        timpAcum = time.time()
        print("Durata: ",timpAcum-timpStart)
        if afisCost:
            print("Cost: ", self.g)
        if afisLung:
            print("Lungime: ", len(l))
        return len(l)


#returneaza datele de afisat pentru a le putea scrie in fisier
    def afisDrumFisier(self,timpStart, afisCost=True, afisLung=True):  # returneaza si lungimea drumului
        drum = self.obtineDrum()
        afisare = ""
        if afisCost:
            afisare += "Cost: %d\n" % self.g
        if afisLung:
            afisare += "Lungime: %d\n" % len(drum)
        timpAcum = time.time()
        afisare += "Durata: %.3f s\n" % (timpAcum - timpStart)
        for nr_nod in range(len(drum)):
            afisare += "%d)\n" % (nr_nod + 1)
            afisare += str(drum[nr_nod]) + "\n"
        afisare += "=" * 20 + "\n"
        return afisare

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    # repr afiseaza ca sa se mai poata utiliza
    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return (sir)

    # euristica banală: daca nu e stare scop, returnez 1, altfel 0

    # str afiseaza ca sa se poata citi
    def __str__(self):  # afisarea stivei ca string. ramane
        sir = ""
        maxInalt = max([len(stiva) for stiva in self.info])
        '''for inalt in range(maxInalt, 0, -1):
            for stiva in self.info:
                print(stiva)'''
        for inalt in range(maxInalt, 0, -1):
            for stiva in self.info:
                if len(stiva) < inalt:
                    sir += "    "
                else:
                    if stiva[inalt-1][0] == 'piramida':                  #afisarea in formatul cerut
                        sir += "/"+str(stiva[inalt - 1][1]) + "\ "
                    if stiva[inalt-1][0] == 'cub':
                        sir += "["+str(stiva[inalt - 1][1]) + "] "
                    if stiva[inalt-1][0] == 'sfera':
                        sir += "("+str(stiva[inalt - 1][1]) + ") "

                    #sir += str(stiva[inalt - 1][1]) + " "
            sir += "\n"
        nr_stive = len(self.info)                     #afiseaza # pana la ultima stiva nevida
        for i in range (len(self.info)-1,0,-1):
            if len(self.info[i]) == 0 :
                nr_stive = nr_stive -1
            else:
                break
        sir += "#" * (4 * nr_stive -1) #+ "\n"
        #sir += "#" * (4 * (len(self.info) - self.info.count([]))-1)    #afiseaza pur si simplu pentru cate stive sunt
        return sir


def calculc_cost(bloc):       #calculeaza costul pentru un bloc
    if bloc[0] == 'cub':
        return 2
    elif bloc[0] == 'piramida':
        return 1
    elif bloc[0] == 'sfera':
        return 3
    return 0


class Graph:  # graful problemei
    def __init__(self, nume_fisier, fisier_iesire):

        f = open(nume_fisier, 'r')
        self.fisier_iesire = open(fisier_iesire, 'w')
        k = f.readline().strip()
        j = 0
        stareInitiala = []
        self.K = k
        # print(k)
        for linie in f.readlines():
            linie = linie.strip()
            print(linie)
            if linie == "#":
                stareInitiala.append([])
                j += 1
            else:
                elemente = linie.strip().split(",")
                linie = []
                for el in elemente:
                    a = el.split("(")
                    forma = a[0]
                    info = a[1].replace(")", "")
                    print(info, forma)
                    linie.append((forma, info))
                stareInitiala.append(linie)
                j += 1
        nrFinalStive = j - int(k)
        self.nrFinalStive = nrFinalStive
        self.start = stareInitiala
        print("Stare Initiala:", self.start)
        print('\n')

        input()

    def testeaza_scop(self, nodCurent):           #pentru nod
        if len(nodCurent.info) - nodCurent.info.count([]) != self.nrFinalStive:
            return False
        return True

    def testeaza_scop_info(self, infoNodCurent):  #daca se da doar informatia din nod
        if len(infoNodCurent) - infoNodCurent.count([]) != self.nrFinalStive:
            return False
        return True

    # def testeaza_scop(self, nodCurent):
    #	return nodCurent.info in self.scopuri;

    # va genera succesorii sub forma de noduri in arborele de parcurgere

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica_banala"):
        listaSuccesori = []
        stive_c = nodCurent.info  # stivele din nodul curent
        nr_stive = len(stive_c)
        for idx in range(nr_stive):
            copie_interm = copy.deepcopy(stive_c)
            if len(copie_interm[idx]) == 0:
                continue
            bloc = copie_interm[idx].pop()
            for j in range(nr_stive):
                if idx == j:
                    continue
                stive_n = copy.deepcopy(copie_interm)  # lista noua de stive
                # aici conditia
                '''if len(stive_n[j]) == 0:
                    continue'''
                nivel = len(stive_n[j])
                if len(stive_n[j]) > 0 and stive_n[j][-1][0] == 'piramida':  #nu se poate aseza pe piramida
                    continue
                if bloc[0] == 'sfera':                                    #pentru sfera:
                    '''if stive_n[j] == stive_n[0] or stive_n[j] == stive_n[-1]:
                        continue'''
                    if j == 0 or j == len(stive_n) - 1:     # nu poate sa fie pe prima sau pe ultima stiva
                        continue
                    if len(stive_n[j - 1]) < nivel + 1 or len(stive_n[j + 1]) < nivel + 1:  #trebuie sa existe un bloc in stanga si in dreapta
                        continue                                                            #la acelasi nivel
                    if stive_n[j - 1][nivel][0] == 'piramida' or stive_n[j + 1][nivel][0] == 'piramida': #in dreapta si in stanga nu pot fi piramide
                        continue
                stive_n[j].append(bloc)
                costMutareBloc= calculc_cost(bloc)            #calculam costul mutarii
                #print(nodCurent.g + costMutareBloc)
                nod_nou=NodParcurgere(stive_n,nodCurent, cost=nodCurent.g+costMutareBloc,h= self.calculeaza_h_buna(stive_n, tip_euristica))
                # nod_nou = NodParcurgere(stive_n,nodCurent,nodCurent.g+costMutareBloc,h=0)
                #nod_nou = NodParcurgere(stive_n, nodCurent, 0, 0)
                if not nodCurent.contineInDrum(stive_n):
                    listaSuccesori.append(nod_nou)

        return listaSuccesori

    #			if linie[element][0] == 'sfera': # am rezolvat sfera
    #				if linie[element] == linie[-1] or linie[element] == linie[0] or bool(linie[element-1]) == False or bool(linie[element+1]):

    # euristica banala
    '''
    def calculeaza_h(self, infoNod, tip_euristica="euristica_banala"):
        if tip_euristica == "euristica_banala":
            if self.testeaza_scop(infoNod) == False:
                return 1
            return 0
        else:
            # calculez cate blocuri nu sunt la locul fata de fiecare dintre starile scop, si apoi iau minimul dintre aceste valori
            euristici = []
            for (iScop, scop) in enumerate(self.scopuri):
                h = 0
                for iStiva, stiva in enumerate(infoNod):
                    for iElem, elem in enumerate(stiva):
                        try:
                            # exista în stiva scop indicele iElem dar pe acea pozitie nu se afla blocul din infoNod
                            if elem != scop[iStiva][iElem]:
                                h += 1
                        except IndexError:
                            # nici macar nu exista pozitia iElem in stiva cu indicele iStiva din scop
                            h += 1
                euristici.append(h)
            return min(euristici)
    '''

    # euristica banala
    # calculez cate blocuri nu sunt la locul fata de fiecare dintre starile scop, si apoi iau minimul dintre aceste valori
    def calculeaza_h_buna(self, infoNod, tip_euristica="euristica_banala"):
        if tip_euristica == "euristica_banala":
            if self.testeaza_scop_info(infoNod) == False:
                return 1
            return 0
        elif tip_euristica == "euristica1":               #calculam cate blocuri trebuie mutate
            #print("Euristica 1")
            if self.testeaza_scop_info(infoNod) == False:
                lungimi = []
                for stiva in infoNod:
                    lungimi.append(len(stiva))
                lungimi.sort()
                #print(lungimi[0] + lungimi[1])
                return (lungimi[0] + lungimi[1])
            else:
                return 0
        elif tip_euristica == "euristica2":               #calculam costul blocurilor de mutat
            #print("Euristica 2")
            if self.testeaza_scop_info(infoNod) == False:
                costuri = []
                for stiva in infoNod:
                    cost = 0
                    for elem in stiva:
                        cost += calculc_cost(elem)
                    costuri.append(cost)
                costuri.sort()
                #print(costuri[0] + costuri[1])
                return (costuri[0] + costuri[1])
            else:
                return 0
        elif tip_euristica == "euristica3":
            #print("Euristica 3")
            if self.testeaza_scop_info(infoNod) == False:
                costuri = []
                for stiva in infoNod:
                    costuri.append(len(stiva)*3)
                costuri.sort()
                #print(costuri[0] + costuri[1])
                return ((costuri[0] + costuri[1])*5)
            else:
                return 0




    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)


# aici nu cred ca umblu. trebuie sa vad testeaza scop si
# eventual genereaza succesori


#BREADTH FIRST

def breadth_first(gr, nrSolutiiCautate, durataTimeOut):   #bun- timeout, afisare in fisier
    timpStart = time.time()
    j=0
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None)]
    #print('aici')
    #print(c)

    while len(c) > 0:
        timpActual = time.time()
        if timpActual - timpStart > durataTimeOut:
            print("Timpul a expirat!")
            return
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            print("Solutie:")
            nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
            gr.fisier_iesire.write("Solutie: \n")
            gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=False, afisLung=False)))
            print("===================\n")
            # aici scriu
            input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        j += 1
        c.extend(lSuccesori)


'''if(nrSolutiiCautate == 1):
        while len(c) > 0:
            timpSfarsit = time.time()
            if timpSfarsit - timpStart > durataTimeOut:
                print("Timeout!")
                return
            nodCurent = c.pop(0)

            if gr.testeaza_scop(nodCurent):
                print("Solutie:")
                nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
                gr.fisier_iesire.write("Solutie: \n")
                gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=True, afisLung=True)))
                print("===================\n")
                input()
                nrSolutiiCautate -= 1
                if nrSolutiiCautate == 0:
                    return
            lSuccesori = gr.genereazaSuccesori(nodCurent)
            j += 1
            for i in lSuccesori:
                if gr.testeaza_scop(i):
                    print("Solutie:")
                    i.afisDrum(timpStart, afisCost=True, afisLung=True)
                    gr.fisier_iesire.write("Solutie: \n")
                    gr.fisier_iesire.write(str(i.afisDrumFisier(timpStart, afisCost=True, afisLung=True)))
                    print("===================\n")
                    return
            c.extend(lSuccesori)'''



def breadth_first1(gr, nrSolutiiCautate, durataTimeOut):   #bun- timeout, afisare in fisier
    timpStart = time.time()
    j=0
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None)]
    #print('aici')
    #print(c)
    if (nrSolutiiCautate == 1):
        while len(c) > 0:
            timpSfarsit = time.time()
            if timpSfarsit - timpStart > durataTimeOut:
                print("Timeout!")
                return
            nodCurent = c.pop(0)

            if gr.testeaza_scop(nodCurent):
                print("Solutie:")
                nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
                gr.fisier_iesire.write("Solutie: \n")
                gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=True, afisLung=True)))
                print("===================\n")
                input()
                nrSolutiiCautate -= 1
                if nrSolutiiCautate == 0:
                    return
            lSuccesori = gr.genereazaSuccesori(nodCurent)
            j += 1
            for i in lSuccesori:
                if gr.testeaza_scop(i):
                    print("Solutie:")
                    i.afisDrum(timpStart, afisCost=True, afisLung=True)
                    gr.fisier_iesire.write("Solutie: \n")
                    gr.fisier_iesire.write(str(i.afisDrumFisier(timpStart, afisCost=True, afisLung=True)))
                    print("===================\n")
                    return
            c.extend(lSuccesori)

    while len(c) > 0:
        timpActual = time.time()
        if timpActual - timpStart > durataTimeOut:
            print("Timpul a expirat!")
            return
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            print("Solutie:")
            nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
            gr.fisier_iesire.write("Solutie: \n")
            gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=False, afisLung=False)))
            print("===================\n")
            # aici scriu
            input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        j += 1
        c.extend(lSuccesori)



#A_STAR

def a_star(gr, nrSolutiiCautate, durataTimeOut, tip_euristica):  #e bun cps timeout + scriere in fisier
    timpStart = time.time()
    print(timpStart)
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h_buna(gr.start,tip_euristica))]

    while len(c) > 0:
        timpActual = time.time()
        if timpActual - timpStart > durataTimeOut:
            print("Timpul a expirat!")
            return
        nodCurent = c.pop(0)


        if gr.testeaza_scop(nodCurent):
            print("Solutie: ")
            nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
            gr.fisier_iesire.write("Solutie: \n")
            gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=True, afisLung=True)))
            print("===================\n")
            input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        k=0
        for succesor in lSuccesori:
            for j in range(len(c)):
                if succesor.info == c[j].info:
                    if succesor.f < c[j].f:
                        c.pop(j)
                    else:
                        lSuccesori.pop(k)
            k+=1
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)




#DEPTH_FIRST

def depth_first(graph, nrSolutiiCautate, durataTimeOut):  # e ok cps
    timpStart = time.time()
    # vom simula o stiva prin relatia de parinte a nodului curent
    df(NodParcurgere(gr.start, None, 0, gr.calculeaza_h_buna(gr.start)),timpStart, nrSolutiiCautate, durataTimeOut)


def df(nodCurent, timpStart, nrSolutiiCautate, durataTimeOut):
    timpActual = time.time()
    if timpActual - timpStart > durataTimeOut:
        print("Timpul a expirat!")
        return 0
    if nrSolutiiCautate == 0:  # testul acesta s-ar valida doar daca in apelul initial avem df(start,if nrSolutiiCautate=0)
        return nrSolutiiCautate
    if gr.testeaza_scop_info(nodCurent.info):
        print("Solutie: ")
        nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
        gr.fisier_iesire.write("Solutie: \n")
        gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=False, afisLung=False)))
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    lsuccesori = gr.genereazaSuccesori(nodCurent)
    for sc in lsuccesori:
        if nrSolutiiCautate != 0:
            nrSolutiiCautate = df(sc, timpStart, nrSolutiiCautate, durataTimeOut)
    return nrSolutiiCautate


#DEPTH_FIRST ITERATIV

def depth_first_iterativ(gr, nrSolutiiCautate, durataTimeOut):
    timpStart = time.time()
    for adancime in range(1, 20):
        if nrSolutiiCautate == 0:
            return
        nrSolutiiCautate = dfi(NodParcurgere(gr.start, None, 0, gr.calculeaza_h_buna(gr.start)),
                               adancime, nrSolutiiCautate,timpStart, durataTimeOut)



def dfi(nodCurent, adancime, nrSolutiiCautate, timpStart, durataTimeOut):  # e ok cps
    timpActual = time.time()
    if timpActual - timpStart > durataTimeOut:
        print("Timpul a expirat!")
        return 0
    if adancime == 1 and gr.testeaza_scop_info(nodCurent.info):
        print("Solutie: ")
        nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
        gr.fisier_iesire.write("Solutie: \n")
        gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=False, afisLung=False)))
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    if adancime > 1:
        succesori = gr.genereazaSuccesori(nodCurent)
        for sc in succesori:
            if nrSolutiiCautate != 0:
                nrSolutiiCautate = dfi(sc, adancime - 1, nrSolutiiCautate, timpStart, durataTimeOut)
    return nrSolutiiCautate


#UCS

def uniform_cost(graph, nrSolutiiCautate, durataTimeOut):   # e ok cps
    timpStart = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h_buna(gr.start))]

    while len(c) > 0:
        timpActual = time.time()
        if timpActual - timpStart > durataTimeOut:
            print("Timpul a expirat!")
            return 0
        nodCurent = c.pop(0)


        if gr.testeaza_scop_info(nodCurent.info):
            print("Solutie: ")
            nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
            gr.fisier_iesire.write("Solutie: \n")
            gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=False, afisLung=False)))
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        succesori = gr.genereazaSuccesori(nodCurent)
        k=0
        for succesor in succesori:
            for j in range(len(c)-1):
                if succesor.info == c[j].info:
                    if succesor.g < c[j].g:
                        c.pop(j)
                    '''else:
                        succesori.pop(k)
            k+=1'''
        for sc in succesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                #ordonez dupa cost
                if c[i].g > sc.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, sc)
            else:
                c.append(sc)




#GREEDY

def greedy(gr, nrSolutiiCautate,durataTimeOut,tip_euristica):   # e ok
    timpStart = time.time()
    j=0
    print(timpStart)
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h_buna(gr.start,tip_euristica))]

    while len(c) > 0:
        timpActual = time.time()
        if timpActual - timpStart > durataTimeOut:
            print("Timpul a expirat!")
            return
        nodCurent = c.pop(0)


        if gr.testeaza_scop(nodCurent):
            print("Solutie: ")
            nodCurent.afisDrum(timpStart, afisCost=True, afisLung=True)
            gr.fisier_iesire.write("Solutie: \n")
            gr.fisier_iesire.write(str(nodCurent.afisDrumFisier(timpStart, afisCost=True, afisLung=True)))
            print("===================\n")
            input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        j +=1
        for sc in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].h >= sc.h:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, sc)
            else:
                c.append(sc)


if (len(sys.argv) != 5):
    print("Nu ati introdus numarul de parametrii necesar!")
    exit(0)

fisier_intrare = sys.argv[1]
fisier_iesire= sys.argv[2]
nrSolutiiCautate = int(sys.argv[3])
durataTimeOut = float(sys.argv[4])

gr = Graph(fisier_intrare,fisier_iesire)

#gr = Graph("input2.txt","output.txt")
'''c = [NodParcurgere(gr.start, None)]
nodCurent = c.pop()'''
#a_star(gr, nrSolutiiCautate=3, durataTimeOut=0.7, tip_euristica="euristica3")  # timpul introdus in secunde # la 1 merge la 0.7 bubuie
#print("A* euristica banala")
'''print("Depth first")
depth_first(gr, 3, 0.1) '''# pe la 0.1 bubuie
#print("Depth first iterativ")
# depth_first_iterativ(gr, 3, 1)la 0.1 bubuie jumate                #punem 1 si nu bubuie
'''print("Uniform cost")
uniform_cost(gr, 3, 3)''' # la 4 merge la 3 bubuie     #                   #punem 1 si bubuie - ambele pe input2.txt (aka inputd.txt)

#GREEDY apelare normala
'''print("Greedy:")
greedy(gr, 3,  0.6, "euristica_banala")''' # cu 0.6 merge ,  l 0.5 bubuie


#python .\main.py input2.txt output.txt 3 2  #input1
#python .\main.py inputTabel2.txt output.txt 3 10  #input2


breadth_first1(gr, nrSolutiiCautate,durataTimeOut)
#a_star(gr, nrSolutiiCautate, durataTimeOut, "euristica_banala")
#a_star(gr, nrSolutiiCautate, durataTimeOut, "euristica1")
#a_star(gr, nrSolutiiCautate, durataTimeOut, "euristica2")
#a_star(gr, nrSolutiiCautate, durataTimeOut, "euristica3")
#depth_first(gr, nrSolutiiCautate, durataTimeOut)
#depth_first_iterativ(gr, nrSolutiiCautate, durataTimeOut)
#uniform_cost(gr, nrSolutiiCautate, durataTimeOut)
#greedy(gr, nrSolutiiCautate, durataTimeOut, "euristica_banala")
#greedy(gr, nrSolutiiCautate, durataTimeOut, "euristica1")
#greedy(gr, nrSolutiiCautate, durataTimeOut, "euristica2")
#greedy(gr, nrSolutiiCautate, durataTimeOut, "euristica3")


'''marcel = [1,5,7,2,8]
marcel.sort()
print(marcel)'''
#print(sys.argv)

# gr=Graph("input.txt")

# Rezolvat cu breadth first
# print("Solutii obtinute cu breadth first:")
# breadth_first(gr, nrSolutiiCautate=3)

# print("\n\n##################\nSolutii obtinute cu A*:")
# nrSolutiiCautate=3
# a_star(gr, nrSolutiiCautate=3,tip_euristica="euristica nebanala")
