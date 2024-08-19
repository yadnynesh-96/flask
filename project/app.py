from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Paths to Excel files
students_excel_file = 'students.xlsx'
admins_excel_file = 'admins.xlsx'
home_decore_excel_file = 'Home_Decore.xlsx'
batch_mentor_excel_file = 'Batch_Mentor.xlsx'

# Ensure the Excel files exist
if not os.path.exists(students_excel_file):
    df_students = pd.DataFrame(columns=[
        'Sr. No.', 'batch', 'name', 'mobile', 'email', 'password', 'designation', 'company',
        'address', 'district', 'subdivision', 'pin', 'areawise', 'country', 'sector',
        'international', 'domestic', 'linkedin', 'facebook', 'instagram', 'profile_pic'
    ])
    df_students.to_excel(students_excel_file, index=False)

if not os.path.exists(admins_excel_file):
    df_admins = pd.DataFrame(columns=['name', 'email', 'password', 'post'])
    df_admins.to_excel(admins_excel_file, index=False)


if not os.path.exists(home_decore_excel_file):
    df = pd.DataFrame(columns=['Sr. No.', 'Image', 'Heading', 'Description', 'Date'])
    df.to_excel(home_decore_excel_file, index=False)

if not os.path.exists(batch_mentor_excel_file):
    df_batch_mentor = pd.DataFrame(columns=['Sr. No.', 'Full Name', 'E-Mail', 'Contact No.', 'Password', 'Batch Assigned'])
    df_batch_mentor.to_excel(batch_mentor_excel_file, index=False)
    
# Ensure the static/images directory exists
image_dir = os.path.join('static', 'images')
os.makedirs(image_dir, exist_ok=True)

    
@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/Contact')
def Contact():
    return render_template('Contact-us.html')

@app.route('/About')
def About():
    return render_template('About-us.html')

