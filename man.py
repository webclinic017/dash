from flask import Flask , render_template , request,flash
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import SubmitField
import webbrowser
import pandas as pd
import chime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    Zone = db.Column(db.String(length=30))
    name = db.Column(db.String(length=30) )
    M1 = db.Column(db.String(length=30))
    M5 = db.Column(db.String(length=30))
    M15 = db.Column(db.String(length=30))
    H1 = db.Column(db.String(length=30))
    H4 = db.Column(db.String(length=30))
    D1 = db.Column(db.String(length=30))

    def __repr__(self):
        return  f'Item{self.name}'


class Item1(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(length=30) )
    M1 = db.Column(db.String(length=30))
    M5 = db.Column(db.String(length=30))
    M15 = db.Column(db.String(length=30))
    H1 = db.Column(db.String(length=30))
    H4 = db.Column(db.String(length=30))
    D1 = db.Column(db.String(length=30))

class Ud(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30))
    M1 = db.Column(db.String(length=30))
    M5 = db.Column(db.String(length=30))
    M15 = db.Column(db.String(length=30))
    H1 = db.Column(db.String(length=30))
    H4 = db.Column(db.String(length=30))
    D1 = db.Column(db.String(length=30))

    def __repr__(self):
        return  f'Item{self.name}'


class Fuck(FlaskForm):
    submit = SubmitField(label='X')




currencys = ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'GOLD', 'WTI', '#USSPX500', '#USNDAQ100', '#US30',
              '#Germany30', '#Euro50','EURGBP']


data = {'name': currencys,'H4': '', 'H1': '','D1': '','M5': '','M1': '','id': '','M15': '','Zone':'' }
dfg = pd.DataFrame(data)
forb = []

A=''




s = False

@app.route('/', methods= ['GET','POST'])
@app.route('/home', methods= ['GET','POST'])
def hello_word():
    global b
    b = None
    global forb
    global dfg
    currencys = ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'GOLD', 'WTI', '#USSPX500', '#USNDAQ100', '#US30',
              '#Germany30', '#Euro50','EURGBP']
    # '@EP','@ENQ', '@YM', '@RTY', '@DD', '@DSX', 'XAUUSD', '@CLE', '@DB', 'TYAH21','EURUSD', 'GBPUSD', 'USDCAD','USDJPY','EURGBP'
    fuck1 = Fuck()
    items = Item.query.all()
    dictlist = []
    ds = []
    for yi in range(len(items)):
        ds.append(items[yi].__dict__)
    d = {}
    for k in ds[0].keys():
        d[k] = tuple(d[k] for d in ds)
    del d['_sa_instance_state']
    '''
        #print(pa)
        for key, value in items[yi].__dict__.items():
            temp = [key, value]
            dictlist.append(temp)
    '''
    #if fuck1.validate_on_submit:
    if request.form.get('fuck1') != None:
        request.form.get('fuck1')
        dem = request.form.get('fuck1')
        only_alpha = ""
        ## looping through the string to find out alphabets
        for char in dem:
            ## ord(chr) returns the ascii value
            ## CHECKING FOR UPPER CASE
            if ord(char) >= 65 and ord(char) <= 90:
                only_alpha += char
            ## checking for lower case
            elif ord(char) >= 97 and ord(char) <= 122:
                only_alpha += char
            elif ord(char) >= 44 and ord(char) <= 57 or ord(char) == 35:
                only_alpha += char
            b = only_alpha.split(",")
        if b not in forb:
            forb += [b]
        ## printing the string which contains only alphabets
        #print(currencys.index[0])
    if len(forb) > 0:
        for forb_i in range(len(forb)):
            ind = currencys.index(forb[forb_i][0])
            items[ind].__dict__[forb[forb_i][1]] = 'chay'
    #pan = pd.DataFrame.from_dict(items[0].__dict__)
    #print(items[0].__dict__)
    #pan = pd.DataFrame.from_dict(items[0].__dict__)
    #print(items[0].__dict__.items())
    #len(items[0].__dict__.items())
    df = pd.DataFrame(d)
    global A
    try:
        for i in df.columns:
            for j in range(len(df)):
                if dfg[i][j] == 'v' and (df[i][j] == 'O' or df[i][j] == 'T') and i != 'M1':  # and i != 'M1'
                    C_out = df['name'][j]
                    TF_out = i
                    A = C_out + ' ' + TF_out
                    flash(A, category='warning')
                    chime.info()
                if dfg[i][j] == 'r' and (df[i][j] == 'Or' or df[i][j] == 'Tr') and i != 'M1':  # and i != 'M1'
                    C_out = df['name'][j]
                    TF_out = i
                    A = C_out + '  ' + TF_out
                    flash(A, category='warning')
                    chime.success()
    except:
        print("An exception occurred")
    if len(forb)>0:
        for uy in range(len(forb)):
            if df[forb[uy][1]][currencys.index(forb[uy][0])] == 'chay':
                del forb[uy]
    dfg = df
    return render_template('home.html', items =items,fuck1 = fuck1)

@app.route('/secondpage')
def second_page():
    fuck1 = Fuck()
    items2 = Ud.query.all()
    return render_template('secondpage.html',items2=items2 ,fuck1 = fuck1)


if __name__ == '__main__':

    app.run(port=8050,debug=True)