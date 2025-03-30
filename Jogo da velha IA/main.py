from flask import Flask, render_template, jsonify, request
import random
import os
from colorama import init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jogo_da_velha_key'

def criar_tabuleiro():
    return [' ' for _ in range(9)]

def verificar_vitoria(tabuleiro, jogador):
    combinacoes = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), 
                   (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    return any(all(tabuleiro[i] == jogador for i in comb) for comb in combinacoes)

def espacos_vazios(tabuleiro):
    return [i for i, x in enumerate(tabuleiro) if x == ' ']

def minimax(tabuleiro, profundidade, eh_maximizando):
    if verificar_vitoria(tabuleiro, 'X'):
        return -1
    if verificar_vitoria(tabuleiro, 'O'):
        return 1
    if len(espacos_vazios(tabuleiro)) == 0:
        return 0

    if eh_maximizando:
        melhor_valor = -float('inf')
        for pos in espacos_vazios(tabuleiro):
            tabuleiro[pos] = 'O'
            valor = minimax(tabuleiro, profundidade + 1, False)
            tabuleiro[pos] = ' '
            melhor_valor = max(melhor_valor, valor)
        return melhor_valor
    else:
        melhor_valor = float('inf')
        for pos in espacos_vazios(tabuleiro):
            tabuleiro[pos] = 'X'
            valor = minimax(tabuleiro, profundidade + 1, True)
            tabuleiro[pos] = ' '
            melhor_valor = min(melhor_valor, valor)
        return melhor_valor

def melhor_jogada(tabuleiro):
    melhor_valor = -float('inf')
    melhor_movimento = None

    for pos in espacos_vazios(tabuleiro):
        tabuleiro[pos] = 'O'
        valor = minimax(tabuleiro, 0, False)
        tabuleiro[pos] = ' '
        if valor > melhor_valor:
            melhor_valor = valor
            melhor_movimento = pos

    return melhor_movimento

TABULEIRO = criar_tabuleiro()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/novo_jogo', methods=['POST'])
def novo_jogo():
    global TABULEIRO
    TABULEIRO = criar_tabuleiro()
    return jsonify({'tabuleiro': TABULEIRO})

@app.route('/fazer_jogada', methods=['POST'])
def fazer_jogada():
    global TABULEIRO
    data = request.get_json()
    posicao = data.get('posicao')

    if TABULEIRO[posicao] == ' ':
        TABULEIRO[posicao] = 'X'

        if verificar_vitoria(TABULEIRO, 'X'):
            return jsonify({'tabuleiro': TABULEIRO, 'status': 'vitoria_jogador'})

        if len(espacos_vazios(TABULEIRO)) == 0:
            return jsonify({'tabuleiro': TABULEIRO, 'status': 'empate'})

        # Jogada da IA
        pos_ia = melhor_jogada(TABULEIRO)
        TABULEIRO[pos_ia] = 'O'

        if verificar_vitoria(TABULEIRO, 'O'):
            return jsonify({'tabuleiro': TABULEIRO, 'status': 'vitoria_ia'})

        if len(espacos_vazios(TABULEIRO)) == 0:
            return jsonify({'tabuleiro': TABULEIRO, 'status': 'empate'})

        return jsonify({'tabuleiro': TABULEIRO, 'status': 'continuar'})

    return jsonify({'erro': 'Posição inválida'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)