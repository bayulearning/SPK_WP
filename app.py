from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask import request, redirect, url_for

from wp import hitung_wp

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''   
app.config['MYSQL_DB'] = 'spk_wp'

mysql = MySQL(app)

# @app.route('/')
# def index():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM kriteria")
#     data = cur.fetchall()
#     cur.close()
#     return render_template('index.html', data=data)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM alternatif")
    alternatif_db = cur.fetchall()

    cur.execute("SELECT * FROM kriteria")
    kriteria_db = cur.fetchall()

    cur.execute("SELECT alternatif_id, kriteria_id, nilai FROM nilai")
    nilai_db = cur.fetchall()
    cur.close()

    # mapping nilai
    nilai = {(a, k): v for a, k, v in nilai_db}

    alternatif = [{'id': a[0], 'nama': a[1]} for a in alternatif_db]
    kriteria = [
        {'id': k[0], 'nama': k[1], 'bobot': float(k[2]), 'tipe': k[3]}
        for k in kriteria_db
    ]

    from wp import hitung_wp
    ranking = hitung_wp(alternatif, kriteria, nilai)

    return render_template(
        'dashboard.html',
        ranking=ranking,
        alternatif=alternatif,
        kriteria=kriteria,
        nilai=nilai
    )



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
    rows = cur.fetchall()

    kriteria = []
    for k in rows:
        kriteria.append({
            'id': k[0],
            'nama': k[1],
            'bobot': k[2],
            'tipe': k[3]
        })

    return render_template('kriteria.html', kriteria=kriteria)



@app.route('/alternatif', methods=['GET', 'POST'])
def alternatif():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama = request.form['nama']
        cur.execute(
            "INSERT INTO alternatif (nama_alternatif) VALUES (%s)",
            (nama,)
        )
        mysql.connection.commit()
        cur.close()

        
        return redirect(url_for('nilai'))

    
    cur.execute("SELECT * FROM alternatif")
    data = cur.fetchall()
    cur.close()

    return render_template('alternatif.html', alternatif=data)


@app.route('/hasil')
def hasil():
    cur = mysql.connection.cursor()

    
    cur.execute("SELECT * FROM alternatif")
    alternatif_db = cur.fetchall()

    
    cur.execute("SELECT * FROM kriteria")
    kriteria_db = cur.fetchall()

    
    cur.execute("""
        SELECT alternatif_id, kriteria_id, nilai
        FROM nilai
    """)
    nilai_db = cur.fetchall()
    cur.close()

    # Mapping alternatif
    alternatif = [
        {'id': a[0], 'nama': a[1]}
        for a in alternatif_db
    ]

    # Mapping kriteria
    kriteria = [
        {'id': k[0], 'nama': k[1], 'bobot': k[2], 'tipe': k[3]}
        for k in kriteria_db
    ]

    
    nilai = {}
    for alt_id, kri_id, nilai_val in nilai_db:
        nilai[(alt_id, kri_id)] = nilai_val

    # print("NILAI DB:", nilai_db)

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
            nilai_input = request.form.get(f'nilai_{k[0]}')

            if nilai_input:
                cur.execute("""
                    INSERT INTO nilai (alternatif_id, kriteria_id, nilai)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nilai = %s
                """, (alt_id, k[0], nilai_input, nilai_input))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('dashboard'))

    cur.close()
    return render_template('nilai.html', alternatif=alternatif, kriteria=kriteria)

# Edit & Update / Delete

@app.route('/alternatif/edit/<int:id>')
def edit_alternatif(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM alternatif WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return redirect(url_for('alternatif'))

    return render_template('alternatif_edit.html', alternatif=data)

@app.route('/alternatif/update/<int:id>', methods=['POST'])
def update_alternatif(id):
    nama = request.form['nama']

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE alternatif SET nama_alternatif = %s WHERE id = %s",
        (nama, id)
    )
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('alternatif'))

@app.route('/kriteria/edit/<int:id>')
def edit_kriteria(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kriteria WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return redirect(url_for('kriteria'))

    return render_template('kriteria_edit.html', kriteria=data)

@app.route('/kriteria/update/<int:id>', methods=['POST'])
def update_kriteria(id):
    nama = request.form['nama']
    bobot = request.form['bobot']
    tipe = request.form['tipe']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE kriteria
        SET nama_kriteria = %s, bobot = %s, tipe = %s
        WHERE id = %s
    """, (nama, bobot, tipe, id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('kriteria'))

@app.route('/kriteria/delete/<int:id>', methods=['POST'])
def delete_kriteria(id):
    cur = mysql.connection.cursor()

    # hapus nilai dulu (FK)
    cur.execute("DELETE FROM nilai WHERE kriteria_id = %s", (id,))
    cur.execute("DELETE FROM kriteria WHERE id = %s", (id,))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('kriteria'))

@app.route('/alternatif/delete/<int:id>', methods=['POST'])
def delete_alternatif(id):
    cur = mysql.connection.cursor()

    # 1. Hapus nilai milik alternatif ini dulu
    cur.execute("DELETE FROM nilai WHERE alternatif_id = %s", (id,))

    # 2. Baru hapus alternatif
    cur.execute("DELETE FROM alternatif WHERE id = %s", (id,))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('alternatif'))


if __name__ == '__main__':
    app.run(debug=True)
