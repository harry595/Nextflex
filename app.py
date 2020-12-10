from flask import Flask, render_template, json, request,flash, url_for,redirect, session, send_from_directory, Blueprint, make_response, jsonify, current_app
import pymysql
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '12rf1124g341h13'
db = pymysql.connect(host='localhost', port=33061, user='root',passwd='***',db='nextflexdb',charset='utf8')
cursor=db.cursor()

 
@app.route('/')
@app.route('/index')
def index():
    sql = "SELECT * FROM movie ORDER BY NumberOfCopies DESC limit 3"
    cursor.execute(sql)
    topmovie=cursor.fetchall()
    return render_template('index.html',topmovie=topmovie)

@app.route('/movie_queue/<int:movie_id>')
def movie_queue(movie_id):
    user_id=session['user']
    sql = "INSERT INTO moviequeue(movieID,CustomerID) VALUES(%s,%s);"
    cursor.execute(sql,(movie_id,user_id))
    db.commit()
    return redirect('/movies')
    
@app.route('/post_account', methods=['POST'])
def post_account():
    user_id=session['user']
    account_num = request.form['account_num']
    account_type = request.form['account_type']
    account_date = request.form['account_date']
    sql = "INSERT INTO account(CustomerID,AccountNum,AccountType,PlanExpiredDate) VALUES (%s,%s,%s,DATE_ADD(NOW(), INTERVAL %s month));"
    cursor.execute(sql,(user_id,account_num,account_type,account_date))
    db.commit()
    return jsonify({'result': 'success'})

@app.route('/returnmovie')
def returnmovie():
    user_id=session['user']
    orderid=request.args.get('oid')
    orderstar=request.args.get('ostar')
    sql = "UPDATE Orders SET holding=0,Rating=%s WHERE OrderID=%s and CustomerID=%s"
    cursor.execute(sql,(orderstar,orderid,user_id))
    sql2 = "SELECT MovieID FROM Orders WHERE OrderID=%s"
    cursor.execute(sql2,orderid)
    orderedmovie=cursor.fetchone()
    sql3 = "UPDATE Movie SET MovieRating= (SELECT AVG(Rating) FROM orders WHERE MovieID=%s) WHERE MovieID=%s"
    cursor.execute(sql3,(orderedmovie,orderedmovie))
    db.commit()
    return jsonify({'result': 'success'})

@app.route('/viewmovie')
def viewmovie():
  user_id=session['user']
  orderid=request.args.get('oid')

  sql = "SELECT * FROM Orders WHERE OrderID=%s and CustomerID=%s and holding=1"
  cursor.execute(sql,(orderid,user_id))
  ordercheck=cursor.fetchone()
  if(ordercheck is None):
    return redirect('/mypage')

  sql2 = "SELECT * FROM movie WHERE MovieID=%s"
  cursor.execute(sql2,ordercheck[2])
  movie_info = cursor.fetchone()
  
  return render_template('viewmovie.html',movie_info=movie_info)

@app.route('/makeorders')
def makeorders():
  qid=request.args.get('qid')
  user_id=session['user']

  #이미 order가 2개일 때 (return해야함) - unlimitedplan 
  checksql = "SELECT COUNT(*) FROM orders WHERE CustomerId=%s and holding=1"
  cursor.execute(checksql,user_id)
  resultflag=cursor.fetchone()
  if(resultflag[0]>=2):
    return redirect('/mypage')
    
  #account에서 유효한 plan이 없을때
  check2sql= "SELECT * FROM account WHERE CustomerID=%s and PlanExpiredDate>NOW();" 
  cursor.execute(check2sql,user_id)
  resultflag2=cursor.fetchall()
  flag=0

  #plans[4]-> movies column은 매달 1일 00시에 0으로 update
  for plans in resultflag2:
      if(plans[4]<2 or plans[3]=='Unlimited Plan'):
          flag=1
  if(flag==0):
    return redirect('/mypage')

  sql = "SELECT * FROM moviequeue WHERE QueueId=%s and CustomerID=%s"
  cursor.execute(sql,(qid,user_id))
  resultflag=cursor.fetchone()
  if resultflag[2]==user_id:
    sql2 = "INSERT INTO orders(MovieID,CustomerID) SELECT MovieID,CustomerID FROM moviequeue WHERE QueueId=%s"
    cursor.execute(sql2,qid)
    sql3 = "DELETE FROM moviequeue WHERE QueueId=%s"
    cursor.execute(sql3,qid)
    sql4 = "UPDATE account set movie=movie+1 WHERE CustomerID=%s;"
    cursor.execute(sql4,user_id)
    sql5 = "UPDATE movie set NumberOfCopies=NumberOfCopies+1 WHERE MovieID=%s;"
    cursor.execute(sql5,resultflag[1])
    db.commit()
  return redirect('/mypage')
  


