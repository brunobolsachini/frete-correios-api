from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/cotacao', methods=['POST'])
def cotar_frete():
    data = request.json

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
        response = requests.get(url, params=params)

        if response.status_code == 200:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)
            servico = root.find(".//cServico")
            valor = servico.find("Valor").text.replace(",", ".")
            prazo = servico.find("PrazoEntrega").text

            resultados[nome] = {
                "valor_frete": float(valor),
                "prazo_dias": int(prazo)
            }
        else:
            resultados[nome] = {"erro": "Falha ao consultar"}

    return jsonify(resultados)

@app.route('/')
def home():
    return 'API de Cotação Correios Online'
