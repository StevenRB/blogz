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

    def __init__(self, blog_title, blog_content):
        self.blog_title = blog_title
        self.blog_title = blog_content

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'POST':
        blog_title = request.form['blog_title'] 
        blog_content = request.form['blog_content']
        title_error, body_error = "", ""

        if not blog_title: title_error = "Please put a title"
        if not blog_content: body_error = "Please put a body"

        if not title_error and not body_error:
            post = Blog(blog_title = request.form['blog_title'], blog_content = request.form['blog_content'])
            db.session.add(post)
            db.session.commit()

            return redirect('/blog?id'+str(post.id) )

        else:
            return render_template( 'add.html', 
                                    title_error=title_error, 
                                    body_error=body_error,
                                    blog_title=blog_title,
                                    blog_body=blog_content)

    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        this_blog = Blog.query.get( blog_id)

        if this_blog:
            return render_template('indiv_blog.html', page_header=this_blog.title, blog= this_blog)
        else: 
            return render_template('noblog.html', page_header="Blog Not Found")
    
    blogs = Blog.query.all()
    
    return render_template('blog.html')

@app.route('/add', methods=['POST', 'GET'])
def add():
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug = True)