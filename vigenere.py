"""Cifra de Vigenère: cifrar, decifrar e quebrar pela linha de comando.

Exemplos:
    python vigenere.py cifrar DomCasmurro.txt -k segredo
    python vigenere.py quebrar texto_criptografado.txt
    python vigenere.py decifrar texto_criptografado.txt -k segredo
"""

import argparse
import string
import sys
import unicodedata
from pathlib import Path

ALFABETO = string.ascii_lowercase
A = ord("a")

# frequência das letras no português (%), já sem acento
FREQ_PT = {
    "a": 14.63, "b": 1.04, "c": 3.88, "d": 4.99, "e": 12.57, "f": 1.02,
    "g": 1.30, "h": 1.28, "i": 6.18, "j": 0.40, "k": 0.02, "l": 2.78,
    "m": 4.74, "n": 5.05, "o": 10.73, "p": 2.52, "q": 1.20, "r": 6.53,
    "s": 7.81, "t": 4.34, "u": 4.63, "v": 1.67, "w": 0.01, "x": 0.21,
    "y": 0.01, "z": 0.47,
}
FREQ_PT_LISTA = [FREQ_PT[c] / 100 for c in ALFABETO]

IC_PORTUGUES = 0.0745  # IC médio de texto em português
IC_ALEATORIO = 1 / 26  # IC de texto totalmente embaralhado

# tudo que não for a-z vai pro lixo
_NAO_LETRAS = bytes(b for b in range(256) if not (A <= b <= ord("z")))


# ==== arquivos ====

def ler_arquivo(caminho):
    """Lê o arquivo tentando utf-8 primeiro e latin-1 se der ruim."""
    dados = Path(caminho).read_bytes()
    try:
        return dados.decode("utf-8-sig")
    except UnicodeDecodeError:
        return dados.decode("latin-1")


def salvar_arquivo(caminho, texto):
    Path(caminho).write_text(texto, encoding="ascii")


# ==== higienização ====

def higienizar(texto):
    """Deixa só letras de a até z, minúsculas e sem acento."""
    texto = texto.lower()
    # NFD separa a letra do acento (á vira a + ´), aí o ascii joga o acento fora
    texto = unicodedata.normalize("NFD", texto)
    somente_ascii = texto.encode("ascii", "ignore")
    return somente_ascii.translate(None, _NAO_LETRAS).decode("ascii")


# ==== cifra ====

def _tabela_deslocamento(desloc):
    """Tabela pro str.translate que anda 'desloc' casas no alfabeto."""
    deslocado = ALFABETO[desloc:] + ALFABETO[:desloc]
    return str.maketrans(ALFABETO, deslocado)


def _aplicar_chave(texto, deslocamentos):
    """Aplica um deslocamento por posição da chave.

    Em vez de ir letra por letra, pega cada fatia texto[i::k] (todas as
    letras que usam a mesma letra da chave) e traduz de uma vez só.
    Fica bem rápido até pra arquivo grande.
    """
    k = len(deslocamentos)
    saida = [""] * len(texto)
    for i, d in enumerate(deslocamentos):
        saida[i::k] = texto[i::k].translate(_tabela_deslocamento(d))
    return "".join(saida)


def _chave_para_deslocamentos(chave):
    chave = higienizar(chave)
    if not chave:
        raise ValueError("a chave precisa ter pelo menos uma letra de a a z")
    return [ord(c) - A for c in chave]


def cifrar(texto_limpo, chave):
    """C = (P + K) mod 26"""
    return _aplicar_chave(texto_limpo, _chave_para_deslocamentos(chave))


def decifrar(texto_cifrado, chave):
    """P = (C - K) mod 26"""
    inversos = [(26 - d) % 26 for d in _chave_para_deslocamentos(chave)]
    return _aplicar_chave(texto_cifrado, inversos)


# ==== criptoanálise ====

def contar_letras(texto):
    return [texto.count(c) for c in ALFABETO]


def indice_coincidencia(texto):
    """Chance de pegar duas letras ao acaso e elas serem iguais."""
    n = len(texto)
    if n < 2:
        return 0.0
    return sum(f * (f - 1) for f in contar_letras(texto)) / (n * (n - 1))


def ic_por_tamanho(texto, tamanho_max):
    """IC médio das colunas pra cada tamanho de chave testado."""
    resultados = {}
    for k in range(1, tamanho_max + 1):
        colunas = [texto[i::k] for i in range(k)]
        resultados[k] = sum(indice_coincidencia(c) for c in colunas) / k
    return resultados


def escolher_tamanho(ics):
    """Pega o menor tamanho com IC perto do melhor.

    Os múltiplos da chave certa (7, 14, 21...) também dão IC alto, então
    pegar só o máximo pode escolher o dobro. Por isso fica com o menor
    que chega a 90% do melhor.
    """
    melhor = max(ics.values())
    for k in sorted(ics):
        if ics[k] >= 0.9 * melhor:
            return k
    return max(ics, key=ics.get)


def qui_quadrado(contagem, total):
    """Quão longe a coluna está do português. Menor = mais parecido."""
    return sum(
        (obs - total * esp) ** 2 / (total * esp)
        for obs, esp in zip(contagem, FREQ_PT_LISTA)
    )


