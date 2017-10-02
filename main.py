from flask import Flask, request, render_template, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:nervous@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "blahthek" 

class Blog(db.Model):

    id = db.Column( db.Integer, primary_key=True )
    title = db.Column( db.String(40) )
    body = db.Column( db.Text )
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner 

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    #Aldelcy's username not unique!
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 


def check_valid( item ):
    message = ''
    if len(item)<3 or len(item)>20 or ' ' in item:
        message = "This must be between 3-20 characters and have no spaces."
    return message

def check_loggedin( sess ):
    if 'username' in sess:
        return True
    return False

@app.before_request
def verify_logged_in():
    accessible = [ 'blog','indiv_blog' ,'login', 'index', 'register' ]
    #If able add blogs to the accessible list
    if request.endpoint not in accessible and not check_loggedin( session ):
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, loggedin=check_loggedin(session), page_header="All Users")



@app.route('/blog', methods=["POST", "GET"])
def blog():
    get_blog_id = request.args.get('id')
    get_user_id = request.args.get('user')
    blogs = Blog.query.all()

    if get_blog_id:
        blog_id = int(get_blog_id)
        this_blog = Blog.query.get( blog_id )

        if this_blog:
            return render_template('indiv_blog.html', loggedin=check_loggedin(session), page_header=this_blog.title, blog=this_blog)
        else:
            return render_template('noblog.html', loggedin=check_loggedin(session), page_header="Blog Not Found")
    
    
    if get_user_id:
        user = User.query.get( int(get_user_id) )
        blogs = user.blogs

    return render_template('/blogs.html', loggedin=check_loggedin(session), page_header="All Blogs", blogs=blogs)

@app.route('/blog_form' , methods=["GET","POST"])
def blog_form():
    
    if request.method == "POST":
        blog_title = request.form['b_title']
        blog_body = request.form['b_body']

        title_error, body_error = "", ""

        if not blog_title: title_error = "Please put a title"
        if not blog_body: body_error = "Please put a body"

        if not title_error and not body_error:
            owner = User.query.filter_by( username = session['username'] ).first()

            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()

            return redirect('/blog?id='+str(new_blog.id) )

        else:
            return render_template('/blog_form.html', 
                                    loggedin=check_loggedin(session), page_header="Create a new Blog", 
                                    title_error=title_error, 
                                    body_error=body_error,
                                    title=blog_title,
                                    body=blog_body)

    return render_template('/blog_form.html', loggedin=check_loggedin(session), page_header="Create a new Blog")

@app.route("/login" , methods=["GET","POST"])
def login():
    if request.method == "POST":
        form_username = request.form["username"]
        form_password = request.form["password"]

        user = User.query.filter_by( username=form_username ).first()
        
        if user and form_password == user.password:
            session["username"] = user.username
            return redirect('/blog_form')
            #return redirect('/blog?user='+str(user.id))
        
        else:
            error = " This username doesn't exist "
            password = " This password is incorrect "
            return render_template("login.html", user_error=error , password_error=password )
        
    return render_template("login.html", loggedin=check_loggedin(session), page_header="Login")

@app.route('/register', methods=["POST","GET"])
def register():

    if request.method == "POST":
        
        form_username = request.form["user_name"]
        form_password = request.form["password"]
        verify_password = request.form["verify_password"]

        username_error = check_valid( form_username )
        password_error = check_valid( form_password )
        verify_password_error = ''

        if form_password != verify_password: verify_password_error = "Password and verify password do not match"

        if not username_error and not password_error and not verify_password_error:
            existing_user = User.query.filter_by( username=form_username ).first()
            
            if not existing_user:
                newuser = User(form_username, form_password)
                db.session.add( newuser )
                db.session.commit()

                session['username'] = newuser.username

                return redirect('/blog?user='+str(newuser.id))
            else:
                username_error = "This username already exists."
                return render_template('register.html',  loggedin=check_loggedin(session), page_header="Register", user_name = form_username, user_name_error = username_error)

        return render_template('register.html',  loggedin=check_loggedin(session), page_header="Register", user_name = form_username, user_name_error = username_error, password_error = password_error, verify_password_error = verify_password_error)
        
    return render_template('register.html', loggedin=check_loggedin(session), page_header="Register")

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged out")
    return redirect('/')

if __name__=="__main__":
    app.run()