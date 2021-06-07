import os
from re import search
from flask import Flask
from flask import render_template, request, redirect,url_for,jsonify, make_response,session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue
from marshmallow import Schema, fields
from requests import get





import platform
import datetime
import hashlib
import urllib.request
import urllib

db = SQLAlchemy()

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_URI = "sqlite:///" + os.path.join(BASE_DIR, "files.db")

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "GDtfDCFYjD"
app.config["FILE_UPLOADS_WINDOWS"] = "C:\SGDF"
app.config["FILE_UPLOADS_LINUX"] = "/opt/SGDF"

db = SQLAlchemy(app)
jsglue = JSGlue(app)

class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
        username = db.Column(db.String(50), nullable=False)
        email = db.Column(db.String(50), nullable=False, unique=True)
        password = db.Column(db.Text, nullable=False)

class Admin(db.Model):
        id = db.Column(db.Integer, primary_key=True)


class File(db.Model):
        
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(50), nullable=False)
        owner = db.Column(db.Integer, db.ForeignKey('user.id'))
        date = db.Column(db.DateTime, index=True)
        size = db.Column(db.Integer)
        hash = db.Column(db.Integer)
        downloadable = db.Column(db.Boolean, nullable=False)
        removable = db.Column(db.Boolean, nullable=False)

class UserSchema(Schema):
        id = fields.Int()
        admin_id = fields.Int()
        username = fields.Str()
        email = fields.Str()
        password = fields.Str()

db.create_all()


@app.route("/api/v1/")
def index():
     return render_template("index.html")

@app.route("/api/v1/login")
def user_login():
     return render_template("public/login.html")


@app.route("/api/v1/user/dashboard", methods=["GET"])
def dashboard():

    if request.method == "GET":

        user_email = request.args.get("email")
        print("email:{}".format(user_email))
        session['USER-LOGIN'] = user_email


        user_id = request.args.get("user_id")

        res = get("http://localhost:5000/api/v1/user/{}/files/".format(user_id)).json()

        print(res["message"])
        print(res["files"])
        files = res["files"]

    return render_template("user/dashboard.html", files=files)


@app.route("/api/v1/admin/dashboard", methods=["GET"])
def admin_dashboard():

    if request.method == "GET":

        user_email = request.args.get("email")
        print("email:{}".format(user_email))
        session['USER-LOGIN'] = user_email



        user_id = request.args.get("user_id")

        res = get("http://localhost:5000/api/v1/user/{}/files/".format(user_id)).json()

        print(res["message"])
        print(res["files"])
        files = res["files"]

    return render_template("admin/admin_dashboard.html", files=files)



