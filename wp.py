import math
import copy

def hitung_wp(alternatif, kriteria, nilai):
    hasil = []

    print("DEBUG kriteria:", kriteria)

    # COPY agar tidak merusak data asli
    kriteria_local = copy.deepcopy(kriteria)

    for k in kriteria:
        if 'bobot' not in k:
            raise Exception(f"Kriteria tidak valid: {k}")

    total_bobot = sum(float(k['bobot']) for k in kriteria)


    for k in kriteria_local:
        k['bobot_norm'] = float(k['bobot']) / total_bobot

    for alt in alternatif:
        log_S = 0
        detail_nilai = {}

        for k in kriteria_local:
            key = (alt['id'], k['id'])

            if key not in nilai:
                raise Exception(
                    f"Nilai alternatif '{alt['nama']}' "
                    f"untuk kriteria '{k['nama']}' belum ada"
                )

            v = float(nilai[key])
            w = k['bobot_norm']

            if k['tipe'] == 'cost':
                w = -w

            log_S += w * math.log(v)
            detail_nilai[k['nama']] = v

        S = math.exp(log_S)

        hasil.append({
            'id': alt['id'],
            'nama': alt['nama'],
            'nilai': S,
            'detail': detail_nilai
        })

    total_S = sum(h['nilai'] for h in hasil)

    for h in hasil:
        h['preferensi'] = h['nilai'] / total_S

    hasil = sorted(hasil, key=lambda x: x['preferensi'], reverse=True)

    for i, h in enumerate(hasil, start=1):
        h['rank'] = i

    return hasil
