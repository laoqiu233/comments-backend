from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///{}'.format(os.path.join(os.getcwd(), 'data.db')))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dtvnfccjoubpyk:f94331ab9c89aad2079dec3b11e66bc55973fa38016fadc79facf64a3cc7d73c@ec2-46-137-124-19.eu-west-1.compute.amazonaws.com:5432/d8vm6c7jd8vakk'
print('Database: ', app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/api/comments', methods=['GET', 'POST'])
def comments_handler():
    resp = None
    if (request.method == 'GET'):
        comments = []
        for comment in Comment.query.order_by(Comment.published.desc()):
            comments.append({
                'User': comment.username,
                'Body': comment.body,
                'Published': int(comment.published.timestamp())
            })
        resp = jsonify(comments), 200
    elif (request.method == 'POST'):
        if (not request.values.get('username', '') or not request.values.get('body', '')):
            resp = jsonify({'msg': 'Bad Request'}), 400
        else:
            new_comment = Comment(
                username=request.values['username'], 
                body=request.values['body']
            )
            db.session.add(new_comment)
            db.session.commit()
            comments = []
            for comment in Comment.query.order_by(Comment.published.desc()):
                comments.append({
                    'User': comment.username,
                    'Body': comment.body,
                    'Published': int(comment.published.timestamp())
                })
            resp = jsonify(comments), 201
            
    resp[0].headers['Access-Control-Allow-Origin'] = '*'
    return resp

if (__name__ == '__main__'):
    db.create_all()
    app.run(
        port=80,
        debug=(os.environ.get('PY_ENV', '') != 'Production' )
    )