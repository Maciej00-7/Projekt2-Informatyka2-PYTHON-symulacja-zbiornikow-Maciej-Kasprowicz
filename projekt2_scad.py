import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath
class Rura:

    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):

        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255) 
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        # 1. Rysowanie obudowy rury
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # 2. Rysowanie cieczy w srodku (jesli plynie)
        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc- 4, Qt.SolidLine,Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)
class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x = x; self.y = y
        self.width = width; self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0 # Wartosc 0.0-1.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc- self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc-= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self): return self.aktualna_ilosc <= 0.1
    def czy_pelny(self): return self.aktualna_ilosc >= self.pojemnosc- 0.1
    # Punkty zaczepienia dla rur

    def punkt_gora_srodek(self): return (self.x + self.width/2, self.y)
    def punkt_dol_srodek(self): return (self.x + self.width/2, self.y + self.height)

    def draw(self, painter):
        # 1. Rysowanie cieczy
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height- h_cieczy
            wysokosc_rysowania = max(1, int(h_cieczy - 2))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width- 6), wysokosc_rysowania)
            # 2. Rysowanie obrysu
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        # 3. Podpis
        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y- 20), self.nazwa)
class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulacja Kaskady Zbiorników")
        self.setFixedSize(1100, 700)
        self.setStyleSheet("background-color: #222;")

        # Tryb zaworu (0 = Oba, 1 = Tylko Z3, 2 = Tylko Z4)
        self.tryb_zaworu = 0

        #Konfiguracja Zbiornikow
        self.z1 = Zbiornik(200, 50, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 100.0; self.z1.aktualizuj_poziom() # Pelny
        
        self.z2 = Zbiornik(530, 200, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(860, 350, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(200, 350, nazwa="Zbiornik 4")

        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        #Konfiguracja Rur
        # Rura 1: Z1 (Dol)-> Z2 (Gora)
        p1_start = self.z1.punkt_dol_srodek()
        p1_koniec = self.z2.punkt_gora_srodek()
        mid_y = (p1_start[1] + p1_koniec[1]) / 2

        self.rura1 = Rura([p1_start, (p1_start[0], mid_y), (p1_koniec[0], mid_y), p1_koniec])

        # Rura 2: Z2 (Dol)-> Z3 (prawo)
        p2_start = self.z2.punkt_dol_srodek()
        p2_koniec = self.z3.punkt_gora_srodek()
        mid_y2 = (p2_start[1] + p2_koniec[1]) / 2

        self.rura2 = Rura([p2_start, (p2_start[0], mid_y2), (p2_koniec[0], mid_y2), p2_koniec])
        # Rura 3: Z2 -> Z4 (W lewo)
        p3_start = self.z2.punkt_dol_srodek() 
        p3_koniec = self.z4.punkt_gora_srodek()
        mid_y3 = (p3_start[1] + p3_koniec[1]) / 2

        self.rura3 = Rura([p3_start,(p3_start[0], mid_y3 ), (p3_koniec[0], mid_y3),p3_koniec])

        self.rury = [self.rura1, self.rura2, self.rura3]

        #Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)
        self.running = False
        self.flow_speed = 0.8
        self.setup_interfejs()

    def setup_interfejs(self):
        # 1. Główny przycisk Start/Stop
        self.btn_start = QPushButton("Start / Stop", self)
        self.btn_start.setGeometry(50, 540, 100, 40)
        self.btn_start.setStyleSheet("background-color: #444; color: white; font-weight: bold;")
        self.btn_start.clicked.connect(self.przelacz_symulacje)

        #3. Przycisk reset
        self.btn_reset = QPushButton("Resetuj", self)
        self.btn_reset.setGeometry(50, 600, 100, 40)
        self.btn_reset.setStyleSheet("background-color: #444; color: white; font-weight: bold;")
        self.btn_reset.clicked.connect(self.resetuj_zbiornik)


        # 2. Generowanie paneli sterowania dla każdego zbiornika
        for i, zbiornik in enumerate(self.zbiorniki):
            base_x = 200 + (i * 220) 
            base_y = 540

            # Etykieta
            lbl = QLabel(zbiornik.nazwa, self)
            lbl.move(base_x, base_y - 20)
            lbl.setStyleSheet("color: #AAA;")

            # Przycisk [+] Napełnij
            btn_fill = QPushButton("[+] Napełnij", self)
            btn_fill.setGeometry(base_x, base_y, 100, 25)
            btn_fill.setStyleSheet("background-color: green; color: white;") 
            # Przekazujemy konkretny obiekt zbiornika i True (napełnij)
            btn_fill.clicked.connect(lambda checked, z=zbiornik: self.steruj_zbiornikiem(z, pelny=True))

            # Przycisk [-] Opróżnij
            btn_empty = QPushButton("[-] Opróżnij", self)
            btn_empty.setGeometry(base_x, base_y + 30, 100, 25)
            btn_empty.setStyleSheet("background-color: red; color: white;") 
            # Przekazujemy konkretny obiekt zbiornika i False (opróżnij)
            btn_empty.clicked.connect(lambda checked, z=zbiornik: self.steruj_zbiornikiem(z, pelny=False))

            # STEROWANIE ZAWOREM dla Zbiornika 2
            if i == 1:
                lbl_v = QLabel("Ustawienie zaworu:", self)
                lbl_v.move(base_x, base_y + 65)
                lbl_v.setStyleSheet("font-size: 10px; color: #BBB;")

                self.combo = QComboBox(self)
                self.combo.addItems(["Rozpływ w obie strony", "Rozpływ w Prawo", "Rozpływ w Lewo", "Zamknięty"])
                self.combo.setGeometry(base_x, base_y + 80, 140, 25)
                self.combo.setStyleSheet("background-color: #555; selection-background-color: #0088cc;")
                self.combo.currentIndexChanged.connect(self.zmiana_zaworu)
    
    def steruj_zbiornikiem(self, zbiornik, pelny):
        if pelny:
            zbiornik.aktualna_ilosc = zbiornik.pojemnosc
        else:
            zbiornik.aktualna_ilosc = 0.0
        
        zbiornik.aktualizuj_poziom()
        self.update()
    def zmiana_zaworu(self, index):
        self.tryb_zaworu = index

    def przelacz_symulacje(self):
        if self.running: self.timer.stop()
        else: self.timer.start(20)
        self.running = not self.running
    
    def resetuj_zbiornik(self):
        self.z1.aktualna_ilosc = 100.0; self.z1.aktualizuj_poziom() 
        self.z2.aktualna_ilosc = 0.0; self.z2.aktualizuj_poziom()
        self.z3.aktualna_ilosc = 0.0; self.z3.aktualizuj_poziom()
        self.z4.aktualna_ilosc = 0.0; self.z4.aktualizuj_poziom()
        self.update()

    def logika_przeplywu(self):
        # 1. Przepływ Z1 -> Z2
        plynie_1 = False
        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            plynie_1 = True
        self.rura1.ustaw_przeplyw(plynie_1)

        #Rura do Z3
        plynie_do_z3 = False
        plynie_do_z4 = False
        if self.z2.aktualna_ilosc > 0.1:
            otwarty_z3 = not self.z3.czy_pelny()
            otwarty_z4 = not self.z4.czy_pelny()

            # TRYB 0: RÓWNOMIERNIE 
            if self.tryb_zaworu == 0:
                if otwarty_z3 and otwarty_z4:
                    do_pobrania = min(self.z2.aktualna_ilosc, self.flow_speed * 2)
                    pobrana = self.z2.usun_ciecz(do_pobrania)
                    self.z3.dodaj_ciecz(pobrana / 2)
                    self.z4.dodaj_ciecz(pobrana / 2)
                    plynie_do_z3 = True; plynie_do_z4 = True
                elif otwarty_z3: 
                    pobrana = self.z2.usun_ciecz(min(self.z2.aktualna_ilosc, self.flow_speed))
                    self.z3.dodaj_ciecz(pobrana)
                    plynie_do_z3 = True
                elif otwarty_z4: 
                    pobrana = self.z2.usun_ciecz(min(self.z2.aktualna_ilosc, self.flow_speed))
                    self.z4.dodaj_ciecz(pobrana)
                    plynie_do_z4 = True

            #TRYB 1: TYLKO Z3
            elif self.tryb_zaworu == 1:
                if otwarty_z3:
                    pobrana = self.z2.usun_ciecz(min(self.z2.aktualna_ilosc, self.flow_speed))
                    self.z3.dodaj_ciecz(pobrana)
                    plynie_do_z3 = True
               

            #TRYB 2: TYLKO Z4
            elif self.tryb_zaworu == 2:
                if otwarty_z4:
                    pobrana = self.z2.usun_ciecz(min(self.z2.aktualna_ilosc, self.flow_speed))
                    self.z4.dodaj_ciecz(pobrana)
                    plynie_do_z4 = True
                    
            #TRYB 3: ZAMKNIĘTY
            elif self.tryb_zaworu == 3:
                pass
                

        self.rura2.ustaw_przeplyw(plynie_do_z3)
        self.rura3.ustaw_przeplyw(plynie_do_z4)
            
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # Najpierw rury (pod spodem), potem zbiorniki
        for r in self.rury: r.draw(p)
        for z in self.zbiorniki: z.draw(p)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec_())