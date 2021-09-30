from flask import Flask, render_template, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


from flask_wtf import FlaskForm
from wtforms import SubmitField
import webbrowser
import pandas as pd
import chime
from flask_cors import CORS



#from oopdatafeed import Manage




app = Flask(__name__)
CORS(app)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'

# init db
db = SQLAlchemy(app)

# init ma
ma = Marshmallow(app)


# data
class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    Zone = db.Column(db.String(length=30))
    name = db.Column(db.String(length=30))
    M1 = db.Column(db.String(length=30))
    M5 = db.Column(db.String(length=30))
    M15 = db.Column(db.String(length=30))
    H1 = db.Column(db.String(length=30))
    H4 = db.Column(db.String(length=30))
    D1 = db.Column(db.String(length=30))

    def __init__(self, name):
        self.name = name


class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'M1', 'M5', 'M15', 'H1', 'H4', 'D1',)


# Init schema
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


@app.route('/', methods=['POST'])
def post_itmes():
    id = request.json('id')
    name = request.json('name')
    M1 = request.json('M1')
    M5 = request.json('M5')
    M15 = request.json('M15')
    H1 = request.json('H1')
    H4 = request.json('H4')
    D1 = request.json('D1')

    new_item = Item(id, name, M1, M5, M15, H1, H4, D1)

    db.session.add(new_item)
    db.session.commit()

    return item_schema.jsonify(new_item)



# Create Item
@app.route('/', methods=['GET'])
def get_items():
    all_items = Item.query.all()
    result = items_schema.dump(all_items)
    return jsonify(result)


# runserver
if __name__ == '__main__':
    # webbrowser.open("http://127.0.0.1:5000/")
    app.run(port=8050,debug=True)
