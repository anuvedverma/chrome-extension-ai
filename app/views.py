from ai.chrome_extension import ChromeExtensionAI
from app import app

chrome_ai = ChromeExtensionAI()


@app.route('/api/<message>')
def get_response(message):
    return chrome_ai.get_response(message)