"""POST"""
@app.route("/api/v1/auth/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        search_user = User.query.filter_by(email=request.form["email"]).first()

        if search_user.admin_id == 0:
            logged_user_dict = {
                "id" : search_user.id,
                "admin_id" : 0,
                "username":search_user.username,
                "email":search_user.email,
                "password":search_user.password
            }

            return redirect(url_for("get_user", user_id = logged_user_dict["id"]))

        else:
            search_admin = Admin.query.filter_by(id=search_user.admin_id).first()
            logged_user_dict = {
                "id" : search_user.id,
                "admin_id" : search_admin.id,
                "username":search_user.username,
                "email":search_user.email,
                "password":search_user.password
            }
    
            return redirect(url_for("get_user", user_id = logged_user_dict["id"]))

            

    return redirect(url_for('login'))
        

"""POST"""
@app.route("/api/v1/auth/register", methods=["POST"])
def register():

    if request.method == "POST":
    
        if request.form["password"] == "root":
            new_admin = Admin()
            db.session.add(new_admin)
            db.session.commit()

            admin_dict = dict(id=new_admin.id)
            new_user = User(admin_id=new_admin.id,username=request.form["username"], email=request.form["email"], password=request.form["password"])

            print("email: {}".format(new_user.email))

            db.session.add(new_user)
            db.session.commit()

            user_dict = dict(id=new_user.id, admin_id=new_user.admin_id, username=new_user.username, email=new_user.email, password=new_user.password)


            res = make_response(render_template("admin/admin_dashboard.html"))
            res.set_cookie('cookie-user-id', user_dict["email"])
            return res
    
        else:
            new_user = User(admin_id=0,username=request.form["username"], email=request.form["email"], password=request.form["password"])

            db.session.add(new_user)
            db.session.commit()

            user_dict = dict(id=new_user.id, admin_id=new_user.admin_id, username=new_user.username, email=new_user.email, password=new_user.password)

            res = make_response(render_template("user/dashboard.html"))
            res.set_cookie('cookie-user-id', user_dict["email"])
            return res
        

    
    return redirect(url_for('register'))


"""POST"""

@app.route("/api/v1/user/<int:user_id>", methods=["POST"])
def post_user(user_id):
    
    if request.method == "POST":
        search_user = User.query.filter_by(id=user_id).first();
        search_file = File.query.filter_by(owner=user_id).all()

        print('serch_user: {}'.format(search_user))
        print('serch_file: {}'.format(search_file))

        search_user_dict = dict(id=search_user.id, admin_id=search_user.admin_id, username=search_user.username, email=search_user.email, password=search_user.password)

        if search_file:
            
            global i
            filesList = []
            files = File.query.all()
            max = len(files)-1

            for i in range(0,len(files)):
                    filesList.append(
                    {
                        'id':files[i].id,
                        'filename':files[i].filename,
                        'owner': files[i].owner,
                        'date':files[i].date,
                        'size':files[i].size,
                        'hash':files[i].hash,
                        'downloadable':files[i].downloadable,
                        'removable':files[i].removable

                        }
                )
    
            if i == max:
                search_file_dict = filesList

            res = make_response(jsonify({"message": "OK", "data": [search_user_dict, search_file_dict]}), 200)
        else:
            res = make_response(jsonify({"message": "OK", "data": [search_user_dict]}), 200)


        return res;

    return make_response(jsonify({"message": "Method not allowed"}), 405)


"""POST"""
@app.route("/api/v1/user/upload-file",methods=["POST"])  
def upload_file():

    if request.method == "POST":

        print('metodo...........')
        print(request.method)

        print('llamando a upload file....')

        user_email = request.cookies.get("cookie-user-id")
        

        if not user_email:
            user_email = session.get('USER-LOGIN')
            print('1')
            print(user_email)
            search_user = User.query.filter_by(email=user_email).first()
            stored_user_dict = dict(id=search_user.id, admin_id=search_user.admin_id, username=search_user.username, email=user_email, password=search_user.password)
        else:
            user_email = request.cookies.get("cookie-user-id")
            print('2')
            print(user_email)
            search_user = User.query.filter_by(email=user_email).first()
            stored_user_dict = dict(id=search_user.id, admin_id=search_user.admin_id, username=search_user.username, email=search_user.email, password=search_user.password)


        if platform.system() == "Windows":
            file_dir = app.config["FILE_UPLOADS_WINDOWS"]
        else:
            file_dir = app.config["FILE_UPLOADS_LINUX"]
        
        file =  request.files["file"]
        filename = file.filename
        file_hash = hashlib.md5(file.read()).hexdigest()
        file_upload_date = datetime.datetime.now()
        file_size = file.tell()/1024


            

        if stored_user_dict["admin_id"] == 0:

                if file:

                    file.save(os.path.join(file_dir, file.filename))
                    print('file saved in directory .....................')

                    file_dict = dict(filename=filename, owner=stored_user_dict["id"],date=file_upload_date,
                    size=file_size,hash=file_hash,downloadable=True, removable=False)

                

                    print('ejecutando respuesta.................')


                    new_file = File(filename=file_dict["filename"], owner=file_dict["owner"], date=file_dict["date"],
                    size=file_dict["size"], hash=file_dict["hash"], downloadable=file_dict["downloadable"], removable=file_dict["removable"])


                    db.session.add(new_file)
                    db.session.commit()

                    
                    files = File.query.filter_by(owner=file_dict["owner"]).all()

                    print(files)


                    return redirect(url_for('dashboard', email=stored_user_dict["email"],user_id=stored_user_dict["id"], **request.args))

                else:
                    return redirect(url_for('dashboard', email=stored_user_dict["email"],user_id=stored_user_dict["id"], **request.args))

        else:

                if file:
                
                    file.save(os.path.join(file_dir, file.filename))
                    print('file saved in directory .....................')


                    file_dict = dict(filename=filename, owner=stored_user_dict["id"],date=file_upload_date,
                    size=file_size,hash=file_hash,downloadable=True, removable=True)

                

                    print('ejecutando respuesta.................')


                    new_file = File(filename=file_dict["filename"], owner=file_dict["owner"], date=file_dict["date"],
                    size=file_dict["size"], hash=file_dict["hash"], downloadable=file_dict["downloadable"], removable=file_dict["removable"])


                    db.session.add(new_file)
                    db.session.commit()

                    
                    files = File.query.filter_by(owner=file_dict["owner"]).all()

                    print(files)

                    return redirect(url_for('admin_dashboard', email=stored_user_dict["email"],user_id=stored_user_dict["id"], **request.args))   

                else:
                    return redirect(url_for('admin_dashboard', email=stored_user_dict["email"],user_id=stored_user_dict["id"], **request.args))


    return redirect(url_for())
    

"""GET"""
@app.route("/api/v1/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    
    search_user = User.query.filter_by(id=user_id).first()

    stored_user_dict = dict(id=search_user.id, admin_id=search_user.admin_id, username=search_user.username, email=search_user.email, password=search_user.password)

    print("stored_user_dict:{}".format(stored_user_dict["email"]))

    return make_response(jsonify({"message":"OK", "stored_user_dict": stored_user_dict},200))
    
"""GET"""
@app.route("/api/v1/user/<path:user_email>", methods=["GET"])
def get_user_by_email(user_email):

    print(urllib.request.unquote(request.url))

    search_user = User.query.filter_by(email=user_email).first()

    stored_user_dict = dict(id=search_user.id, admin_id=search_user.admin_id, username=search_user.username, email=search_user.email, password=search_user.password)

    return make_response(jsonify({"message":"OK", "stored_user_dict": stored_user_dict},200))

"""GET"""
@app.route("/api/v1/users", methods=["GET"])
def get_users():


   global i
   usersList = []
   users = User.query.all()
   max = len(users)-1
   

   for i in range(0,len(users)):
        usersList.append(
           {
            'id':users[i].id,
            'admin_id':users[i].admin_id,
            'username': users[i].username,
            'email':users[i].email,
            'password':users[i].password
            }
       )
    
   if i == max:
      return jsonify(usersList)


"""GET"""
@app.route('/get-cookie/')
def get_cookie():
    user_id = request.cookies.get('cookie-user-id')
    res = make_response({"message": "OK", "stored-cookie":user_id}, 200)
    return res


"""GET"""
@app.route("/api/v1/get-files", methods=["GET"])
def get_all_files():


   global i
   filesList = []
   files = File.query.all()
   max = len(files)-1

   for i in range(0,len(files)):
        filesList.append(
           {
            'id':files[i].id,
            'filename':files[i].filename,
            'owner': files[i].owner,
            'date':files[i].date,
            'size':files[i].size,
            'hash':files[i].hash,
            'downloadable':files[i].downloadable,
            'removable':files[i].removable

            }
       )
    
   if i == max:
      return jsonify(filesList)


"""GET"""
@app.route("/api/v1/user/<int:user_id>/files/", methods=["GET"])
def get_files(user_id):

   global i
   filesList = list()
   files = File.query.filter_by(owner=user_id).all()
   max = len(files)-1

   if not files:
        return make_response(jsonify({"message":"NO FILES", "files" : filesList}))
   else:
            for i in range(0,len(files)):
                    filesList.append(
                    {
                        'id':files[i].id,
                        'filename':files[i].filename,
                        'owner': files[i].owner,
                        'date':files[i].date,
                        'size':files[i].size,
                        'hash':files[i].hash,
                        'downloadable':files[i].downloadable,
                        'removable':files[i].removable

                        }
                )
            
            if i == max:
               return make_response(jsonify({"message":"OK", "files" : filesList}))
    

"""GET"""
@app.route("/api/v1/user/<int:user_id>/files/<int:file_id>", methods=["GET"])
def get_file(user_id, file_id):
    search_user = User.query.filter_by(id=user_id).first()
    stored_file = File.query.filter_by(id=file_id, owner=search_user.id).first()

    file_id_dict = dict(id=stored_file.id, filename=stored_file.filename, owner=stored_file.owner, date=stored_file.date,
    size=stored_file.size,hash=stored_file.hash,downloadable=stored_file.downloadable,removable=stored_file.removable)

    return jsonify(file_id_dict)


"""GET"""
@app.route("/api/v1/user/files/<string:filename>/download", methods=["GET"])
def download_file(filename):
    print('downloading file...{}'.format(filename))
    return send_from_directory(app.config['FILE_UPLOADS_WINDOWS'], path=filename, as_attachment=True)


"""GET"""
@app.route("/api/v1/user/files/<int:file_id>/delete", methods=["GET"])
def delete_file(file_id):

    print('file id: {}'.format(file_id))

    file_to_be_deleted =  File.query.filter_by(id=file_id).first()

    user_id = file_to_be_deleted.owner

    user_who_is_deleting = User.query.filter_by(id=user_id).first()

    db.session.delete(file_to_be_deleted)
    db.session.commit()

    
    print('file deleted!')

    

    email = user_who_is_deleting.email
    user_id = user_who_is_deleting.id

    return redirect(url_for('admin_dashboard', email=email,user_id=user_id, **request.args))


@app.route('/logout')
def logout():
    session.pop('USER-LOGIN',None)
    res = make_response(render_template("index.html"))
    res.set_cookie('cookie-user-id', '', expires=0)
    res.delete_cookie('cookie-user-id')
    return res



