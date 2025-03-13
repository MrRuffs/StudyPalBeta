from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from together import Together
from dotenv import load_dotenv
from flask_cors import CORS
import uuid

load_dotenv()


app = Flask(__name__)
CORS(app)  # Allow frontend requests
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

client = Together(api_key=os.getenv('API_KEY'))

def generate_flashcards(topic, quantity):
    prompt = f"Generate {quantity} flashcards for me on the topic of '{topic}'. Return only a Python 2D list where each sublist contains a question and its answer, with no extra text."
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def decode_token(token):
    try:
        # Decode the token using the secret key
        decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired!")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token!")

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/generate-flashcards-page")
def generate_flashcards_page():
    return render_template("generate_flashcards.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sign-up")
def sign_up():
    return render_template("sign_up.html")

@app.route("/sign-up-api", methods=["POST"])
def register_user():
    data = request.get_json()
    name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'message': 'All fields are required!'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists!'}), 409
    
    if User.query.filter_by(name=name).first():
        return jsonify({'message': 'Username already exists!'}), 409
    
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route("/login-api", methods=["POST"])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'All fields are required!'}), 400
    
    user = User.query.filter_by(name=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    access_token = create_access_token(identity={'email': user.email})
    return jsonify({'access_token': access_token}), 200

@app.route('/home')
def home():
    return render_template("home.html")

@app.route("/generate-flashcards", methods=["POST"])
def generate_flashcards_route():
    data = request.json
    topic = data.get("topic")
    quantity = int(data.get("amount"))

    if not topic or not quantity:
        return jsonify({"error": "Missing topic or amount."}, 400)
    
    try:
        flashcards = generate_flashcards(topic, int(quantity))
        return jsonify({"flashcards": flashcards})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/init-db")
def init_db():
    db.create_all()
    return "Database initialized!"

@app.route("/show-users")
def show_users():
    users = User.query.all()
    user_list = [{"name": user.name, "email": user.email} for user in users]
    return jsonify(user_list)

@app.route("/get-username", methods=["POST"])
def get_username():
    token = request.json.get('token')
    if not token:
        return jsonify({"message": "Token is missing!"}), 400
    
    try:
        decoded_token = decode_token(token)
        email = decoded_token['sub']['email']
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"username": user.name}), 200
        else:
            return jsonify({"message": "User not found!"}), 404
    except Exception as e:
        return jsonify({"message": "Invalid token!"}), 401


if __name__ == '__main__':
    app.run(debug=True)