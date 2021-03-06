from flask import Blueprint, render_template, session, request, url_for, redirect, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_required, current_user
from ..Models.models import *
import time
from random import uniform
from ..configurations import *
from werkzeug.utils import secure_filename
from .test_Parkinson import *
from datetime import datetime

user = Blueprint('user', __name__,template_folder='user_templates',static_folder='user_static',url_prefix='/User')

def save(encoded_data, filename):
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return cv2.imwrite(filename, img)

@user.route('/user_homepage')
@login_required
# @roles_required('User')
def user_homepage():
    return render_template('user_index.html', name=current_user.username)

@user.route('/add_details', methods=["GET", "POST"])
def user_details():
    if request.method == "POST":
        place_id = request.form.get("slct_place")
        gender = request.form.get("rdb_gender")
        age = request.form.get("txt_age")
        address = request.form.get("txt_address")
        contact = request.form.get("txt_contact")
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file_name, file_ext = os.path.splitext(file.filename)
            new_filename = file_name + time.strftime("%Y-%I-%M-%S") + str(uniform(0, 1000)).zfill(5) + file_ext
            file.filename = new_filename
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        add_details = User_details(place_id=place_id, gender=gender, age=age, user_id=current_user.id, address=address, contact=contact, image=file.filename)
        db.session.add(add_details)
        db.session.commit()
    districts = District.query.all()
    return render_template("user_details.html", districts=districts, name=current_user.username)
    # return redirect(url_for("user.user_homepage"))

@user.route('/ajaxPlace/<did>')
def ajaxPlace(did):
    places = Place.query.filter_by(district_id=did).join(District).all()
    return render_template("Ajaxplace.html", places=places)



@user.route('/editProfile', methods=["GET", "POST"])
def userEditProfile():
    if request.method == "POST":
        new_filename = ""
        name = request.form.get("txt_name")
        email = request.form.get("txt_email")
        district = request.form.get("slct_district")
        place = request.form.get("slct_place")
        gender = request.form.get("rdb_gender")
        age = request.form.get("txt_age")
        address = request.form.get("txt_address")
        contact = request.form.get("txt_contact")
        file = request.files['file']
        print(request.files)
        if file.filename != "":
            if file and allowed_file(file.filename):
                file_name, file_ext = os.path.splitext(file.filename)
                new_filename = file_name + time.strftime("-%Y-%I-%M-%S-") + str(uniform(0, 1000)).zfill(5) + file_ext
                file.filename = new_filename
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        else:
            print("hai")
            new_filename = request.form.get("hfile")
        
        update_user = Users.query.filter_by(id=current_user.id).first()
        update_user.username = name
        update_user.email = email
        db.session.commit()
        update_useDetails = User_details.query.filter_by(user_id=current_user.id).first()
        update_useDetails.place_id = place
        update_useDetails.gender = gender
        update_useDetails.age = age
        update_useDetails.address = address
        update_useDetails.contact = contact
        update_useDetails.image = new_filename
        db.session.commit()
        return redirect(url_for("user.userEditProfile"))
        
    user = Users.query.filter_by(id=current_user.id).first()
    user_details = User_details.query.join(Place, Place.id==User_details.place_id).join(District, District.id==Place.district_id).add_columns(Place.id, District.id, Place.place_name, District.district_name).filter(User_details.user_id==current_user.id).first()
    district = District.query.all()
    places = Place.query.filter(Place.id==User_details.place_id).all()
    return render_template("user_edit_profile.html", user=user, user_details=user_details, districts=district, places=places)

@user.route('/test_parkinson', methods=["GET", "POST"])
def test_parkinson():
    return render_template("user_test.html",name=current_user.username)

@user.route('testForParkinson', methods=["POST"])
def testForParkinson():
    if request.method == "POST":
        data = request.get_json()['base64']
        # print(data)
        TEST_IMAGE_STORAGE = os.path.join(USER_DIR, "Test_Image_Storage")
        if not os.path.exists(TEST_IMAGE_STORAGE):
            os.mkdir(TEST_IMAGE_STORAGE)
        timestamp = datetime.now()
        ts = timestamp.strftime("%d-%m-%Y-%I-%M-%S-%p")
        file_name = str(current_user.id) + "-" + current_user.username + "-" + str(ts) + ".png"
        file_name = os.path.join(TEST_IMAGE_STORAGE, file_name)
        print(file_name)
        save(data.split(',')[1], file_name)
        test_result = check_parkinson(data)
        add_result = Test_results(user_id=current_user.id, test_img_name=file_name.split(os.path.sep)[-1],
                                test_result=test_result['result'])
        db.session.add(add_result)
        db.session.commit()
        return jsonify(test_result)

@user.route('/book_doctor', methods=["GET", "POST"])
def book_doctor():
    doctors = db.engine.execute('select * from doctor_details as dd inner join users u inner join user_roles ur on dd.doctor_id = u.id and u.id = ur.role_id where ur.role_id=1')
    # for doctor in doctors:
    #     print(doctor)
    return render_template("book_doctor.html",name=current_user.username, doctors=doctors)