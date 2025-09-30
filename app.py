#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import hashlib
import os

# Inicializa Flask, apontando a pasta 'front' como static
app = Flask(__name__, static_folder='front')

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

# ----------------- FRONTEND -----------------
@app.route('/')
def index():
    # Serve o index.html corretamente
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    # Serve JS, CSS ou outros arquivos estáticos
    return send_from_directory(app.static_folder, filename)

# ----------------- API -----------------
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

    # Contar keys completas e verificar parcial
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

# Rota de debug (ativa apenas se DEBUG_MODE=True)
if DEBUG_MODE:
    @app.route('/api/debug_example')
    def api_debug_example():
        return jsonify({'example': EXPECTED})

# ----------------- RUN -----------------
if __name__ == '__main__':
    # Porta fornecida pelo Render via variável de ambiente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
