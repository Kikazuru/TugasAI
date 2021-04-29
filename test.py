from utm import from_latlon
from json import load

temp = load(open("lokasi.json"))

utm = {}

for lokasi in temp:
    nama = lokasi["nama"]
    koor = lokasi["koordinat"]

    print(f"nama : {nama}")
    koor = from_latlon(koor[0], koor[1])
    utm[nama] = (koor[0], koor[1])

for x, y in utm.items():
    print(x, y)