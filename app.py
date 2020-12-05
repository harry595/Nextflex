from flask import Flask, render_template, json, request,flash, url_for,redirect, session, send_from_directory, Blueprint, make_response, jsonify, current_app
import pymysql
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '12rf1124g341h13'
db = pymysql.connect(host='localhost', port=33061, user='root',passwd='hh237237!!',db='nextflexdb',charset='utf8')
cursor=db.cursor()

 
@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/movie_queue/<int:movie_id>')
def movie_queue(movie_id):
    user_id=session['user']
    sql = "INSERT INTO moviequeue(movieID,CustomerID) VALUES(%s,%s);"
    cursor.execute(sql,(movie_id,user_id))
    db.commit()
    return redirect('/movies')

@app.route('/movies')
def movies():
  rtype=request.args.get('search_type')
  ktype=request.args.get('keywords')
  if(ktype == ''):
    sql = "SELECT * FROM movie"
    rows_count = cursor.execute(sql)
    if rows_count > 0 :
        movie_info = cursor.fetchall()
    else:
        movie_info=None
    return render_template('movies.html',movies=movie_info)
  else:
      if(rtype=="movie"):
        sql = "SELECT * FROM movie WHERE MovieName LIKE %s"
        rows_count = cursor.execute(sql, (('%' + ktype + '%',)))
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info)
      elif(rtype=="actor"):
        sql = "SELECT * FROM movie left JOIN movieinfo_actor ON movie.MovieID = movieinfo_actor.Movie_info_ID left JOIN actor ON actor.ActorID = movieinfo_actor.Actor_info_ID WHERE ActorName LIKE %s;"
        rows_count = cursor.execute(sql,(('%' + ktype + '%',)))
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info)
      elif(rtype=="movie_type"):
        sql = "SELECT * FROM MOVIE WHERE MovieType= %s"
        rows_count = cursor.execute(sql,ktype)
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info)
      else:
        sql = "SELECT * FROM movie"
        rows_count = cursor.execute(sql)
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info)

    

@app.route('/mypage')
def mypage():
    user_id=session['user']
    sql = "SELECT * FROM customer WHERE CustomerID= %s"
    cursor.execute(sql,user_id)
    user_info = cursor.fetchone()

    sql2 = "SELECT * FROM account where CustomerID=%s"
    cursor.execute(sql2,user_id)
    account_info = cursor.fetchall()
    return render_template('mypage.html',user_info=user_info,account_info=account_info)

@app.route('/logout') 
def logout(): 
    session.pop('user', None) 
    return redirect('/')

# 추가
@app.route('/login', methods=['POST','GET'])
def about():
    if request.method == 'POST':
        login_info = request.form
        EmailAddress = login_info['email']
        Passwd = login_info['passwd']
        sql = "SELECT * FROM customer WHERE EmailAddress = %s"
        rows_count = cursor.execute(sql,EmailAddress)
        if rows_count > 0 :
            user_info = cursor.fetchone()
            pw_correct = bcrypt.checkpw(Passwd.encode('UTF-8'), user_info[1].encode('UTF-8'))
            session['user'] = user_info[0]
        else:
            print('User does not exist')
            return redirect(request.url)
        return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        register_info = request.form
        EmailAddress = register_info['email']

        if register_info['password1'] != register_info['password2']:
            print('mismatch password')
            return render_template('signup.html')
            
        Passwd = bcrypt.hashpw(register_info['password1'].encode('utf-8'),bcrypt.gensalt())
        FirstName = register_info['Firstname']
        LastName = register_info['Lastname']
        sql="""
            INSERT INTO customer (EmailAddress,Passwd,FirstName,LastName)
            VALUES (%s,%s,%s,%s);
        """
        cursor.execute(sql,(EmailAddress,Passwd,FirstName,LastName))
        db.commit()
        db.close()
        return redirect('login')
    return render_template('signup.html')