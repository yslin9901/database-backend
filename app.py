from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager,UserMixin,login_user,current_user
from flask_migrate import Migrate
import json

# Create Flask app
app = Flask(__name__)

# Make the api can be access from anywhere
CORS(app)

# Set secret key for sessions
app.config['SECRET_KEY'] = 'secret'

# Make json output prettier
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Set the database uri
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"

# Disable Track to elimate warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create database instance, which will reference the above database uri
db = SQLAlchemy(app)

# Create migration tools to easy manage db by using
# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade
migrate = Migrate(app, db)

# Create loginmanager instance to easy manage login
login_manager = LoginManager()
login_manager.init_app(app)

# User Table
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120))
    def __init__(self, name, password):
        self.username = username
        self.password = password
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def __repr__(self):
        return '<UserModel %r>' % (self.name)

# Response wrapper
def error(msg):
    return jsonify({
        'error': True,
        'msg': msg
    })
def success(data):
    return jsonify({
        'error': False,
        'data': data
    })

# For Login Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Flask routes
@app.route('/')
def index():
    return 'This is Backend.'

@app.route('/login',methods=['GET','POST'])
def login():
    if request.values.get('username') == None or request.values.get('password') == None:
        return error('Empty Filed!')
    else:
        username = request.values.get('username')
        password = request.values.get('password')
    
    user = User.query.filter_by(username=username,password=password).first()
    if user != None:
        login_user(user)
        return success({'username':user.username})
    else:
        return error('Invalid Credential!')

@app.route('/userinfo',methods=['GET','POST'])
def userinfo():
    return success({'username':current_user.username})
@app.route('/register',methods=['GET','POST'])
def register():
    if request.values.get('username') == None or request.values.get('password') == None:
        return error('Empty Filed!')
    else:
        username = request.values.get('username')
        password = request.values.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user == None:
        try:
            user = User(username,password)
            user.save_to_db()
            return success({'username':user.username})
        except:
            return error('Database Error!')
    else:
        return error('Name Exists!')
    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000,threaded=True)
    