@app.route('/')
def home():
    # Load the Excel file
    df = pd.read_excel(home_decore_excel_file)

    # Retrieve the latest three entries
    latest_entries = df.sort_values(by='Sr. No.', ascending=False).head(3) if not df.empty else pd.DataFrame()

    return render_template('home.html', latest_entries=latest_entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        df = pd.read_excel(students_excel_file)
        user = df[(df['email'] == email) & (df['password'] == password)]
        if not user.empty:
            session['user'] = user.to_dict('records')[0]
            session['edit_mode'] = False
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        df = pd.read_excel(students_excel_file)
        sr_no = len(df) + 1

        data = {
            'Sr. No.': sr_no,
            'batch': request.form['batch'],
            'name': request.form['name'],
            'mobile': request.form['mobile'],
            'email': request.form['email'],
            'password': request.form['password'],
            'designation': request.form['designation'],
            'company': request.form['company'],
            'address': request.form['address'],
            'district': request.form['district'],
            'subdivision': request.form['subdivision'],
            'pin': request.form['pin'],
            'areawise': request.form['areawise'],
            'country': request.form['country'],
            'sector': request.form['sector'],
            'international': request.form['international'],
            'domestic': request.form['domestic'],
            'linkedin': request.form['linkedin'],
            'facebook': request.form['facebook'],
            'instagram': request.form['instagram'],
            'profile_pic': None  # To be handled in file upload
        }
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filepath = os.path.join(image_dir, file.filename)
                file.save(filepath)
                data['profile_pic'] = f'images/{file.filename}'

        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel(students_excel_file, index=False)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'edit' in request.form:
            session['edit_mode'] = not session.get('edit_mode', False)
        else:
            try:
                email = session['user']['email']
                df = pd.read_excel(students_excel_file)

                new_data = {
                    'batch': request.form.get('batch', session['user']['batch']),
                    'name': request.form.get('name', session['user']['name']),
                    'mobile': request.form.get('mobile', session['user']['mobile']),
                    'password': request.form.get('password', session['user']['password']),
                    'designation': request.form.get('designation', session['user']['designation']),
                    'company': request.form.get('company', session['user']['company']),
                    'address': request.form.get('address', session['user']['address']),
                    'district': request.form.get('district', session['user']['district']),
                    'subdivision': request.form.get('subdivision', session['user']['subdivision']),
                    'pin': request.form.get('pin', session['user']['pin']),
                    'areawise': request.form.get('areawise', session['user']['areawise']),
                    'country': request.form.get('country', session['user']['country']),
                    'sector': request.form.get('sector', session['user']['sector']),
                    'international': request.form.get('international', session['user']['international']),
                    'domestic': request.form.get('domestic', session['user']['domestic']),
                    'linkedin': request.form.get('linkedin', session['user']['linkedin']),
                    'facebook': request.form.get('facebook', session['user']['facebook']),
                    'instagram': request.form.get('instagram', session['user']['instagram']),
                    'profile_pic': session['user']['profile_pic']  # Preserve existing profile pic
                }

                # Handle profile picture upload
                if 'profile_pic' in request.files:
                    file = request.files['profile_pic']
                    if file.filename != '':
                        filepath = os.path.join(image_dir, file.filename)
                        file.save(filepath)
                        new_data['profile_pic'] = f'images/{file.filename}'

                df.update(pd.DataFrame([new_data], index=[df[df['email'] == email].index[0]]))
                df.to_excel(students_excel_file, index=False)

                session['user'] = new_data
                session['edit_mode'] = False
                flash('Profile updated successfully!')
            except KeyError:
                flash('An error occurred: Email not found in session.')
                return redirect(url_for('login'))

    return render_template('profile.html', user=session['user'], edit_mode=session.get('edit_mode', False))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('edit_mode', None)
    return redirect(url_for('home'))

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'password': request.form['password'],
            'post': request.form['post']
        }
        df = pd.read_excel(admins_excel_file)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel(admins_excel_file, index=False)
        flash('Admin registration successful! Please log in.')
        return redirect(url_for('admin_login'))
    return render_template('admin_signup.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        df = pd.read_excel(admins_excel_file)
        admin = df[(df['email'] == email) & (df['password'] == password)]
        if not admin.empty:
            session['admin'] = admin.to_dict('records')[0]
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('admin_login.html')


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    df_students = pd.read_excel(students_excel_file)
    
    
    if request.method == 'POST':
        if 'delete' in request.form:
            email_to_delete = request.form.get('email')
            if email_to_delete:
                df_students = df_students[df_students['email'] != email_to_delete]
                df_students.to_excel(students_excel_file, index=False)
                flash('Student record deleted successfully!')
                return redirect(url_for('admin_dashboard'))
        elif 'edit' in request.form:
            email_to_edit = request.form.get('email')
            if email_to_edit:
                student = df_students[df_students['email'] == email_to_edit]
                if not student.empty:
                    student = student.iloc[0].to_dict()
                    return render_template('admin_edit.html', student=student)
                else:
                    flash('Student not found!')
                    return redirect(url_for('admin_dashboard'))
        elif 'search' in request.form:
            search_query = request.form.get('search')
            search_column = request.form.get('search_column')
            if search_query and search_column:
                if search_column in df_students.columns:
                    df_students = df_students[df_students[search_column].astype(str).str.contains(search_query, case=False, na=False)]
                else:
                    flash('Invalid search column!')
            df_students = df_students.sort_values(by='name')

    students = df_students.to_dict(orient='records')

    admin = session['admin']  # Assuming admin details are stored in session

    return render_template('admin_dashboard.html', students=students, admin=admin)


@app.route('/admin/edit', methods=['POST'])
def admin_edit():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    email = request.form['email']
    df_students = pd.read_excel(students_excel_file)
    index = df_students[df_students['email'] == email].index[0]

    df_students.at[index, 'batch'] = request.form.get('batch', df_students.at[index, 'batch'])
    df_students.at[index, 'name'] = request.form.get('name', df_students.at[index, 'name'])
    df_students.at[index, 'mobile'] = request.form.get('mobile', df_students.at[index, 'mobile'])
    df_students.at[index, 'password'] = request.form.get('password', df_students.at[index, 'password'])
    df_students.at[index, 'designation'] = request.form.get('designation', df_students.at[index, 'designation'])
    df_students.at[index, 'company'] = request.form.get('company', df_students.at[index, 'company'])
    df_students.at[index, 'address'] = request.form.get('address', df_students.at[index, 'address'])
    df_students.at[index, 'district'] = request.form.get('district', df_students.at[index, 'district'])
    df_students.at[index, 'subdivision'] = request.form.get('subdivision', df_students.at[index, 'subdivision'])
    df_students.at[index, 'pin'] = request.form.get('pin', df_students.at[index, 'pin'])
    df_students.at[index, 'areawise'] = request.form.get('areawise', df_students.at[index, 'areawise'])
    df_students.at[index, 'country'] = request.form.get('country', df_students.at[index, 'country'])
    df_students.at[index, 'sector'] = request.form.get('sector', df_students.at[index, 'sector'])
    df_students.at[index, 'international'] = request.form.get('international', df_students.at[index, 'international'])
    df_students.at[index, 'domestic'] = request.form.get('domestic', df_students.at[index, 'domestic'])
    df_students.at[index, 'linkedin'] = request.form.get('linkedin', df_students.at[index, 'linkedin'])
    df_students.at[index, 'facebook'] = request.form.get('facebook', df_students.at[index, 'facebook'])
    df_students.at[index, 'instagram'] = request.form.get('instagram', df_students.at[index, 'instagram'])

    # Handle profile picture upload
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            filepath = os.path.join(image_dir, file.filename)
            file.save(filepath)
            df_students.at[index, 'profile_pic'] = f'images/{file.filename}'

    df_students.to_excel(students_excel_file, index=False)
    flash('Student record updated successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)  # Remove the admin from the session
    flash('You have been logged out.')
    return redirect(url_for('admin_login'))

    

@app.route('/admin/home_decor', methods=['GET', 'POST'])
def admin_home_decor():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Define the directory for image uploads
    image_dir = os.path.join('static', 'images')

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    df = pd.read_excel(home_decore_excel_file)

    if request.method == 'POST':
        image = request.files['image']
        heading = request.form['heading']
        description = request.form['description']
        date = request.form['date']

        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(image_dir, image_filename))
        else:
            image_filename = ''

        next_sr_no = df['Sr. No.'].max() + 1 if not df.empty else 1

        new_entry = pd.DataFrame([{
            'Sr. No.': next_sr_no,
            'Image': image_filename,
            'Heading': heading,
            'Description': description,
            'Date': date
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(home_decore_excel_file, index=False)

        flash('Entry added successfully!')
        return redirect(url_for('admin_home_decor'))

    latest_entries = df.sort_values(by='Sr. No.', ascending=False).head(3) if not df.empty else pd.DataFrame()

    return render_template('admin_home_decor.html', latest_entries=latest_entries)

# Batch Mentor Signup
@app.route('/admin/add_batch_mentor', methods=['GET', 'POST'])
def add_batch_mentor():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        df = pd.read_excel(batch_mentor_excel_file)
        sr_no = len(df) + 1
        data = {
            'Sr. No.': sr_no,
            'Full Name': request.form['full_name'],
            'E-Mail': request.form['email'],
            'Contact No.': request.form['contact_no'],
            'Password': request.form['password'],
            'Batch Assigned': request.form['batch_assigned'],
        }
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel(batch_mentor_excel_file, index=False)
        flash('Batch Mentor registration successful!')
        return redirect(url_for('admin_dashboard'))
    return render_template('batch_mentor_signup.html')

@app.route('/batch_mentor/login', methods=['GET', 'POST'])
def batch_mentor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        df = pd.read_excel(batch_mentor_excel_file)
        mentor = df[(df['E-Mail'] == email) & (df['Password'] == password)]
        if not mentor.empty:
            session['mentor'] = mentor.to_dict('records')[0]
            return redirect(url_for('batch_mentor_dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('batch_mentor_login.html')

@app.route('/batch_mentor/dashboard', methods=['GET', 'POST'])
def batch_mentor_dashboard():
    if 'mentor' not in session:
        return redirect(url_for('batch_mentor_login'))

    df_students = pd.read_excel(students_excel_file)
    batch_assigned = session['mentor']['Batch Assigned']
    df_students = df_students[df_students['batch'] == batch_assigned]

    if request.method == 'POST':
        if 'edit' in request.form:
            email_to_edit = request.form.get('email')
            if email_to_edit:
                student = df_students[df_students['email'] == email_to_edit]
                if not student.empty:
                    student = student.iloc[0].to_dict()
                    return render_template('batch_mentor_edit.html', student=student)
                else:
                    flash('Student not found!')
                    return redirect(url_for('batch_mentor_dashboard'))
        elif 'search' in request.form:
            search_query = request.form.get('search')
            search_column = request.form.get('search_column')
            if search_query and search_column:
                if search_column in df_students.columns:
                    df_students = df_students[df_students[search_column].astype(str).str.contains(search_query, case=False, na=False)]
                else:
                    flash('Invalid search column!')
            df_students = df_students.sort_values(by='name')

    students = df_students.to_dict(orient='records')
    mentor = session['mentor']
    return render_template('batch_mentor_dashboard.html', students=students, mentor=mentor)

@app.route('/batch_mentor/edit', methods=['POST'])
def batch_mentor_edit():
    if 'mentor' not in session:
        return redirect(url_for('batch_mentor_login'))

    email = request.form['email']
    df_students = pd.read_excel(students_excel_file)
    index = df_students[df_students['email'] == email].index[0]

    df_students.at[index, 'batch'] = request.form.get('batch', df_students.at[index, 'batch'])
    df_students.at[index, 'name'] = request.form.get('name', df_students.at[index, 'name'])
    df_students.at[index, 'mobile'] = request.form.get('mobile', df_students.at[index, 'mobile'])
    df_students.at[index, 'password'] = request.form.get('password', df_students.at[index, 'password'])
    df_students.at[index, 'designation'] = request.form.get('designation', df_students.at[index, 'designation'])
    df_students.at[index, 'company'] = request.form.get('company', df_students.at[index, 'company'])
    df_students.at[index, 'address'] = request.form.get('address', df_students.at[index, 'address'])
    df_students.at[index, 'district'] = request.form.get('district', df_students.at[index, 'district'])
    df_students.at[index, 'subdivision'] = request.form.get('subdivision', df_students.at[index, 'subdivision'])
    df_students.at[index, 'pin'] = request.form.get('pin', df_students.at[index, 'pin'])
    df_students.at[index, 'areawise'] = request.form.get('areawise', df_students.at[index, 'areawise'])
    df_students.at[index, 'country'] = request.form.get('country', df_students.at[index, 'country'])
    df_students.at[index, 'sector'] = request.form.get('sector', df_students.at[index, 'sector'])
    df_students.at[index, 'international'] = request.form.get('international', df_students.at[index, 'international'])
    df_students.at[index, 'domestic'] = request.form.get('domestic', df_students.at[index, 'domestic'])
    df_students.at[index, 'linkedin'] = request.form.get('linkedin', df_students.at[index, 'linkedin'])
    df_students.at[index, 'facebook'] = request.form.get('facebook', df_students.at[index, 'facebook'])
    df_students.at[index, 'instagram'] = request.form.get('instagram', df_students.at[index, 'instagram'])

    df_students.to_excel(students_excel_file, index=False)
    flash('Student record updated successfully!')
    return redirect(url_for('batch_mentor_dashboard'))

@app.route('/batch_mentor/logout')
def batch_mentor_logout():
    session.pop('mentor', None)
    flash('You have been logged out.')
    return redirect(url_for('batch_mentor_login'))


@app.route('/view_mentors', methods=['GET', 'POST'])
def view_mentors():
    if request.method == 'POST':
        if 'edit' in request.form:
            edit_id = request.form.get('edit_id')
            print(f"Edit ID received: {edit_id}")  # Debug statement
            if edit_id and edit_id.isdigit():
                return redirect(url_for('edit_mentor', mentor_id=int(edit_id)))
            else:
                print("Invalid ID for editing.")  # Debug statement
                return "Invalid ID for editing."

        elif 'delete' in request.form:
            delete_id = request.form.get('delete_id')
            print(f"Delete ID received: {delete_id}")  # Debug statement
            if delete_id and delete_id.isdigit():
                delete_mentor(delete_id)
                return redirect(url_for('view_mentors'))
            else:
                print("Invalid ID for deleting.")  # Debug statement
                return "Invalid ID for deleting."

    df = pd.read_excel('Batch_Mentor.xlsx')
    mentors = df.to_dict(orient='records')
    return render_template('view_mentors.html', mentors=mentors)


@app.route('/edit_mentor/<int:mentor_id>', methods=['GET', 'POST'])
def edit_mentor(mentor_id):
    # Load the data
    df = pd.read_excel('Batch_Mentor.xlsx')
    mentor_data = df.loc[df['Sr. No.'] == mentor_id].to_dict(orient='records')[0]

    if request.method == 'POST':
        # Update the mentor's information in the DataFrame
        df.loc[df['Sr. No.'] == mentor_id, 'Full Name'] = request.form['full_name']
        df.loc[df['Sr. No.'] == mentor_id, 'E-Mail'] = request.form['email']
        df.loc[df['Sr. No.'] == mentor_id, 'Contact No.'] = request.form['contact']
        df.loc[df['Sr. No.'] == mentor_id, 'Batch Assigned'] = request.form['batch']
        
        # Save the updated DataFrame back to the Excel file
        df.to_excel('Batch_Mentor.xlsx', index=False)
        return redirect(url_for('view_mentors'))

    return render_template('edit_mentor.html', mentor=mentor_data)

def delete_mentor(mentor_id):
    df = pd.read_excel('Batch_Mentor.xlsx')
    df = df[df['Sr. No.'] != int(mentor_id)]
    df.to_excel('Batch_Mentor.xlsx', index=False)

if __name__ == '__main__':
    app.run(debug=True)
