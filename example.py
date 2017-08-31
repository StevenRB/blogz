from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:greatdata@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column( db.Integer, primary_key=True )
    title = db.Column( db.String(40) )
    body = db.Column( db.Text )

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog', methods=["POST", "GET"])
def blog():

    if request.method == "POST":
        blog_title = request.form['b_title']
        blog_body = request.form['b_body']

        title_error, body_error = "", ""

        if not blog_title: title_error = "Please put a title"
        if not blog_body: body_error = "Please put a body"

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()

            return redirect('/blog?id='+str(new_blog.id) )

        else:
            return render_template('/blog_form.html', 
                                    page_header="Create a new Blog", 
                                    title_error=title_error, 
                                    body_error=body_error,
                                    title=blog_title,
                                    body=blog_body)

    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        this_blog = Blog.query.get( blog_id )

        if this_blog:
            return render_template('indiv_blog.html', page_header=this_blog.title, blog=this_blog)
        else:
            return render_template('noblog.html', page_header="Blog Not Found")


    blogs = Blog.query.all()
    return render_template('/blogs.html', page_header="All Blogs", blogs=blogs)


@app.route('/blog_form')
def blog_form():
    return render_template('/blog_form.html', page_header="Create a new Blog")



if __name__=="__main__":
    app.run()

"""
from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:greatdata@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
#app.config['WHOOSH_BASE']='whoosh'

db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_content = db.Column(db.String(1200))

@app.route('/', methods=['POST', 'GET'])
def index():
    posts = Blog.query.all()

    return render_template('index.html', posts=posts)

@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        post = Blog(blog_title=request.form['blog_title'], blog_content=request.form['blog_content'])
        db.session.add(post)
        db.session.commit()
        #return redirect('/blog?id='+new_blog.id)
        return redirect(('index'))

    if request.args.get('id'):
        blog_id = request.args.get('id')

        blog = Blog.query.get( blog_id)
        #return render_template('indiv_blog.html', pageheader=blog.title, blog=blog)
        return render_template('add.html')

@app.route('/blog', methods=['POST','GET'])
def blog():
    return render_template('blog.html')


if __name__ == '__main__':
    app.run(debug = True)
"""