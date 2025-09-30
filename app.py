#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import hashlib
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='front')
CORS(app)  # só se precisar do frontend externo

# ----------------- CONFIGURAÇÃO -----------------
KEYS = [
    "speXes1is4",
    "vh32i35jx2vhd5au5ow",
    "rClrFsjvimrmrJzcvetzfjrVehlrekfFMvekfTriivxrmrJvxivufj",
    "01010101011011100110100101100011011011110111001001101110011010010110111101110011566F616D536F72726964656E746573",
    "ofimestaproximo",
    "Ni0r9hlpLz",
    "thedeath",
    "nohopehere",
]
EXPECTED = "".join(KEYS)
EXPECTED_MD5 = hashlib.md5(EXPECTED.encode("utf-8")).hexdigest()
DEBUG_MODE = False
# -------------------------------------------------

# ----------------- ROTAS DO FRONTEND -----------------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# ----------------- ROTAS DA API -----------------
@app.route('/api/check', methods=['POST'])
def api_check():
    data = request.get_json() or {}
    user_input = str(data.get('input', ''))

    response = {
        'is_prefix_valid': EXPECTED.startswith(user_input),
        'matched_count': 0,
        'matched_keys': [False]*len(KEYS),
        'partial_index': None,
        'partial_correct': False,
        'is_complete': user_input == EXPECTED,
        'expected_md5': EXPECTED_MD5 if user_input == EXPECTED else None
    }

    # Verifica quantas keys completas estão corretas e parcial
    acc = ""
    matched = 0
    for idx, key in enumerate(KEYS):
        next_acc = acc + key
        if len(user_input) >= len(next_acc):
            if user_input[:len(next_acc)] == next_acc:
                response['matched_keys'][idx] = True
                matched += 1
            else:
                break
            acc = next_acc
        else:
            if len(user_input) > len(acc):
                part = user_input[len(acc):]
                expected_part = key[:len(part)]
                response['partial_index'] = idx
                response['partial_correct'] = (part == expected_part)
            break

    response['matched_count'] = matched
    return jsonify(response)

# rota de debug (ativa somente quando DEBUG_MODE=True)
if DEBUG_MODE:
    @app.route('/api/debug_example')
    def api_debug_example():
        return jsonify({'example': EXPECTED})

# ----------------- RUN -----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