@app.route('/movies')
def movies():
  rtype=request.args.get('search_type')
  ktype=request.args.get('keywords')
  user_id=session['user']
  sql_recommend='''SELECT * FROM Movie 
                    WHERE MovieType=(
                        SELECT MovieType 
                        FROM movie left join orders on orders.MovieID=movie.MovieID 
                        WHERE CustomerID=%s 
                        GROUP BY MovieType 
                        order by -COUNT(*) 
                        limit 1) 
                    order by -MovieRating limit 1;'''
  rows_count = cursor.execute(sql_recommend,user_id)
  recommend_movie = cursor.fetchone()

  if(ktype == ''):
    sql = "SELECT * FROM movie"
    rows_count = cursor.execute(sql)
    if rows_count > 0 :
        movie_info = cursor.fetchall()
    else:
        movie_info=None
    return render_template('movies.html',movies=movie_info,recommend_movie=recommend_movie)
  else:
      if(rtype=="movie"):
        sql = "SELECT * FROM movie WHERE MovieName LIKE %s"
        rows_count = cursor.execute(sql, (('%' + ktype + '%',)))
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info,recommend_movie=None)
      elif(rtype=="actor"):
        #두명 이상 검색
        if("," in ktype):
            ksplit=tuple(ktype.split(","))
            knum=len(ktype.split(","))
            sql = "SELECT * FROM movie left JOIN movieinfo_actor ON movie.MovieID = movieinfo_actor.Movie_info_ID left JOIN actor ON actor.ActorID = movieinfo_actor.Actor_info_ID where ActorName in %s GROUP BY MovieName HAVING COUNT(MovieName)=%s;"
            rows_count = cursor.execute(sql,(ksplit,knum))
            if rows_count > 0 :
                movie_info = cursor.fetchall()
            else:
                movie_info=None
            return render_template('movies.html',movies=movie_info,recommend_movie=None)
        sql = "SELECT * FROM movie left JOIN movieinfo_actor ON movie.MovieID = movieinfo_actor.Movie_info_ID left JOIN actor ON actor.ActorID = movieinfo_actor.Actor_info_ID WHERE ActorName LIKE %s;"
        rows_count = cursor.execute(sql,(('%' + ktype + '%',)))
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info,recommend_movie=None)
      elif(rtype=="movie_type"):
        sql = "SELECT * FROM MOVIE WHERE MovieType= %s"
        rows_count = cursor.execute(sql,ktype)
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info,recommend_movie=None)
      else:
        sql = "SELECT * FROM movie"
        rows_count = cursor.execute(sql)
        if rows_count > 0 :
            movie_info = cursor.fetchall()
        else:
            movie_info=None
        return render_template('movies.html',movies=movie_info,recommend_movie=recommend_movie)

    

@app.route('/mypage')
def mypage():
    user_id=session['user']
    sql = "SELECT * FROM customer WHERE CustomerID= %s"
    cursor.execute(sql,user_id)
    user_info = cursor.fetchone()

    sql2 = "SELECT * FROM account where CustomerID=%s and PlanExpiredDate > NOW()"
    cursor.execute(sql2,user_id)
    account_info = cursor.fetchall()

    sql3 = "SELECT * FROM moviequeue as mq JOIN movie as m on mq.MovieID=m.MovieID WHERE CustomerID=%s; "
    cursor.execute(sql3,user_id)
    queue_info = cursor.fetchall()

    sql4="SELECT * FROM Orders as mq JOIN movie as m on mq.MovieID= m.MovieID WHERE CustomerID=%s and holding=1;"
    cursor.execute(sql4,user_id)
    order_info = cursor.fetchall()
    
    return render_template('mypage.html',user_info=user_info,account_info=account_info,queue_info=queue_info,order_info=order_info)

@app.route('/logout') 
def logout(): 
    session.pop('user', None) 
    return redirect('/')

# 추가
@app.route('/login', methods=['POST','GET'])
def about():
    if request.method == 'POST':
        login_info = request.form
        print(login_info)
        EmailAddress = login_info['email']
        Passwd = login_info['passwd']
        sql = "SELECT * FROM customer WHERE EmailAddress=%s"
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
        sql="INSERT INTO customer (EmailAddress,Passwd,FirstName,LastName) VALUES (%s,%s,%s,%s);"
        cursor.execute(sql,(EmailAddress,Passwd,FirstName,LastName))
        db.commit()
        return redirect('login')
    return render_template('signup.html')