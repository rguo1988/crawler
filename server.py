from flask import Flask, render_template, redirect, url_for
from crawler import *
import os
import time
app = Flask(__name__,static_url_path='',root_path='./') 

@app.route('/')
def index():
    return app.send_static_file('index.html')
@app.route('/update')
def update():
    fun_RunCrawler();
    return app.send_static_file('index.html')

if __name__ == '__main__':
    #default setting of website
    app.run(host='127.0.0.1',port=5000,debug=True)
