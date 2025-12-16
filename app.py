from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask import request, redirect, url_for

from wp import hitung_wp

app = Flask(__name__)

# KONFIGURASI MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''   
app.config['MYSQL_DB'] = 'spk_wp'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kriteria")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', data=data)

def dashboard():
    return render_template('dashboard.html')

@app.route('/kriteria', methods=['GET', 'POST'])
def kriteria():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama = request.form['nama']
        bobot = request.form['bobot']
        tipe = request.form['tipe']

        cur.execute(
            "INSERT INTO kriteria (nama_kriteria, bobot, tipe) VALUES (%s,%s,%s)",
            (nama, bobot, tipe)
        )
        mysql.connection.commit()

    cur.execute("SELECT * FROM kriteria")
    data = cur.fetchall()
    cur.close()

    return render_template('kriteria.html', kriteria=data)

@app.route('/alternatif', methods=['GET','POST'])
def alternatif():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama = request.form['nama']
        cur.execute(
            "INSERT INTO alternatif (nama_alternatif) VALUES (%s)",
            (nama,)
        )
        mysql.connection.commit()

    cur.execute("SELECT * FROM alternatif")
    data = cur.fetchall()
    cur.close()

    return render_template('alternatif.html', alternatif=data)

@app.route('/hasil')
def hasil():
    cur = mysql.connection.cursor()

    # Ambil alternatif
    cur.execute("SELECT * FROM alternatif")
    alternatif_db = cur.fetchall()

    # Ambil kriteria
    cur.execute("SELECT * FROM kriteria")
    kriteria_db = cur.fetchall()

    # Ambil nilai
    cur.execute("SELECT * FROM nilai")
    nilai_db = cur.fetchall()

    cur.close()

    # Mapping alternatif
    alternatif = [
        {'id': a[0], 'nama': a[1]} for a in alternatif_db
    ]

    # Mapping kriteria
    kriteria = [
        {'id': k[0], 'nama': k[1], 'bobot': k[2], 'tipe': k[3]}
        for k in kriteria_db
    ]

    # Mapping nilai
    nilai = {}
    for n in nilai_db:
        nilai[(n[1], n[2])] = n[3]

    # Hitung WP
    ranking = hitung_wp(alternatif, kriteria, nilai)

    return render_template('hasil.html', ranking=ranking)



@app.route('/nilai', methods=['GET','POST'])
def nilai():
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM alternatif")
    alternatif = cur.fetchall()

    cur.execute("SELECT * FROM kriteria")
    kriteria = cur.fetchall()

    if request.method == 'POST':
        alt_id = request.form['alternatif']
        for k in kriteria:
            nilai = request.form[f'nilai_{k[0]}']
            cur.execute(
                "INSERT INTO nilai (alternatif_id, kriteria_id, nilai) VALUES (%s,%s,%s)",
                (alt_id, k[0], nilai)
            )
        mysql.connection.commit()

    cur.close()
    return render_template('nilai.html', alternatif=alternatif, kriteria=kriteria)








if __name__ == '__main__':
    app.run(debug=True)
