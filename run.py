import flask
import sqlite3
from sqlite3 import OperationalError
import math
import string
from urllib.parse import urlparse
import base64
import os


app = flask.Flask(__name__, template_folder='templates')
host = 'http://localhost:5000/'


def conv62(num,b =62):
    if b<=0 or b>62:
        return 0;
    chars = string.digits + string.ascii_lowercase + string.ascii_uppercase
    r = num%b;
    d = math.floor(num/b)
    hsh = chars[r]
    while d>0:
        r = q%b;
        d = math.floor(d/b)
        res += chars[r]
    return hsh

def conv10(num, b=62):
    chars = string.digits + string.ascii_lowercase + string.ascii_uppercase
    res = 0;
    for x in range(len(num)):
        res = b*res +  chars.find(num[x])
    return res;


def database():
    create = """
        CREATE TABLE URLS_MAP(
        ID INT PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create)
        except OperationalError:
            pass

@app.route('/', methods = ['GET', 'POST'])
def main():
    if flask.request.method == 'POST':
        original_url = str.encode(flask.request.form.get('url'))
        print(original_url)
        if urlparse(original_url).scheme == '':
            url = 'https://' + original_url
        else:
            url = original_url
        if url == b'':
            url = b'http://localhost:5000/'
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO URLS_MAP (URL) VALUES (?)',
                [base64.urlsafe_b64encode(url)]
            )
            conn.commit()
            string_encode = conv62(res.lastrowid)
        return flask.render_template('index1.html', short_url = host+string_encode)
    return flask.render_template('index1.html')



@app.route('/<short_url>')
def url_redirect(short_url):
    dec_string = conv10(short_url)
    url = host
    try:
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'SELECT URL FROM URLS_MAP WHERE ID = ?', [dec_string]
            )
            try:
                short = res.fetchone()
                if short is not None:
                    url = base64.urlsafe_b64decode(short[0])
            except Exception as e:
                print(e)
        return flask.redirect(url)
    except OverflowError as e:
        print(str(e))

if __name__ == 'main':
    database()
    app.run(debug = True)
