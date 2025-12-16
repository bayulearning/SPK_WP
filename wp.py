import math

def hitung_wp(alternatif, kriteria, nilai):
    # normalisasi bobot
    total_bobot = sum([k['bobot'] for k in kriteria])
    for k in kriteria:
        k['bobot'] /= total_bobot
        if k['tipe'] == 'cost':
            k['bobot'] *= -1

    hasil = {}
    for a in alternatif:
        S = 1
        for k in kriteria:
            n = nilai[(a['id'], k['id'])]
            S *= n ** k['bobot']
        hasil[a['nama']] = S

    total_S = sum(hasil.values())
    V = {k: v / total_S for k, v in hasil.items()}

    return sorted(V.items(), key=lambda x: x[1], reverse=True)
