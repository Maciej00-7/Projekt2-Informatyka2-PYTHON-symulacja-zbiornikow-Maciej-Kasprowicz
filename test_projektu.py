import pytest
from PyQt5.QtWidgets import QApplication
from projekt2_scad import Zbiornik, SymulacjaKaskady


def test_zbiornik_napelnianie():
    z = Zbiornik(0, 0)
    z.pojemnosc = 100.0
    
    dodano = z.dodaj_ciecz(30.0)
    assert z.aktualna_ilosc == 30.0
    assert dodano == 30.0
    assert z.poziom == 0.3

def test_zbiornik_przepelnienie():

    z = Zbiornik(0, 0)
    z.pojemnosc = 100.0
    z.aktualna_ilosc = 80.0
    
    dodano = z.dodaj_ciecz(50.0)
    
    assert z.aktualna_ilosc == 100.0
    assert dodano == 20.0
    assert z.czy_pelny() is True

def test_zbiornik_oproznianie():
    z = Zbiornik(0, 0)
    z.aktualna_ilosc = 50.0
    
    usunieto = z.usun_ciecz(20.0)
    assert z.aktualna_ilosc == 30.0
    assert usunieto == 20.0

def test_zbiornik_oproznianie_pustego():

    z = Zbiornik(0, 0)
    z.aktualna_ilosc = 5.0
    
    usunieto = z.usun_ciecz(10.0)
    assert z.aktualna_ilosc == 0.0
    assert usunieto == 5.0
    assert z.czy_pusty() is True

def test_zbiornik_limity():
    z = Zbiornik(0, 0)
    z.pojemnosc = 100.0
    
    z.aktualna_ilosc = 90.0
    dodano = z.dodaj_ciecz(50.0)
    
    assert z.aktualna_ilosc == 100.0
    assert dodano == 10.0