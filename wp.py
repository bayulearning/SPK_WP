import math

def hitung_wp(alternatif, kriteria, nilai):
    hasil = []
    total_bobot = sum(float(k['bobot']) for k in kriteria)

    for k in kriteria:
        k['bobot'] = float(k['bobot']) / total_bobot

    for alt in alternatif:
        log_S = 0

        for k in kriteria:
            key = (alt['id'], k['id'])

            if key not in nilai:
                raise Exception(
                    f"Nilai alternatif '{alt['nama']}' "
                    f"untuk kriteria '{k['nama']}' belum ada"
                )

            v = float(nilai[key])
            w = float(k['bobot'])

            if k['tipe'] == 'cost':
                w = -w

            log_S += w * math.log(v)

        S = math.exp(log_S)

        hasil.append({
            'id': alt['id'],
            'nama': alt['nama'],
            'nilai': S
        })

    total = sum(h['nilai'] for h in hasil)

    for h in hasil:
        h['preferensi'] = h['nilai'] / total

    return sorted(hasil, key=lambda x: x['preferensi'], reverse=True)
