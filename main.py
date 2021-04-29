from json import load
from os import system
import networkx as nx
import matplotlib.pyplot as plt
from utm import from_latlon

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
    

def show_pilihan(daftar_lokasi, dipilih):
    print("Pilih lokasi : ")
    i = 1
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
    while True:
        print("Pilih menu : ")
        print("1. Tambah lokasi")
        print("2. Tampilkan graf")
        print("3. Exit")
        n = input(": ")
        if n == "1":
            while True:
                show_pilihan(daftar_lokasi, dipilih)
                try:
                    n = abs(int(input(": ")) - 1)
                    system("clear")
                    
                    if n == len(daftar_lokasi):
                        tsp.generate_graf()
                        break

                    if not dipilih[n]:
                        dipilih[n] = 1
                        tsp.add_node(daftar_lokasi[n])
                    else:
                        print("Anda sudah memilih lokasi tersebut")
                    
                except:
                    print("Pilihan tidak ditemukan!") 
        elif n == '2':
            tsp.show_graf()
        elif n == '3':
            break
    
    
        

