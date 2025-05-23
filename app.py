from flask import Flask, request, jsonify
import requests
import os
import traceback

app = Flask(__name__)

@app.route('/cotacao', methods=['POST'])
def cotar_frete():
    try:
        data = request.json
        print("Dados recebidos:", data)

        cep_origem = data.get("cep_origem", "").replace("-", "")
        cep_destino = data.get("cep_destino", "").replace("-", "")
        peso = data.get("peso", "1")
        comprimento = data.get("comprimento", "20")
        altura = data.get("altura", "10")
        largura = data.get("largura", "15")
        valor_declarado = data.get("valor_declarado", "0")

        cod_servicos = {
            "PAC": "41106",
            "SEDEX": "40010"
        }

        resultados = {}

        for nome, codigo in cod_servicos.items():
            params = {
                "nCdEmpresa": "",
                "sDsSenha": "",
                "nCdServico": codigo,
                "sCepOrigem": cep_origem,
                "sCepDestino": cep_destino,
                "nVlPeso": peso,
                "nCdFormato": "1",
                "nVlComprimento": comprimento,
                "nVlAltura": altura,
                "nVlLargura": largura,
                "nVlDiametro": "0",
                "sCdMaoPropria": "N",
                "nVlValorDeclarado": valor_declarado,
                "sCdAvisoRecebimento": "N",
                "StrRetorno": "xml"
            }

            url = "https://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"
            print(f"Consultando Correios para: {nome}")

            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)
            servico = root.find(".//cServico")
            valor = servico.find("Valor").text.replace(",", ".")
            prazo = servico.find("PrazoEntrega").text

            resultados[nome] = {
                "valor_frete": float(valor),
                "prazo_dias": int(prazo)
            }

        return jsonify(resultados)
    
    except Exception as e:
        print("Erro interno na API:")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno na API", "detalhe": str(e)}), 500

@app.route('/')
def home():
    return 'API de Cotação Correios Online'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
