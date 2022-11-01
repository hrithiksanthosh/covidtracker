from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'covidlogin'

mysql = MySQL(app)

def send_email(receiver_email, uniqueid):
    import smtplib, ssl

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "gov.coviddetails@gmail.com"  # Enter your address
    password = "testcoen6311"
    message = "Your UniqueId %s to view the covid details" % uniqueid

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        tablename = "government_login"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cmd = 'SELECT * FROM %s WHERE username = "%s" AND password = "%s"' % (tablename, username, password)
        cursor.execute(cmd)
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            return render_template('register.html')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/vaccine', methods=['GET', 'POST'])
def vaccine():
    msg = ''
    if request.method == 'POST' and 'uniqueId' in request.form:
        uniqueId = request.form['uniqueId']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cmd = 'SELECT * FROM vaccine WHERE uniqueId = "% s"' % (uniqueId)
        cursor.execute(cmd)
        account = cursor.fetchone()
        if account:
            msg = 'UniqueId is validated'
            session['name'] = account['name']
            session['email'] = account['email']
            session['dateofbirth'] = account['dateofbirth']
            session['firstdose'] = account['firstdose']
            session['firstdosename'] = account['firstdosename']
            session['firstdate'] = account['date']
            session['seconddose'] = account['seconddose']
            session['seconddate'] = account['seconddate']
            session['seconddosename'] = account['seconddosename']
            session['location'] = account['location']
            return render_template('vaccinedetails.html', msg=msg)
        else:
            msg = 'Incorrect UniqueId'
    return render_template('vaccine.html', msg=msg)

@app.route('/testresult', methods=['GET', 'POST'])
def testresults():
    msg = ''
    if request.method == 'POST' and 'uniqueId' in request.form:
        uniqueId = request.form['uniqueId']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cmd = 'SELECT * FROM test WHERE uniqueId = "% s"' % (uniqueId)
        cursor.execute(cmd)
        account = cursor.fetchone()
        if account:
            msg = 'UniqueId is validated'
            session['name'] = account['Name']
            session['email'] = account['email']
            session['dateofbirth'] = account['dateofbirth']
            session['date'] = account['date']
            session['result'] = account['Result']
            session['location'] = account['location']
            return render_template('testdetails.html', msg=msg)
        else:
            msg = 'Incorrect UniqueId'
    return render_template('testresults.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('homepage'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'dob' in request.form and 'location' in request.form:
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        location = request.form['location']
        uniqueid = name[:4] + dob[len(dob)-2:len(dob)]
        selected_field = (request.form["coviddata"])
        if selected_field == 'vaccine':
            vaccine_dose = request.form['dosenumber']
            vaccine_date = request.form['vaccinedate']
            vaccine_name = request.form['vaccinename']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cmd = 'SELECT * FROM vaccine WHERE uniqueid = "%s"' % uniqueid
            cursor.execute(cmd)
            account = cursor.fetchone()
            if account:
                cmd = "UPDATE vaccine SET seconddose='%s', seconddate='%s', seconddosename='%s' WHERE (UniqueId = '%s');" % (
                    vaccine_dose, vaccine_date, vaccine_name, uniqueid)
                cursor.execute(cmd)
                mysql.connection.commit()
                msg = 'You have successfully registered !'
            else:
                if vaccine_dose == '1':
                    cmd = "INSERT INTO vaccine (name, dateofbirth, email, firstdose, date, firstdosename, UniqueId, location) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s')" % (name, dob, email,
                                                                                                              vaccine_dose, vaccine_date, vaccine_name, uniqueid, location)
                elif vaccine_dose == '2':
                    cmd = "INSERT INTO vaccine (name, dateofbirth, email, seconddose, seconddate, seconddosename, UniqueId, location) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s')" % (name, dob, email,
                                                                                                              vaccine_dose, vaccine_date, vaccine_name, uniqueid, location)
                cursor.execute(cmd)
                mysql.connection.commit()
                msg = 'You have successfully registered !'
        elif selected_field == 'test':
            test_date = request.form['testdate']
            test_result = request.form['testresult']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cmd = 'SELECT * FROM test WHERE uniqueid = "%s"' % uniqueid
            cursor.execute(cmd)
            account = cursor.fetchone()
            if account:
                cmd = "UPDATE test SET date='%s', Result='%s' WHERE (UniqueId = '%s');" % (
                                        test_date, test_result, uniqueid)
                cursor.execute(cmd)
                mysql.connection.commit()
                msg = 'You have successfully registered !'
            else:
                cmd = "INSERT INTO test (name, dateofbirth, email, date, result, UniqueId, location) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                                        name, dob, email, test_date, test_result, uniqueid, location)
                cursor.execute(cmd)
                mysql.connection.commit()
                msg = 'You have successfully registered !'
        else:
            msg = "Please select vaccine details or test results to register"

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

if __name__ == '__main__':
   app.run()
