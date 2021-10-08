from flask import Flask, render_template, request, flash, jsonify ,json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import requests

from flask_wtf import FlaskForm
from wtforms import SubmitField
import webbrowser
import pandas as pd
import chime
from flask_cors import CORS

currencys = ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'GOLD', 'OIL-NOV21',  'US500Cash', 'US100Cash', 'US30Cash',
             'EU50Cash', 'GER40Cash']



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



class Ud(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30))
    M1 = db.Column(db.String(length=30))
    M5 = db.Column(db.String(length=30))
    M15 = db.Column(db.String(length=30))
    H1 = db.Column(db.String(length=30))
    H4 = db.Column(db.String(length=30))
    D1 = db.Column(db.String(length=30))

    def __init__(self, name):
        self.name = name


class UdSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'M1', 'M5', 'M15', 'H1', 'H4', 'D1',)

# Init schema
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


canceled_by_botton = []
@app.route('/', methods=['POST'])
def post_itmes():
    a = request.get_json()
    if a not in canceled_by_botton:
        canceled_by_botton.append(a)
    return a


# Create Item
@app.route('/', methods=['GET'])
def get_items():
    all_items = Item.query.all()
    result = items_schema.dump(all_items)
    result1 = items_schema.dump(all_items)
    if len(canceled_by_botton) > 0:
        print(canceled_by_botton)
        for canceled_by_botton_i in (canceled_by_botton):
            tf_cansulated = canceled_by_botton_i['tf']
            curr_cansulated = canceled_by_botton_i['curr']
            ind = currencys.index(curr_cansulated)
            result1[ind][tf_cansulated] = 'chay'

        for uy in range(len(canceled_by_botton)):
                tf_cansulated = canceled_by_botton_i['tf']
                curr_cansulated = canceled_by_botton_i['curr']
                ind = currencys.index(curr_cansulated)
                if result[ind][tf_cansulated] == 'chay':
                    del canceled_by_botton[uy]
    return jsonify(result1)


@app.route('/eng', methods=['GET'])
def get_items_eng():
    all_items_eng = Ud.query.all()
    result_eng = items_schema.dump(all_items_eng)
    return jsonify(result_eng)


# runserver
if __name__ == '__main__':
    # webbrowser.open("http://127.0.0.1:5000/")
    app.run(port=8050,debug=True)
