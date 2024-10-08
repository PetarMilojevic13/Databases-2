from datetime import datetime,timezone
import time
import re
from bitarray import bitarray
recnik_Dtabela=dict()
pomeraji = []
def napravi_niz_validnih_redova_indeksa(indeks,vrednosti,operatori,brojac):
    if (vrednosti==[] and operatori==[]):
        return []
    else:
        resenje = None
        for index in range(len(vrednosti)):
            torka = vrednosti[index]

            if(resenje==None):
                if(int(torka[1]) in indeks[torka[0]]):
                    resenje=indeks[torka[0]][int(torka[1])]
            else:
                op = operatori[index-1]
                if (op=="and" and (int(torka[1]) in indeks[torka[0]])):
                    resenje=(resenje & (indeks[torka[0]][int(torka[1])]))
                elif(op=="or" and (int(torka[1]) in indeks[torka[0]])):
                    resenje=(resenje | (indeks[torka[0]][int(torka[1])]))

        niz_res = []
        if(resenje!=None):
            for index in range(brojac-1):
                if(resenje[index]==1):
                    niz_res.append(index+2)
        return niz_res


def proveri_validnost_reda(kolone_FactTable,vrednosti,operatori):
    if (vrednosti==[] and operatori==[]):
        return True
    else:
        resenje = None
        for index in range(len(vrednosti)):
            torka = vrednosti[index]
            iskaz = None
            if (kolone_FactTable[torka[0]]==int(torka[1])):
                iskaz=True
            else:
                iskaz=False
            if(resenje==None):
                resenje=iskaz
            else:
                op = operatori[index-1]
                if (op=="and"):
                    resenje=(resenje and iskaz)
                elif(op=="or"):
                    resenje=(resenje or iskaz)
        return resenje

def racunanje_bez_indeksa():
    #pocetno_vreme = datetime.now(timezone.utc)
    #pocetno_vreme = pocetno_vreme.timestamp()



    print("RACUNANJE BEZ INDEKSA")

    print("Unesite izraz za pretragu (Dx=X and(or) Dy=Y ....)")
    where_izraz = input()
    pattern_vrednosti = r'(D\d+)=(\d+)'
    pattern_operatori = r'\b(and|or)\b'
    vrednosti = re.findall(pattern_vrednosti, where_izraz)
    operatori = re.findall(pattern_operatori, where_izraz)


    #Vadjenje vrednosti iz Dtabela
    #Smatramo da su Dtabele male te da mozemo da ih cele drzimo u memoriji

    parsirane_vrednosti_Dtabela = [(kljuc, int(vrednost)) for kljuc, vrednost in vrednosti]

    for p in parsirane_vrednosti_Dtabela:
        Dtabela = p[0]
        recnik_Dtabela[Dtabela] = dict()
        ime_fajla=Dtabela+".txt"
        print(ime_fajla)

        brojac=0

        with open(ime_fajla, 'r') as file:
            for line in file:
                vrednosti_polja = line.strip().split(",")
                if brojac==0:
                    brojac+=1
                    for vp in vrednosti_polja:
                        recnik_Dtabela[Dtabela][vp]=[]
                else:
                    unutrasnji_brojac=0
                    for key in recnik_Dtabela[Dtabela].keys():
                        recnik_Dtabela[Dtabela][key].append(int(vrednosti_polja[unutrasnji_brojac]))
                        unutrasnji_brojac+=1

    print(recnik_Dtabela)

    print("Unesite ime FactTable fajla:")
    fact_tabela = input()

    print("Unesite agregatni iskaz koji zelite da izracunate:")
    agregatni_iskaz = input()

    #Izvlacenje agregatne funkcije i kolone po kojoj se radi ta agregatna funkcija
    agregatna_funkcija = re.findall(r'\b(avg|sum|count|max|min)\b', agregatni_iskaz)
    agregatna_funkcija=agregatna_funkcija[0]

    agregatna_kolona = re.findall(r'\((\w+)\)', agregatni_iskaz)
    agregatna_kolona=agregatna_kolona[0]


    count = None
    sum = None
    min = None
    max = None


    pocetno_vreme = time.perf_counter_ns()

    print("Zapoceto racunanje vremena u ",pocetno_vreme)

    kolone_FactTable = dict()

    #Prolazenje kroz FactTable kada nema indeksa
    brojac=0
    with open(fact_tabela, 'r') as file:
        for line in file:
            vrednosti_polja = line.strip().split(",")
            if brojac == 0:
                brojac += 1
                for vp in vrednosti_polja:
                    kolone_FactTable[vp] = None
            else:
                unutrasnji_brojac = 0
                for key in kolone_FactTable.keys():
                    if(vrednosti_polja[unutrasnji_brojac]!="NULL"):
                        kolone_FactTable[key]=int(vrednosti_polja[unutrasnji_brojac])
                    else:
                        kolone_FactTable[key] = vrednosti_polja[unutrasnji_brojac]
                    unutrasnji_brojac += 1

                validno = proveri_validnost_reda(kolone_FactTable,vrednosti,operatori)

                if (validno):
                    kolona_vrednost = kolone_FactTable[agregatna_kolona]
                    if(kolona_vrednost!="NULL"):
                        if(min==None or kolona_vrednost<min):
                            min=kolona_vrednost
                        if(max==None or kolona_vrednost>max):
                            max=kolona_vrednost

                        if (count==None):
                            count=1
                        else:
                            count+=1
                        if (sum == None):
                            sum=kolona_vrednost
                        else:
                            sum+=kolona_vrednost

    if(agregatna_funkcija=="avg"):
        if (sum==None or count==None):
            res="NULL"
        else:
            sum=sum*1.0
            count=count*1.0
            res = float(sum/count)
        print("Konacno resenje  za ",agregatni_iskaz," je jednako ",res)

    if(agregatna_funkcija=="sum"):
        if (sum==None or count==None):
            res="NULL"
        else:
            res=sum
        print("Konacno resenje  za ",agregatni_iskaz," je jednako ",res)

    if(agregatna_funkcija=="count"):
        if (sum==None or count==None):
            res=0
        else:
            res=count
        print("Konacno resenje  za ",agregatni_iskaz," je jednako ",res)

    if(agregatna_funkcija=="min"):
        if (sum==None or count==None):
            res="NULL"
        else:
            res=min
        print("Konacno resenje  za ",agregatni_iskaz," je jednako ",res)

    if(agregatna_funkcija=="max"):
        if (sum==None or count==None):
            res="NULL"
        else:
            res=max
        print("Konacno resenje  za ",agregatni_iskaz," je jednako ",res)

    zavrsno_vreme = time.perf_counter_ns()

    print("Zavrseno racunanje vremena u ", zavrsno_vreme)
    print("Ukupno trajanje BEZ INDEKSA:",zavrsno_vreme-pocetno_vreme)

    print("Ispis redova u Dtabela koji su odgovarajuci za dati iskaz")

    if(vrednosti!=[]):
        skup = []
        for torka in vrednosti:
            if (torka[0] not in skup):
                skup.append(torka[0])
        for DT in skup:
            print("Tabela ",DT)
            tabela = recnik_Dtabela[DT]
            ispis = ""
            duzina = len(tabela[DT])
            for t in tabela.keys():
                if (ispis!=""):
                    ispis+=","
                ispis+=t
            print(ispis)
            for index in range(duzina):
                ispis=""
                for t in tabela.keys():
                    if (ispis != ""):
                        ispis += ","
                    ispis += str(tabela[t][index])
                print(ispis)




