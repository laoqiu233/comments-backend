from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///{}'.format(os.path.join(os.getcwd(), 'data.db')))
print('Database: ', app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/api/comments', methods=['GET', 'POST'])
def comments_handler():
    if (request.method == 'GET'):
        resp = []
        for comment in Comment.query.all():
            resp.append({
                'User': comment.username,
                'Body': comment.body,
                'Published': int(comment.published.timestamp())
            })
        return jsonify(resp)
    elif (request.method == 'POST'):
        if (not request.values.get('username', '') or not request.values.get('body', '')):
            return jsonify({'msg': 'Bad Request'}), 400
        else:
            new_comment = Comment(
                username=request.values['username'], 
                body=request.values['body']
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({
                'User': new_comment.username,
                'Body': new_comment.body,
                'Published': int(new_comment.published.timestamp())
            }), 201

if (__name__ == '__main__'):
    db.create_all()
    app.run(
        port=80,
        debug=(os.environ.get('PY_ENV', '') != 'Production' )
    )