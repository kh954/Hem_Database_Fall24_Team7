from flask import Flask, render_template, request, redirect, session
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
database_connection_session = psycopg2.connect(
    host="ep-quiet-sound-a5omz81p.us-east-2.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="oUrYj8HTAC6t",
    port=5432
)

@app.route('/')
def home():
    userdata = session.get('user')
    patdata = session.get('pat')  # Get patient-specific data from the session

    return render_template('index.html', userdata=userdata, patdata=patdata)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Secure the query to avoid SQL injection
        with database_connection_session.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('SELECT * FROM users WHERE email=%s AND password=%s', (email, password))
            userdata = cur.fetchone()

            if userdata:
                # Save user data to the session
                session['user'] = dict(userdata)

                # Fetch all patient data for this user from the patient table
                user_id = userdata['id']
                cur.execute('SELECT * FROM patient WHERE user_id=%s', (user_id,))
                patient_data = cur.fetchone()

                if patient_data:
                    # Save patient data to a separate session variable
                    session['pat'] = dict(patient_data)

                return redirect('/')  # Redirect to the profile page or home
            else:
                # If user data is not found, the email or password is incorrect
                message = 'Invalid email or password'
                return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.clear()  # Clear session data on logout
    return redirect('/')  # Redirect to the home page or login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # Collect form data
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        role = request.form.get('role')
        address = request.form.get('address')

        if password != confirm_password:
            message = 'Passwords do not match!'
        else:
            with database_connection_session.cursor() as cur:
                # Check if user exists
                cur.execute('SELECT * FROM users WHERE email=%s', (email,))
                if cur.fetchone():
                    message = "User already exists!"
                else:
                    # Insert new user into database
                    cur.execute(
                        '''
                        INSERT INTO users (fname, lname, email, password, contact, gender, role) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        RETURNING id
                        ''',
                        (firstname, lastname, email, password, contact, gender, role)
                    )
                    database_connection_session.commit()
                    new_user_id = cur.fetchone()[0]

                    cur.execute(
                        'INSERT INTO patient (user_id, age, address, medical_record_id) VALUES (%s, %s, %s, %s)',
                        (new_user_id, age, address, 1)
                    )
                    database_connection_session.commit()
                    message = "User created successfully!"

        # Render a response (you can redirect or show a success message)
        return render_template('register.html', msg=message)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/login')  # Redirect to login if not logged in

    userdata = session.get('user')  # Fetch user data from the session
    patdata = session.get('pat')  # Fetch patient data from the session

    if request.method == 'POST':
        # Update the database
        new_firstname = request.form.get('firstname')
        new_lastname = request.form.get('lastname')
        new_age = request.form.get('age')
        new_address = request.form.get('address')

        with database_connection_session.cursor() as cur:
            # Update the users table
            cur.execute(
                'UPDATE users SET fname=%s, lname=%s WHERE id=%s',
                (new_firstname, new_lastname, userdata['id'])
            )

            # Update the patient table
            cur.execute(
                'UPDATE patient SET age=%s, address=%s WHERE user_id=%s',
                (new_age, new_address, userdata['id'])
            )

            database_connection_session.commit()

            # Update the session data
            userdata['fname'] = new_firstname
            userdata['lname'] = new_lastname
            session['user'] = userdata

            patdata['age'] = new_age
            patdata['address'] = new_address
            session['pat'] = patdata

            return redirect('/')  # Redirect to profile or home page

    # Render the edit profile form
    return render_template('edit_profile.html', userdata=userdata, patdata=patdata)

if __name__ == '__main__':
    app.run(debug=True)
