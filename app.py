#https://github.com/modcomlearning/FlaskProject
#import flask
import requests
from flask import *
#method 2 of installing: cick View - Tools Window - Terminal
#once at terminal,type :pip install flask
#create the flask object
app = Flask(__name__)#__name__ means main
#This secret key encrypts your user session for security reasons
app.secret_key = 'ASDF__awth$%%!=l'#16
@app.route('/')
def home():
    return render_template('home.html')

import pymysql
#establish db connection
connection = pymysql.connect(host='localhost', user='root', password='', database='clothes_db')
@app.route('/tops')
def tops():
    #create ur query
    sql = "SELECT * FROM products_tbl "
    #run ur query
    #create a cursor used to execute sql
    cursor = connection.cursor()
    #now use the cursor to execute the sql
    cursor.execute(sql)
    #check how many rows are returned
    if cursor.rowcount == 0:
        return render_template("tops.html", msg='Out of stock')
    else:
        rows = cursor.fetchall()
        return render_template('tops.html', rows=rows)


@app.route('/single/<product_id>')
def single(product_id):
    #create ur query
    sql = "SELECT * FROM products_tbl WHERE product_id = %s"
    #run ur query
    #create a cursor used to execute sql
    cursor = connection.cursor()
    #now use the cursor to execute the sql
    cursor.execute(sql, (product_id))
    #check how many rows are returned
    if cursor.rowcount == 0:
        return render_template("single.html", msg='Product does not exist')
    else:
        row = cursor.fetchone()
        return render_template('single.html', row=row)

@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        customer_fname = request.form['customer_fname']
        customer_lname = request.form['customer_lname']
        customer_surname = request.form['customer_surname']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        customer_password = request.form['customer_password']
        customer_password2 = request.form['customer_password2']
        customer_gender = request.form['customer_gender']
        customer_address = request.form['customer_address']
        dob = request.form['dob']

        # validations
        import re
        if customer_password != customer_password2:
            return render_template('register.html', password = 'Password do not match')

        elif len(customer_password) < 8:
            return render_template('register.html', password='Password must 8 characters')

        elif not re.search("[a-z]", customer_password):
            return render_template('register.html', password='Must have a small letter')

        elif not re.search("[A-Z]", customer_password):
            return render_template('register.html', password='Must have a caps letter')

        elif not re.search("[0-9]", customer_password):
            return render_template('register.html', password='Must have a number')

        elif not re.search("[_@$]", customer_password):
            return render_template('register.html', password='Must have a small letter')

        elif len(customer_phone) < 10:
            return render_template('register.html', phone='Must be above 10 numbers')

        else:
            sql = "insert into customers(customer_fname, customer_lname, customer_surname, customer_email, customer_phone, customer_password, customer_gender, customer_address, dob) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor = connection.cursor()
            try:
                cursor.execute(sql, (customer_fname, customer_lname, customer_surname,
                                     customer_email,customer_phone, customer_password,
                                     customer_gender, customer_address, dob))
                connection.commit()
                return render_template('register.html', success = 'Saved Successfully')
            except:
                return render_template('register.html', error='Failed')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        #receive the posted email and password as variables
        email = request.form['email']
        password = request.form['password']
        #we move to the db and confirm if above details exist
        sql = "SELECT * FROM customers where customer_email = %s and customer_password = %s"
        #create a cursor and execute above sql
        cursor = connection.cursor()
        #execute the sql,provide email and password to fit %s placeholders
        cursor.execute(sql, (email, password))
        #check if a match was found
        if cursor.rowcount == 0:
            return render_template('login.html', error='Wrong Credentials')
        elif cursor.rowcount == 1:
            session['user'] = email
            return redirect('/tops')
        else:
            return render_template('login.html', error='Error Occurred, Try Later')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout ():
    session.pop('user')
    return redirect('/login')


@app.route('/reviews',methods = ['POST','GET'])
def reviews():
    if request.method == 'POST':
        user = request.form['user']
        product_id = request.form['product_id']
        message = request.form['message']
        #Do a table for reviews
        sql = "insert into reviews(user,product_id,message)values(%s,%s,%s)"
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (user, product_id, message))
            connection.commit()
            #when going back to /single carrying the product_id
            flash("Thank you for your review")
            return redirect(url_for('single', product_id=product_id ))
        except:
            flash("Review not posted")
            flash("Please try again")
            return redirect(url_for('single', product_id=product_id))
    else:
        return

