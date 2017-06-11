from app import app
from chrome_extension import ChromeExtensionAI


chrome_ai = ChromeExtensionAI()


def get_access_token():
    f = open(".config", "r")
    token = f.readline()
    return token


@app.route('/')
@app.route('/index')
def index():
  return "Hello, World!"


@app.route('/api/<input_text>')
def get_response(input_text):
  return chrome_ai.get_response(input_text)

