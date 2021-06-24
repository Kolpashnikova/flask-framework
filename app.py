from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  key = os.environ
  return render_template('index.html', key=key)

@app.route('/about', methods=['GET', 'POST'])
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
