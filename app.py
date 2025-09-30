from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)  # Habilita CORS globalmente para produção

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
PAGE = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Verificador de Keys - The Hidden Web (Oculto)</title>
  <style>
    body{font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background:#0f172a; color:#e6eef8; padding:24px}
    .container{max-width:900px;margin:0 auto}
    h1{font-size:24px;margin-bottom:6px}
    p.lead{color:#cbd5e1;margin-top:0}
    .input-wrap{display:flex;gap:8px;margin-top:16px}
    input[type=text]{flex:1;padding:12px;border-radius:8px;border:1px solid #334155;background:#020617;color:#e6eef8;font-size:16px}
    button{padding:10px 14px;border-radius:8px;border:none;background:#2563eb;color:white;cursor:pointer}
    .meta{margin-top:18px;color:#93c5fd}
    .status-box{margin-top:12px;padding:14px;border-radius:10px;background:#021124;font-family:monospace}
    .ok{color:#34d399}
    .bad{color:#fb7185}
    .neutral{color:#94a3b8}
    footer{margin-top:30px;color:#94a3b8;font-size:13px}
  </style>
</head>
<body>
  <div class="container">
    <h1>Verificador de Keys</h1>
    <p class="lead">Cole a concatenação completa ou parcial das keys.</p>

    <div class="input-wrap">
      <input id="inputConcat" placeholder="Cole aqui a concatenação das keys..." autocomplete="off" />
      <button id="btnClear">Limpar</button>
    </div>

    <div class="meta">
      <div id="prefixStatus" class="status-box neutral">Status do prefixo: —</div>
      <div id="completeStatus" class="status-box neutral" style="margin-top:10px">Chaves completas: —</div>
      <div id="partialStatus" class="status-box neutral" style="margin-top:10px">Chave atual: —</div>
      <div id="md5Area" class="status-box neutral" style="margin-top:10px">MD5: —</div>
    </div>
  </div>

<script>
const input = document.getElementById('inputConcat');
const btnClear = document.getElementById('btnClear');
const btnExample = document.getElementById('btnExample');
const prefixStatus = document.getElementById('prefixStatus');
const completeStatus = document.getElementById('completeStatus');
const md5Area = document.getElementById('md5Area');
const partialStatus = document.getElementById('partialStatus');

let lastSent = '';

function updateUIFromResponse(data){
  prefixStatus.textContent = data.is_prefix_valid ? 'Prefixo válido até o momento.' : 'Prefixo inválido (há caracteres incorretos).';
  prefixStatus.className = 'status-box ' + (data.is_prefix_valid ? 'ok' : 'bad');

  completeStatus.textContent = 'Chaves completas: '+data.matched_count;
  completeStatus.className = 'status-box neutral';

  if(data.partial_index !== null && data.partial_index !== undefined){
    partialStatus.textContent = data.partial_correct ? ('Chave atual: parcial correta (índice aproximado: '+(data.partial_index+1)+')') : ('Chave atual: parcial INCORRETA (índice aproximado: '+(data.partial_index+1)+')');
    partialStatus.className = 'status-box ' + (data.partial_correct ? 'ok' : 'bad');
  } else {
    partialStatus.textContent = 'Chave atual: —';
    partialStatus.className = 'status-box neutral';
  }

  if(data.is_complete){
    md5Area.innerHTML = '<div>Concatenação completa detectada.</div><div style="margin-top:6px">MD5 esperado:</div><div style="font-family:monospace;margin-top:6px">'+data.expected_md5+'</div>';
    md5Area.className = 'status-box ok';
  } else {
    md5Area.textContent = 'MD5: —';
    md5Area.className = 'status-box neutral';
  }
}

async function checkServer(value){
  if(value === lastSent) return;
  lastSent = value;
  try{
    const res = await fetch('/api/check',{
      method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})
    });
    if(!res.ok) throw new Error('erro de rede');
    const data = await res.json();
    updateUIFromResponse(data);
  }catch(e){
    prefixStatus.textContent = 'Erro comunicando o servidor: '+e.message;
    prefixStatus.className = 'status-box bad';
  }
}

input.addEventListener('input', (e)=>{ checkServer(e.target.value.trim()); });
btnClear.addEventListener('click', ()=>{input.value=''; input.dispatchEvent(new Event('input'));});
btnExample.addEventListener('click', async ()=>{ 
  try{
    const r = await fetch('/api/debug_example');
    if(r.ok){ const j = await r.json(); input.value = j.example; input.dispatchEvent(new Event('input')); }
  }catch(err){ console.warn('debug fetch failed', err); }
});

// initial
checkServer('');
</script>
</body>
</html>
"""

# ----------------- ROTAS -----------------

@app.route('/')
def index():
    return render_template_string(PAGE)


@app.route('/api/check', methods=['POST'])
def api_check():
    data = request.get_json() or {}
    user_input = (data.get('input') or '')
    if not isinstance(user_input, str):
        user_input = str(user_input)

    expected = EXPECTED
    response = {
        'is_prefix_valid': False,
        'matched_count': 0,
        'matched_keys': [False]*len(KEYS),
        'partial_index': None,
        'partial_correct': False,
        'is_complete': False,
        'expected_md5': None,
    }

    # prefix check (fast)
    if expected.startswith(user_input):
        response['is_prefix_valid'] = True
    else:
        response['is_prefix_valid'] = False

    # determine how many full keys matched and if there is a partial match
    acc = ""
    matched = 0
    for idx, key in enumerate(KEYS):
        next_acc = acc + key
        if len(user_input) >= len(next_acc):
            # user_input covers whole key region
            if user_input[:len(next_acc)] == next_acc:
                response['matched_keys'][idx] = True
                matched += 1
            else:
                # mismatch in this key region -> stop
                break
            acc = next_acc
        else:
            # user_input does not yet reach end of this key; check partial
            if len(user_input) > len(acc):
                part = user_input[len(acc):]
                expected_part = key[:len(part)]
                response['partial_index'] = idx
                response['partial_correct'] = (part == expected_part)
            break

    response['matched_count'] = matched

    # complete?
    if user_input == expected:
        response['is_complete'] = True
        response['expected_md5'] = EXPECTED_MD5

    return jsonify(response)


# rota de debug (ativa somente quando DEBUG_MODE True)
if DEBUG_MODE:
    @app.route('/api/debug_example')
    def api_debug_example():
        return jsonify({'example': EXPECTED})


# ----------------- RUN -----------------
if __name__ == '__main__':
    # Em produção defina debug=False e DEBUG_MODE=False
    app.run(debug=True)
