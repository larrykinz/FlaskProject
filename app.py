from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/library_db"
app.secret_key = 'supersecretkey'
mongo = PyMongo(app)


@app.route('/index')
def index():
    try:
        books = mongo.db.books.find()
        books = [{**book, '_id': str(book['_id'])} for book in books]
        return render_template('index.html', books=books)
    except PyMongoError as e:
        flash(f"Unable to retrieve books: {e}", 'error')
        return render_template('index.html', books=[])

@app.route('/')
def landing_page():
    return render_template('landing_page.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        if title and author:
            try:
                mongo.db.books.insert_one({'title': title, 'author': author})
                flash('Book added successfully!', 'success')
            except PyMongoError as e:
                flash(f"Unable to add the book: {e}", 'error')
        else:
            flash('Both title and author are required!', 'warning')
        return redirect(url_for('index'))
    return render_template('add_book.html')


@app.route('/delete_book/<book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        mongo.db.books.delete_one({'_id': ObjectId(book_id)})
        flash('Book deleted successfully!', 'success')
    except PyMongoError as e:
        flash(f"Unable to  delete the book: {e}", 'error')
    return redirect(url_for('index'))


@app.route('/update_book/<book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        if title and author:
            try:
                mongo.db.books.update_one(
                    {'_id': ObjectId(book_id)},
                    {'$set': {'title': title, 'author': author}}
                )
                flash('Book updated successfully!', 'success')
            except PyMongoError as e:
                flash(f"Unable to update the book: {e}", 'error')
        else:
            flash('Both title and author are required!', 'warning')
        return redirect(url_for('index'))

    book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    if book:
        book['_id'] = str(book['_id'])
        return render_template('update_book.html', book=book)
    else:
        flash('Book not found!', 'warning')
        return redirect(url_for('index'))


@app.route('/staff_register', methods=['GET', 'POST'])
def staff_register():
    if request.method == 'POST':
        staff_name = request.form.get('staff_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if staff_name and email and password:
            existing_staff = mongo.db.staff.find_one({'email': email})
            if existing_staff:
                flash('Staff member already exists with this email!', 'warning')
            else:
                try:
                    mongo.db.staff.insert_one({'staff_name': staff_name, 'email': email, 'password': password})
                    flash('Staff registered successfully! You can now log in.', 'success')
                    return redirect(url_for('staff_login'))
                except PyMongoError as e:
                    flash(f"An error occurred while registering staff: {e}", 'error')
        else:
            flash('All fields are required!', 'warning')

    return render_template('staff_register.html')


@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            staff = mongo.db.staff.find_one({'email': email})
            if staff and staff['password'] == password:
                flash(f"Welcome {staff['staff_name']}!", 'success')
                return redirect(url_for('add_book'))
            else:
                flash('Invalid email or password!', 'warning')
        else:
            flash('Email and password are required!', 'warning')

    return render_template('staff_login.html')










@app.route('/member_register', methods=['GET', 'POST'])
def member_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if name and email and password:
            if mongo.db.members.find_one({'email': email}):
                flash('Member already exists with this email!', 'warning')
            else:
                try:
                    mongo.db.members.insert_one({'name': name, 'email': email, 'password': password})
                    flash('Member registered successfully! You can now log in.', 'success')
                    return redirect(url_for('member_login'))
                except PyMongoError as e:
                    flash(f"Unable to register member: {e}", 'error')
        else:
            flash('All fields are required!', 'warning')

    return render_template('member_register.html')




@app.route('/member_login', methods=['GET', 'POST'])
def member_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            member = mongo.db.members.find_one({'email': email})
            if member and member['password'] == password:
                flash(f"Welcome {member['name']}!", 'success')
                return redirect(url_for('view_books'))
            else:
                flash('Invalid email or password!', 'warning')
        else:
            flash('Email and password are required!', 'warning')

    return render_template('member_login.html')


@app.route('/view_books')
def view_books():
    books = mongo.db.books.find()
    books = [{**book, '_id': str(book['_id'])} for book in books]
    return render_template('view_books.html', books=books)

@app.route('/borrow_book/<book_id>', methods=['POST'])
def borrow_book(book_id):

    flash('Book borrowed successfully!', 'success')
    return redirect(url_for('view_books'))


if __name__ == '__main__':
    app.run(debug=True)
