# app.py — brand new Flask app (no prior code), dark mode + robust fallback
from flask import Flask, render_template, request
import os, logging
from core import SymptomCore

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'symptomx-dev')

# logging
os.makedirs('logs', exist_ok=True)
handler = logging.FileHandler('logs/app.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# initialize core (always available due to built-in fallback)
core = SymptomCore(data_dir='data')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    possible = []
    message = None
    user_input = ''
    if request.method == 'POST':
        user_input = (request.form.get('symptoms') or '').strip()
        try:
            out = core.diagnose(user_input, top_k=5)
            result = out.get('primary')
            possible = out.get('possible', [])
            message = out.get('message')
        except Exception as e:
            app.logger.error(f"diagnose failed: {e}")
            # Even on exceptions, don't surface 'service unavailable'; give a friendly message.
            message = "Could not process that input. Try different wording (e.g., 'fever, cough')."
    return render_template('index.html', result=result, possible=possible, message=message, user_input=user_input)

@app.route('/health')
def health():
    return {'status': 'ok', 'diseases': len(core.diseases), 'vocab': len(core.vocab)}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
