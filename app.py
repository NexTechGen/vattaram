from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key or use os.environ

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MongoDB Atlas Connection
client = MongoClient('mongodb+srv://UOJvattaram:UOJ2023et@cluster0.qxvkvqt.mongodb.net/?retryWrites=true&w=majority&connectTimeoutMS=50000&socketTimeoutMS=50000&serverSelectionTimeoutMS=50000')
db = client['vattaram']
collection = db['weare']
fs = gridfs.GridFS(db)

# User class
class User(UserMixin):
    def __init__(self, id):
        self.id = str(id)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    try:
        user = collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user['_id'])
    except:
        return None

@app.route('/')
def index():
    students = list(collection.find())

    # Sort students based on last 3 digits of reg_no
    def get_last_digits(student):
        try:
            return int(student['reg_no'].split('/')[-1])
        except:
            return 0  # fallback if reg_no is malformed

    students.sort(key=get_last_digits)
    return render_template('index.html', students=students)


@app.route('/upload', methods=['POST'])
def upload():
    fname = request.form['full-name']
    reg_no = request.form['reg_no']
    phone = request.form['phone']
    address = request.form['address']
    link = request.form['location_link']
    image = request.files['image']

    # Check for duplicate registration number
    existing_user = collection.find_one({'reg_no': reg_no})
    if existing_user:
        flash('Registration number already exists.', 'warning')
        return redirect(url_for('index'))

    img_name = f"{fname.lower()}_{datetime.datetime.now().strftime('%Y%m%d')}"
    image_id = fs.put(image, filename=img_name, content_type=image.content_type)

    student = {
        "name": fname,
        "reg_no": reg_no,
        "phone": phone,
        "address": address,
        "loc_url": link,
        "image_id": image_id,
        "password": generate_password_hash("FOT2023ET"),
        "created_at": datetime.datetime.utcnow()
    }

    collection.insert_one(student)
    flash('Student uploaded successfully. Default password is "FOT2023ET".', 'success')
    return redirect(url_for('index'))

@app.route('/image/<image_id>')
def get_image(image_id):
    file = fs.get(ObjectId(image_id))
    response = make_response(file.read())
    response.headers.set('Content-Type', file.content_type)
    response.headers.set('Cache-Control', 'public, max-age=86400')
    return response

@app.route('/update/<student_id>', methods=['GET', 'POST'])
@login_required
def update(student_id):
    student = collection.find_one({"_id": ObjectId(student_id)})

    if request.method == 'POST':
        fname = request.form['full-name']
        reg_no = request.form['reg_no']
        phone = request.form['phone']
        address = request.form['address']
        link = request.form['location_link']

        updated_data = {
            "name": fname,
            "reg_no": reg_no,
            "phone": phone,
            "address": address,
            "loc_url": link,
        }

        # Handle image update
        if 'image' in request.files and request.files['image'].filename:
            if 'image_id' in student:
                fs.delete(student['image_id'])

            image = request.files['image']
            img_name = f"{fname.lower()}_{datetime.datetime.now().strftime('%Y%m%d')}"
            new_image_id = fs.put(image, filename=img_name, content_type=image.content_type)
            updated_data['image_id'] = new_image_id
        else:
            updated_data['image_id'] = student.get('image_id')

        collection.update_one({"_id": ObjectId(student_id)}, {"$set": updated_data})
        flash('Student information updated successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('update.html', student=student)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        reg_no = request.form['reg_no']
        password = request.form['password']
        
        user = collection.find_one({"reg_no": reg_no})

        if user and check_password_hash(user['password'], password):
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('update', student_id=user['_id']))
        else:
            flash('Invalid registration number or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_pw = generate_password_hash(new_password)
        collection.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"password": hashed_pw}})
        flash('Password updated successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('change_password.html')

if __name__ == '__main__':
    app.run(debug=True)
