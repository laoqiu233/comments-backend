from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///{}'.format(os.path.join(os.getcwd(), 'data.db')))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dtvnfccjoubpyk:f94331ab9c89aad2079dec3b11e66bc55973fa38016fadc79facf64a3cc7d73c@ec2-46-137-124-19.eu-west-1.compute.amazonaws.com:5432/d8vm6c7jd8vakk'
print('Database: ', app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

password = '********'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip = db.Column(db.String(15), nullable=False)

@app.route('/api/testpw', methods=['POST'])
def testpw():
    if (request.form.get('password', '') == password):
        return jsonify({'msg': 'ok'})
    else:
        return jsonify({'msg': 'wrong password'}), 400

@app.route('/api/comments', methods=['GET', 'POST'])
def comments_handler():
    resp = None
    if (request.method == 'GET'):
        comments = []
        for comment in Comment.query.order_by(Comment.published.desc()):
            comments.append({
                'Id': comment.id,
                'User': comment.username,
                'Body': comment.body,
                'Published': int(comment.published.timestamp()),
            })
            if (request.values.get('password', '') == password): comments[-1]['Ip'] = comment.ip
        return jsonify(comments), 200
    elif (request.method == 'POST'):
        if (not request.form.get('username', '') or not request.form.get('body', '')):
            return jsonify({'msg': 'Bad Request'}), 400
        else:
            new_comment = Comment(
                username=request.values['username'], 
                body=request.values['body'],
                ip=request.remote_addr
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({
                    'Id': new_comment.id,
                    'User': new_comment.username,
                    'Body': new_comment.body,
                    'Published': int(new_comment.published.timestamp())
            }), 201

@app.route('/api/comments/<int:comment_id>', methods=['GET', 'DELETE'])
def comment_view(comment_id):
    comment = Comment.query.filter_by(id=comment_id).get_or_404()

    if (request.method == 'GET'):
        formatted_comment = {
            'Id': new_comment.id,
            'User': new_comment.username,
            'Body': new_comment.body,
            'Published': int(new_comment.published.timestamp()),
        }
        if (request.values.get('password', '') == password): formatted_comment['Ip'] = comment.ip
        return jsonify(formatted_comment)
    elif (request.method == 'DELETE'):
        db.session.remove(comment)
        db.session.commit()
        return {'msg': 'deleted'}, 200

@app.after_request
def apply_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    return response

if (__name__ == '__main__'):
    db.create_all()
    app.run(
        port=80,
        debug=(os.environ.get('PY_ENV', '') != 'Production' )
    )