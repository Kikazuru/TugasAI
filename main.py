from json import load
from os import system

import networkx as nx
import matplotlib.pyplot as plt

from utm import from_latlon
from sys import maxsize
from itertools import permutations

class TSP:
    def __init__(self):
        self.daftar_lokasi = []
        self.graf = None
        self.n = None

    def show_graf(self):
        G = nx.Graph()
        
        for lokasi in self.daftar_lokasi:
            nama = lokasi["nama"]
            koordinat = lokasi["koordinat"]
            G.add_node(nama, pos=(koordinat[0],koordinat[1]))

        for i in range(self.n):
            nama1 = self.daftar_lokasi[i]["nama"]
            for j in range(i + 1, self.n):
                nama2 = self.daftar_lokasi[j]["nama"]
                G.add_edge(nama1, nama2, weight = self.graf[i][j])

        pos=nx.get_node_attributes(G,'pos')
        nx.draw(G,pos)
        nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
        plt.show()
    
    def add_node(self, node):
        nama = node["nama"]
        koordinat = node["koordinat"]
        koordinat = from_latlon(koordinat[0], koordinat[1])
        x,y = koordinat[0],koordinat[1]
        self.daftar_lokasi.append({"nama":nama, "koordinat":(x,y)})

    def generate_graf(self):
        self.n = n = len(self.daftar_lokasi)
        self.graf = [[0] * n for _ in range(n)]
        for i in range(n):
            x1, y1 = self.daftar_lokasi[i]["koordinat"]
            for j in range(i + 1, n):
                x2, y2 = self.daftar_lokasi[j]["koordinat"]
                jarak = (abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2) ** (0.5)
                self.graf[i][j] = round(jarak, 4)
                self.graf[j][i] = round(jarak, 4)
    
    def solve(self):
        vertex = [i for i in range(1, len(self.graf))]

        min_path = maxsize # 99999
        next_permutation = permutations(vertex)
        hasil_jalur_terbaik = None

        for permutasi in next_permutation:
            current_pathweight = 0

            k = 0
            for j in permutasi:
                current_pathweight += self.graf[k][j]
                k = j
                
            current_pathweight += self.graf[k][0]

            if current_pathweight < min_path:
                min_path = current_pathweight
                hasil_jalur_terbaik = permutasi

        hasil_jalur_terbaik = [self.daftar_lokasi[0]["nama"]] + [self.daftar_lokasi[i]["nama"] for i in hasil_jalur_terbaik]
        return hasil_jalur_terbaik, min_path



def show_pilihan(daftar_lokasi, dipilih):
    print("Pilih lokasi : ")
    i = 0
    for cek, lokasi in zip(dipilih, daftar_lokasi):
        nama = lokasi['nama']
        if not cek:
            print(f"{i}. {nama}")
        i += 1
    print(f"{i}. KELUAR")

if __name__ == '__main__':
    daftar_lokasi = load((open("lokasi.json")))
    dipilih = [0] * len(daftar_lokasi)

    tsp = TSP()

    tsp.add_node(daftar_lokasi[0])
    dipilih[0] = 1

    while True:
        print("Pilih menu : ")
        print("1. Tambah lokasi")
        print("2. Tampilkan graf")
        print("3. Hasil")
        print("4. Exit")
        n = input(": ")
        if n == "1":
            while True:
                show_pilihan(daftar_lokasi, dipilih)
                try:
                    #problem disini bug pilihan
                    n = int(input(": "))
                    system("clear")
                    
                    if n == len(daftar_lokasi):
                        tsp.generate_graf()
                        break

                    if -1 < n < len(daftar_lokasi) and not dipilih[n]:
                        dipilih[n] = 1
                        tsp.add_node(daftar_lokasi[n])
                    else:
                        print("Anda sudah memilih lokasi tersebut")
                    
                except:
                    print("Pilihan tidak ditemukan!") 
        elif n == '2':
            print(tsp.graf)
            tsp.show_graf()
        elif n == '3':
            hasil_jalur_terbaik, bobot_minimal = tsp.solve()
            print(hasil_jalur_terbaik)
            print(bobot_minimal)
        elif n == '4':
            break
    
    
        