@app.route('/contact',methods = ['POST','GET'])
def contact():
    if request.method == 'POST':
        contact_name = request.form['contact_name']
        contact_email = request.form['contact_email']
        contact_message = request.form['contact_message']

        sql = "insert into contact(contact_name,contact_email,contact_message)values(%s,%s,%s)"
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (contact_name, contact_email, contact_message))
            connection.commit()
            flash("Message sent successfully")
            return redirect('/tops')
        except:
            flash("Message not sent")
            flash("Please try again")
            return render_template('contact.html', error='Error Occurred, Try Later')
    else:
        return render_template('contact.html')




#https://github.com/modcomlearning/mpesa_sample
#create a payment template
#create a daraja account:https://developer.safaricom.co.ke/Documentation

import datetime
import base64
from requests.auth import HTTPBasicAuth
@app.route('/mpesa_payment', methods = ['POST','GET'])
def mpesa_payment():
        if request.method == 'POST':
            phone = str(request.form['phone'])
            amount = str(request.form['amount'])
            # GENERATING THE ACCESS TOKEN
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" #AUTH URL
            r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

            data = r.json()
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
            business_short_code = "174379"
            data = business_short_code + passkey + timestamp
            encoded = base64.b64encode(data.encode())
            password = encoded.decode('utf-8')


            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password": "{}".format(password),
                "Timestamp": "{}".format(timestamp),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
                "AccountReference": "account",
                "TransactionDesc": "account"
            }

            # POPULAING THE HTTP HEADER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" #C2B URL

            response = requests.post(url, json=payload, headers=headers)
            print (response.text)
            return render_template('payments.html', msg = 'Please Complete Payment in Your Phone')
        else:
            return render_template('payments.html')

@app.route('/sets')
def sets():
    #create ur query
    sql = "SELECT * FROM sets "
    #run ur query
    #create a cursor used to execute sql
    cursor = connection.cursor()
    #now use the cursor to execute the sql
    cursor.execute(sql)
    #check how many rows are returned
    if cursor.rowcount == 0:
        return render_template("sets.html", msg='Out of stock')
    else:
        rows = cursor.fetchall()
        return render_template('sets.html', rows=rows)

@app.route('/setsingle/<set_id>')
def setsingle(set_id):
    #create ur query
    sql = "SELECT * FROM sets WHERE set_id = %s"
    #run ur query
    #create a cursor used to execute sql
    cursor = connection.cursor()
    #now use the cursor to execute the sql
    cursor.execute(sql, (set_id))
    #check how many rows are returned
    if cursor.rowcount == 0:
        return render_template("setsingle.html", msg='Product does not exist')
    else:
        row = cursor.fetchone()
        return render_template('setsingle.html', row=row)


@app.route('/admin', methods = ['POST','GET'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # we now move to the database and confirm if above details exist
        sql = "SELECT * FROM admin where email = %s and password=%s"
        # create a cursor and execute above sql
        cursor = connection.cursor()
        # execute the sql, provide email and password to fit %s placeholders
        cursor.execute(sql, (email, password))
        # check if a match was found
        if cursor.rowcount ==0:
            return render_template('admin.html', error = 'Wrong Credentials')
        elif cursor.rowcount ==1:
            session['admin'] = email
            return  redirect('/dashboard')
        else:
            return render_template('admin.html', error='Error Occured, Try Later')
    else:
        return render_template('admin.html')



@app.route('/dashboard')
def dashboard():
    if 'admin' in session:
        sql = "select * from customers"
        cursor = connection.cursor()
        cursor.execute(sql)
        if cursor.rowcount == 0:
            return render_template('dashboard.html', msg = "No Customers")
        else:
            rows = cursor.fetchall()
            return  render_template('dashboard.html', rows = rows) # create this template
    else:
        return redirect('/admin')


@app.route('/customer_del/<customer_id>')
def customer_del(customer_id):
    if 'admin' in session:
        sql = 'delete from customers where customer_id = %s'
        cursor = connection.cursor()
        cursor.execute(sql,(customer_id))
        connection.commit()
        return redirect('/dashboard')
    else:
        return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)