def racunanje_indeks():
    #pocetno_vreme = datetime.now(timezone.utc)
    #pocetno_vreme = pocetno_vreme.timestamp()
    print("RACUNANJE SA INDEKSOM")

    print("Unesite izraz za pretragu (Dx=X and(or) Dy=Y ....)")
    where_izraz = input()

    pattern_vrednosti = r'(D\d+)=(\d+)'
    pattern_operatori = r'\b(and|or)\b'
    vrednosti = re.findall(pattern_vrednosti, where_izraz)
    operatori = re.findall(pattern_operatori, where_izraz)
    #Vadjenje vrednosti iz Dtabela
    #Smatramo da su Dtabele male te da mozemo da ih cele drzimo u memoriji

    parsirane_vrednosti_Dtabela = [(kljuc, int(vrednost)) for kljuc, vrednost in vrednosti]

    for p in parsirane_vrednosti_Dtabela:
        Dtabela = p[0]
        recnik_Dtabela[Dtabela] = dict()
        ime_fajla=Dtabela+".txt"
        print(ime_fajla)

        brojac=0

        with open(ime_fajla, 'r') as file:
            for line in file:
                vrednosti_polja = line.strip().split(",")
                if brojac==0:
                    brojac+=1
                    for vp in vrednosti_polja:
                        recnik_Dtabela[Dtabela][vp]=[]
                else:
                    unutrasnji_brojac=0
                    for key in recnik_Dtabela[Dtabela].keys():
                        recnik_Dtabela[Dtabela][key].append(int(vrednosti_polja[unutrasnji_brojac]))
                        unutrasnji_brojac+=1

    print(recnik_Dtabela)

    print("Unesite ime FactTable fajla:")
    fact_tabela = input()

    print("Unesite agregatni iskaz koji zelite da izracunate:")
    agregatni_iskaz = input()

    #Izvlacenje agregatne funkcije i kolone po kojoj se radi ta agregatna funkcija
    agregatna_funkcija = re.findall(r'\b(avg|sum|count|max|min)\b', agregatni_iskaz)
    agregatna_funkcija=agregatna_funkcija[0]

    agregatna_kolona = re.findall(r'\((\w+)\)', agregatni_iskaz)
    agregatna_kolona=agregatna_kolona[0]


    count = None
    sum = None
    min = None
    max = None

    kolone_FactTable = dict()
    indeksi=dict()
    for k in vrednosti:
        d = k[0]
        indeksi[d]=dict()

    #Pravljenje indeksa

    indeksi_ispravnik=[]
    pomeraji=[]
    brojac=0
    with open(fact_tabela, 'r') as file:
        while(True):
            if (brojac>0):
                pomeraj = file.tell()
                pomeraji.append(pomeraj)
            line = file.readline()
            if not line:
                #Kraj
                break
            vrednosti_polja = line.strip().split(",")
            if brojac == 0:
                brojac += 1
                for vp in vrednosti_polja:
                    kolone_FactTable[vp] = None
            else:
                brojac += 1
                unutrasnji_brojac = 0
                for key in kolone_FactTable.keys():
                    if(vrednosti_polja[unutrasnji_brojac]!="NULL"):
                        kolone_FactTable[key]=int(vrednosti_polja[unutrasnji_brojac])
                    else:
                        kolone_FactTable[key] = vrednosti_polja[unutrasnji_brojac]
                    unutrasnji_brojac += 1

                for k in indeksi:
                    vr = kolone_FactTable[k]
                    if(vr in indeksi[k]):
                        indeksi[k][vr][brojac-2]=1
                    else:
                        indeksi[k][vr]=bitarray(10000)
                        indeksi[k][vr].setall(0)
                        indeksi[k][vr][brojac-2]=1

    pocetno_vreme = time.perf_counter_ns()

    print("Zapoceto racunanje vremena u ",pocetno_vreme)

    indeksi_ispravnik=[]
    if(vrednosti==[]):
        for index in range(brojac-1):
            indeksi_ispravnik.append(index+2)
    else:
        indeksi_ispravnik = napravi_niz_validnih_redova_indeksa(indeksi,vrednosti,operatori,brojac)

    with open(fact_tabela, 'r',encoding='utf-8') as file:
        for trenutna_linija in indeksi_ispravnik:

                    pomeraj = pomeraji[trenutna_linija-2]
                    file.seek(pomeraj)
                    line = file.readline()
                    # for line in file:
                    vrednosti_polja = line.strip().split(",")
                    if brojac == 0:
                        brojac += 1
                        for vp in vrednosti_polja:
                            kolone_FactTable[vp] = None
                    else:
                        brojac += 1
                        unutrasnji_brojac = 0
                        for key in kolone_FactTable.keys():
                            if (vrednosti_polja[unutrasnji_brojac]!="NULL"):
                                kolone_FactTable[key] = int(vrednosti_polja[unutrasnji_brojac])
                            else:
                                kolone_FactTable[key] = vrednosti_polja[unutrasnji_brojac]
                            unutrasnji_brojac += 1

                        #validno = proveri_validnost_reda(kolone_FactTable, vrednosti, operatori)
                        validno=True
                        if (validno):
                            kolona_vrednost = kolone_FactTable[agregatna_kolona]
                            if(kolona_vrednost != "NULL"):
                                if (min == None or kolona_vrednost < min):
                                    min = kolona_vrednost
                                if (max == None or kolona_vrednost > max):
                                    max = kolona_vrednost

                                if (count == None):
                                    count = 1
                                else:
                                    count += 1
                                if (sum == None):
                                    sum = kolona_vrednost
                                else:
                                    sum += kolona_vrednost

    if (agregatna_funkcija == "avg"):
        if (sum == None or count == None):
            res = "NULL"
        else:
            sum = sum * 1.0
            count = count * 1.0
            res = float(sum / count)
        print("Konacno resenje  za ", agregatni_iskaz, " je jednako ", res)

    if (agregatna_funkcija == "sum"):
        if (sum == None or count == None):
            res = "NULL"
        else:
            res = sum
        print("Konacno resenje  za ", agregatni_iskaz, " je jednako ", res)

    if (agregatna_funkcija == "count"):
        if (sum == None or count == None):
            res = 0
        else:
            res = count
        print("Konacno resenje  za ", agregatni_iskaz, " je jednako ", res)

    if (agregatna_funkcija == "min"):
        if (sum == None or count == None):
            res = "NULL"
        else:
            res = min
        print("Konacno resenje  za ", agregatni_iskaz, " je jednako ", res)

    if (agregatna_funkcija == "max"):
        if (sum == None or count == None):
            res = "NULL"
        else:
            res = max
        print("Konacno resenje  za ", agregatni_iskaz, " je jednako ", res)

    zavrsno_vreme = time.perf_counter_ns()

    print("Zavrseno racunanje vremena u ", zavrsno_vreme)
    print("Ukupno trajanje SA INDEKSOM:", zavrsno_vreme - pocetno_vreme)

    print("Ispis redova u Dtabela koji su odgovarajuci za dati iskaz")

    if(vrednosti!=[]):
        skup = []
        for torka in vrednosti:
            if (torka[0] not in skup):
                skup.append(torka[0])
        for DT in skup:
            print("Tabela ",DT)
            tabela = recnik_Dtabela[DT]
            ispis = ""
            duzina = len(tabela[DT])
            for t in tabela.keys():
                if (ispis!=""):
                    ispis+=","
                ispis+=t
            print(ispis)
            for index in range(duzina):
                ispis=""
                for t in tabela.keys():
                    if (ispis != ""):
                        ispis += ","
                    ispis += str(tabela[t][index])
                print(ispis)





if __name__ == "__main__":

    racunanje_bez_indeksa()

    racunanje_indeks()
