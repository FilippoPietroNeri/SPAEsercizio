import jwt
from flask import Flask, render_template, request, jsonify, session
from utils.db import create_connection

app = Flask(__name__)
app.json.sort_keys = False
app.secret_key = '0zVNpqTWddJv3m2EgsJSH5kfpoHvsmqQ'

# Endpoint / 
@app.route('/')
def homepage():
    return render_template('index.html')

### API ###

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        connection = create_connection()

        userEmail = data['Email']
        userPassword = data['Password']

        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT * FROM Docente AS p
        WHERE p.Email = (%s);
        """, (userEmail,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({ 'error': 'User does not exist'}), 400

        token = jwt.encode(
            payload=user,
            key=app.secret_key
        )

        if user['Email'] == userEmail and user['Password'] == userPassword:
            session['logged_in'] = user['ID']
            return jsonify({ 'message': 'User logged in!', 'success': True, 'token': token }), 200
        else:
            return jsonify({ 'error': 'Wrong email or password!'}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({ 'message': 'Logged out' }), 200

# Endpoint API /api/docenti
@app.route('/api/docenti', methods=['GET'])
def get_docenti():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT ID, Nome, Cognome, Email FROM Docente;")    
    docenti = cursor.fetchall()
    cursor.close()

    return jsonify(docenti), 200

# Endpoint API /api/aule
@app.route('/api/aule', methods=['GET'])
def get_aule():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT ID FROM Aula;")    
    aule = cursor.fetchall()
    cursor.close()
    return jsonify(aule), 200

# Endpoint API /api/seminari
@app.route('/api/seminari', methods=['GET'])
def api_seminari():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.ID, s.Titolo, s.Orario, a.Capacita, d.Nome, d.Cognome 
        FROM Seminario s 
        JOIN Aula a ON s.AulaID = a.ID 
        JOIN Docente d ON s.DocenteID = d.ID 
        ORDER BY STR_TO_DATE(s.Orario, '%d/%m/%Y %h:%m:%s') ASC;
    """)
    seminari = cursor.fetchall()
    cursor.close()
    return jsonify(seminari), 200

# Endpoint API /api/prenotazioni
@app.route('/api/prenotazioni')
def api_prenotazioni():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.ID, p.NumeroStudenti, s.Titolo, s.Orario 
        FROM Prenotazioni p 
        JOIN Seminario s ON p.SeminarioID = s.ID;
    """)
    prenotazioni = cursor.fetchall()
    cursor.close()
    return jsonify(prenotazioni), 200

# Endpoint API /api/signup
@app.route('/api/signup', methods=['POST'])
def signup():
    connection = create_connection()

    data = request.json
    nome = data['Nome']
    cognome = data['Cognome']
    email = data['Email']
    password = data['Password']

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Docente (Nome, Cognome, Email, Password) 
        VALUES (%s, %s, %s, %s);
    """, (nome, cognome, email, password))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Docente registrato con successo!'}), 200

# Endpoint API /api/insert/seminario
@app.route('/api/insert/seminario', methods=['POST'])
def insert_seminario():
    connection = create_connection()

    data = request.json
    titolo = data['Titolo']
    orario = data['Orario']
    aula_id = data['AulaID']
    docente_id = data['DocenteID']

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Seminario (Titolo, Orario, AulaID, DocenteID) 
        VALUES (%s, %s, %s, %s);
    """, (titolo, orario, aula_id, docente_id))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Seminario inserito con successo!'}), 200

# Endpoint API /api/book
@app.route('/api/book', methods=['POST'])
def book_seminario():
    if not 'logged_in' in session:
        return jsonify({ 'error': 'You are not authorized' }), 401

    connection = create_connection()

    try:
        data = request.json
        seminario_id = data['SeminariID']
        numero_studenti = int(data['NumeroStudenti'])

        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.Capacita, COALESCE(SUM(p.NumeroStudenti), 0) AS TotalePrenotati 
            FROM Seminario s 
            JOIN Aula a ON s.AulaID = a.ID 
            LEFT JOIN Prenotazioni p ON s.ID = p.SeminarioID 
            WHERE s.ID = %s 
            GROUP BY a.Capacita;
        """, (seminario_id,))
        result = cursor.fetchone()
        if not result or result['TotalePrenotati'] + numero_studenti > result['Capacita']:
            return jsonify({'error': 'Capacità aula superata!'}), 400

        cursor.execute("""
            INSERT INTO Prenotazioni (SeminarioID, NumeroStudenti) 
            VALUES (%s, %s);
        """, (seminario_id, numero_studenti))
        connection.commit()
        cursor.close()
        return jsonify({'message': 'Prenotazione effettuata con successo!'}), 200
    except err:
        return jsonify({'error': "C'è stato un errore nel mentre che stavi provando a prenotare un seminario!"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3452, debug=True)