def achar_deslocamento(coluna):
    """Testa os 26 deslocamentos e fica com o que mais parece português."""
    contagem = contar_letras(coluna)
    total = len(coluna)
    if total == 0:
        return 0
    melhor_d, melhor_score = 0, float("inf")
    for d in range(26):
        # desfazer o deslocamento d é só girar a contagem
        girada = contagem[d:] + contagem[:d]
        score = qui_quadrado(girada, total)
        if score < melhor_score:
            melhor_d, melhor_score = d, score
    return melhor_d


def quebrar(texto_cifrado, tamanho_max=10, tamanho=None):
    """Descobre tamanho da chave, a chave e o texto. Devolve tudo junto."""
    ics = ic_por_tamanho(texto_cifrado, tamanho_max)
    if tamanho is None:
        tamanho = escolher_tamanho(ics)
    deslocs = [achar_deslocamento(texto_cifrado[i::tamanho]) for i in range(tamanho)]
    chave = "".join(ALFABETO[d] for d in deslocs)
    return {
        "ics": ics,
        "tamanho": tamanho,
        "chave": chave,
        "texto": decifrar(texto_cifrado, chave),
    }


# ==== CLI ====

def _pegar_chave(args):
    return args.chave if args.chave else input("Chave: ")


def cmd_higienizar(args):
    limpo = higienizar(ler_arquivo(args.entrada))
    salvar_arquivo(args.saida, limpo)
    print(f"{len(limpo)} letras salvas em {args.saida}")


def cmd_cifrar(args):
    chave = _pegar_chave(args)
    cifrado = cifrar(higienizar(ler_arquivo(args.entrada)), chave)
    salvar_arquivo(args.saida, cifrado)
    print(f"Texto cifrado ({len(cifrado)} letras) salvo em {args.saida}")


def cmd_decifrar(args):
    chave = _pegar_chave(args)
    # higieniza de novo só por garantia (quebra de linha, etc.)
    texto = decifrar(higienizar(ler_arquivo(args.entrada)), chave)
    salvar_arquivo(args.saida, texto)
    print(f"Texto decifrado salvo em {args.saida}")
    print(f"Começo: {texto[:args.preview]}")


def cmd_quebrar(args):
    cifrado = higienizar(ler_arquivo(args.entrada))
    if len(cifrado) < 2:
        sys.exit("Texto cifrado vazio ou curto demais.")

    r = quebrar(cifrado, args.max, args.tamanho)

    print("Índice de Coincidência por tamanho de chave")
    print(f"(português ~ {IC_PORTUGUES:.4f}, aleatório ~ {IC_ALEATORIO:.4f})\n")
    maior = max(r["ics"].values())
    for k, ic in r["ics"].items():
        barra = "#" * round(40 * ic / maior)
        marca = "  <<" if k == r["tamanho"] else ""
        print(f"  {k:>3}  {ic:.4f}  {barra}{marca}")

    print(f"\nTamanho estimado da senha: {r['tamanho']}")
    print(f"Senha encontrada: {r['chave']}")

    salvar_arquivo(args.saida, r["texto"])
    print(f"Texto decifrado salvo em {args.saida}")
    print(f"\nComeço do texto:\n{r['texto'][:args.preview]}")


def montar_parser():
    p = argparse.ArgumentParser(
        description="Cifra de Vigenère e criptoanálise por IC + frequência (português)."
    )
    sub = p.add_subparsers(dest="comando", required=True)

    h = sub.add_parser("higienizar", help="só limpa o texto (a-z)")
    h.add_argument("entrada")
    h.add_argument("-o", "--saida", default="texto_higienizado.txt")
    h.set_defaults(func=cmd_higienizar)

    c = sub.add_parser("cifrar", help="higieniza e cifra um .txt")
    c.add_argument("entrada")
    c.add_argument("-k", "--chave", help="senha (se omitir, pergunta)")
    c.add_argument("-o", "--saida", default="texto_criptografado.txt")
    c.set_defaults(func=cmd_cifrar)

    d = sub.add_parser("decifrar", help="decifra usando a senha")
    d.add_argument("entrada")
    d.add_argument("-k", "--chave", help="senha (se omitir, pergunta)")
    d.add_argument("-o", "--saida", default="texto_decifrado.txt")
    d.add_argument("--preview", type=int, default=300, help="letras mostradas no terminal")
    d.set_defaults(func=cmd_decifrar)

    q = sub.add_parser("quebrar", help="quebra a cifra sem saber a senha")
    q.add_argument("entrada")
    q.add_argument("-m", "--max", type=int, default=10, help="maior tamanho de chave testado")
    q.add_argument("-t", "--tamanho", type=int, help="força um tamanho de chave")
    q.add_argument("-o", "--saida", default="texto_quebrado.txt")
    q.add_argument("--preview", type=int, default=300, help="letras mostradas no terminal")
    q.set_defaults(func=cmd_quebrar)

    return p


def main():
    # sem isso os acentos saem zoados em alguns terminais do Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = montar_parser().parse_args()
    try:
        args.func(args)
    except (ValueError, OSError) as e:
        sys.exit(f"Erro: {e}")


if __name__ == "__main__":
    main()
