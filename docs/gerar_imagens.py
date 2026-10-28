"""Gera as imagens de docs/VISUALIZACAO.md a partir do próprio vigenere.py.

Todos os números das figuras (IC, qui-quadrado, letras cifradas) saem das
funções do programa, então as imagens sempre batem com o que ele faz.

Uso (na raiz do repositório):
    python docs/gerar_imagens.py

Precisa de matplotlib (só para as imagens; o vigenere.py continua usando
apenas a biblioteca padrão).
"""

import sys
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import vigenere as v  # noqa: E402

SAIDA = RAIZ / "docs" / "img"
SENHA = "segredo"

# ==== estilo ====

FUNDO = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
APAGADO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
NEUTRO = "#f0efec"
AZUL = "#2a78d6"
AZUL_CLARO = "#b7d3f6"
LARANJA = "#eb6834"
BOM = "#0ca30c"
RUIM = "#d03b3b"

# uma cor por posição da senha (s e g r e d o); a letra vai escrita no
# quadrado, então a cor nunca carrega a informação sozinha
CORES_CHAVE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]
TINTA_SOBRE = ["#ffffff", "#ffffff", "#ffffff", TINTA, TINTA, "#ffffff", "#ffffff"]

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 11,
    "figure.facecolor": FUNDO,
    "axes.facecolor": FUNDO,
    "axes.edgecolor": EIXO,
    "axes.labelcolor": TINTA_2,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "savefig.facecolor": FUNDO,
})

# acento solto depois do NFD não aparece sozinho; mostra a versão "com espaço"
ACENTO_VISIVEL = {"́": "´", "̀": "`", "̃": "~", "̂": "^",
                  "̧": "¸", "̈": "¨"}

PASSO = 1.12  # distância entre quadrados


def mostrar(c):
    if c == " ":
        return "␣"
    return ACENTO_VISIVEL.get(c, c)


def num(x, casas=4):
    """Número no formato brasileiro (vírgula decimal)."""
    return f"{x:.{casas}f}".replace(".", ",")


def quadrado(ax, x, y, texto, sub=None, fundo=NEUTRO, tinta=TINTA, borda=None,
             largura=1.0, tamanho=15, negrito=True, riscado=False):
    """Desenha um quadrado arredondado com uma letra (e um número pequeno embaixo)."""
    ax.add_patch(FancyBboxPatch(
        (x + 0.04, y + 0.04), largura - 0.08, 0.92,
        boxstyle="round,pad=0,rounding_size=0.14",
        facecolor=fundo, edgecolor=borda or fundo, linewidth=1.6 if borda else 0))
    ty = y + (0.6 if sub is not None else 0.5)
    ax.text(x + largura / 2, ty, texto, ha="center", va="center", color=tinta,
            fontsize=tamanho, fontweight="bold" if negrito else "normal")
    if sub is not None:
        ax.text(x + largura / 2, y + 0.22, sub, ha="center", va="center",
                color=tinta, fontsize=8.5, alpha=0.85)
    if riscado:
        ax.plot([x + 0.18, x + largura - 0.18], [y + 0.18, y + 0.82],
                color=RUIM, linewidth=1.6)


def grade(colunas, linhas, rotulo=3.6, escala=0.5, altura_titulo=1.6):
    """Figura em coordenadas de 'quadrados': x de -rotulo até colunas, y para baixo."""
    largura = rotulo + colunas * PASSO + 0.3
    altura = linhas * 1.35 + altura_titulo
    fig = plt.figure(figsize=(largura * escala, altura * escala))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-rotulo, colunas * PASSO + 0.3)
    ax.set_ylim(-linhas * 1.35 + 0.1, altura_titulo + 0.1)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def titulo_grade(ax, titulo, subtitulo=None, rotulo=3.6):
    ax.text(-rotulo + 0.2, 1.25, titulo, fontsize=15, fontweight="bold", color=TINTA, va="center")
    if subtitulo:
        ax.text(-rotulo + 0.2, 0.55, subtitulo, fontsize=10.5, color=TINTA_2, va="center")


def rotulo_linha(ax, y, texto, rotulo=3.6):
    ax.text(-rotulo + 0.2, y + 0.5, texto, fontsize=11, color=TINTA_2, va="center")


def salvar(fig, nome):
    SAIDA.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA / nome, dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("  ", nome)


# ==== 0. visão geral ====

def fig_visao_geral():
    fig = plt.figure(figsize=(13, 3.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.3)
    ax.axis("off")

    caixas = [
        (0.2, "Texto .txt", "acentos, pontuação,\nespaços", NEUTRO, TINTA),
        (2.75, "Higienizar", "só a–z,\nminúsculo", AZUL, "#ffffff"),
        (5.3, "Cifrar", "senha 'segredo'\nC = (P + K) mod 26", AZUL, "#ffffff"),
        (7.85, "Quebrar", "1) IC → tamanho\n2) χ² → cada letra", LARANJA, "#ffffff"),
        (10.4, "Texto + senha", "recuperados\nsem saber a senha", NEUTRO, TINTA),
    ]
    for x, nome, desc, cor, tinta in caixas:
        ax.add_patch(FancyBboxPatch((x, 0.9), 2.3, 1.6, boxstyle="round,pad=0,rounding_size=0.15",
                                    facecolor=cor, edgecolor=EIXO if cor == NEUTRO else cor))
        ax.text(x + 1.15, 2.05, nome, ha="center", va="center", fontsize=13,
                fontweight="bold", color=tinta)
        ax.text(x + 1.15, 1.35, desc, ha="center", va="center", fontsize=9.5, color=tinta)
    for x in (2.5, 5.05, 7.6, 10.15):
        ax.add_patch(FancyArrowPatch((x, 1.7), (x + 0.25, 1.7), arrowstyle="-|>",
                                     mutation_scale=14, color=TINTA_2, linewidth=1.5))
    ax.text(6.45, 0.45, "Parte 1 do enunciado", ha="center", color=AZUL, fontsize=10)
    ax.text(9.0, 0.45, "Parte 2 do enunciado", ha="center", color=LARANJA, fontsize=10)
    ax.text(0.2, 3.0, "O caminho de uma frase pelo programa", fontsize=15,
            fontweight="bold", color=TINTA, va="center")
    salvar(fig, "00_visao_geral.png")


# ==== 1. higienização ====

def fig_higienizacao(frase, nome, titulo):
    """Mostra cada etapa de higienizar() caractere por caractere.

    Cada caractere original ocupa uma 'fatia' com a largura do que ele vira
    depois do NFD (é → e + ´ ocupa duas casas), então as linhas ficam
    alinhadas e dá para seguir cada letra de cima a baixo.
    """
    grupos = []  # (original, minúsculo, [caracteres NFD])
    for c in frase:
        baixo = c.lower()
        grupos.append((c, baixo, list(unicodedata.normalize("NFD", baixo))))
    colunas = sum(len(g[2]) for g in grupos)
    resultado = v.higienizar(frase)

    fig, ax = grade(colunas, 5, rotulo=4.2)
    titulo_grade(ax, titulo, f"higienizar({frase!r})  →  {resultado!r}", rotulo=4.2)

    linhas_y = [-1.3, -2.65, -4.0, -5.35]
    rotulos = ["1. original", "2. minúsculas", "3. NFD separa\n    o acento", "4. só a–z fica"]
    for y, r in zip(linhas_y, rotulos):
        rotulo_linha(ax, y, r, rotulo=4.2)

    x = 0.0
    for original, baixo, nfd in grupos:
        larg = len(nfd) * PASSO - (PASSO - 1)
        mudou_baixo = baixo != original
        quadrado(ax, x, linhas_y[0], mostrar(original), largura=larg)
        quadrado(ax, x, linhas_y[1], mostrar(baixo), largura=larg,
                 borda=AZUL if mudou_baixo else None)
        for i, c in enumerate(nfd):
            xi = x + i * PASSO
            separado = len(nfd) > 1
            quadrado(ax, xi, linhas_y[2], mostrar(c), borda=AZUL if separado else None)
            fica = "a" <= c <= "z"
            if fica:
                quadrado(ax, xi, linhas_y[3], c, fundo=AZUL, tinta="#ffffff")
            else:
                quadrado(ax, xi, linhas_y[3], mostrar(c), fundo=FUNDO, tinta=APAGADO,
                         borda=GRADE, negrito=False, riscado=True)
        x += len(nfd) * PASSO

    # resultado compacto
    rotulo_linha(ax, -6.7, "resultado", rotulo=4.2)
    for i, c in enumerate(resultado):
        quadrado(ax, i * PASSO, -6.7, c, fundo=AZUL, tinta="#ffffff")
    ax.text(len(resultado) * PASSO + 0.3, -6.2, f"{len(resultado)} letras",
            color=TINTA_2, fontsize=11, va="center")
    ax.set_ylim(-7.0, 1.7)
    salvar(fig, f"01_higienizacao_{nome}.png")


# ==== 2. cifra ====

def fig_cifra(texto, nome, titulo, inicio=0, nota=None):
    """Tabela visual de C = (P + K) mod 26, com a senha alinhada pela posição real."""
    k = len(SENHA)
    n = len(texto)
    fig, ax = grade(n, 4.4, rotulo=3.8)
    sub = f"senha '{SENHA}' repetida por baixo do texto · a = 0, b = 1, …, z = 25"
    if nota:
        sub += f" · {nota}"
    titulo_grade(ax, titulo, sub, rotulo=3.8)

    ys = {"P": -1.3, "K": -2.5, "S": -3.7, "C": -4.9}
    rotulo_linha(ax, ys["P"], "texto (P)", 3.8)
    rotulo_linha(ax, ys["K"], "senha (K)", 3.8)
    rotulo_linha(ax, ys["S"], "P + K", 3.8)
    rotulo_linha(ax, ys["C"], "mod 26 → C", 3.8)

    cifrado = v.cifrar(texto, SENHA) if inicio == 0 else None
    for i, p in enumerate(texto):
        pos = (inicio + i) % k
        kc = SENHA[pos]
        pv, kv = ord(p) - 97, ord(kc) - 97
        soma = pv + kv
        c = chr((soma % 26) + 97)
        if cifrado is not None:
            assert c == cifrado[i]  # confere com a implementação de verdade
        x = i * PASSO
        quadrado(ax, x, ys["P"], p, sub=str(pv))
        quadrado(ax, x, ys["K"], kc, sub=str(kv), fundo=CORES_CHAVE[pos], tinta=TINTA_SOBRE[pos])
        deu_volta = soma >= 26
        quadrado(ax, x, ys["S"], str(soma), sub="−26" if deu_volta else None,
                 borda=LARANJA if deu_volta else None, tamanho=12)
        quadrado(ax, x, ys["C"], c, sub=str(soma % 26), fundo=CORES_CHAVE[pos],
                 tinta=TINTA_SOBRE[pos])
    ax.set_ylim(-5.2, 1.7)
    salvar(fig, f"02_cifra_{nome}.png")


# ==== 3. colunas ====

def fig_colunas(cifrado, nome, titulo, k=7, linhas_max=5):
    """Escreve o texto cifrado em k colunas: cada coluna usa uma só letra da senha."""
    linhas = min(linhas_max, -(-len(cifrado) // k))
    cortado = len(cifrado) > linhas * k
    fig, ax = grade(k + 6.5, linhas + 2.2, rotulo=0.4)
    ax.text(0, 1.25, titulo, fontsize=15, fontweight="bold", color=TINTA, va="center")
    ax.text(0, 0.55, f"texto cifrado escrito em linhas de {k} letras · coluna i = letras i, i+{k}, i+{2*k}, …",
            fontsize=10.5, color=TINTA_2, va="center")

    for j in range(k):
        ax.text(j * PASSO + 0.5, -0.45, f"col {j}", ha="center", fontsize=9, color=TINTA_2)
    for linha in range(linhas):
        for j in range(k):
            i = linha * k + j
            y = -1.5 - linha * 1.12
            if i < len(cifrado):
                quadrado(ax, j * PASSO, y, cifrado[i], fundo=CORES_CHAVE[j % 7],
                         tinta=TINTA_SOBRE[j % 7])
            else:
                quadrado(ax, j * PASSO, y, "", fundo=FUNDO, borda=GRADE)
    y_fim = -1.5 - linhas * 1.12
    if cortado:
        for j in range(k):
            ax.text(j * PASSO + 0.5, y_fim + 0.55, "⋮", ha="center", fontsize=16, color=APAGADO)

    # tamanho de cada coluna
    xr = k * PASSO + 0.6
    ax.text(xr, -0.45, "letras na coluna", fontsize=9, color=TINTA_2)
    for j in range(k):
        tam = len(cifrado[j::k])
        ax.text(xr, -1.0 - j * 0.62, f"col {j}:  {tam:,}".replace(",", ".") + (" letra" if tam == 1 else " letras"),
                fontsize=10.5, color=TINTA, va="center")
    ax.set_ylim(min(y_fim - 0.4, -1.0 - k * 0.62), 1.7)
    salvar(fig, f"03_colunas_{nome}.png")


# ==== 4. índice de coincidência ====

def fig_ic(cifrado, nome, titulo, nota):
    r = v.quebrar(cifrado)
    ics = r["ics"]
    escolhido = r["tamanho"]
    ks = list(ics)
    valores = [ics[k] for k in ks]
    melhor = max(valores)

    fig, ax = plt.subplots(figsize=(9, 4.3))
    fig.subplots_adjust(left=0.1, right=0.8, top=0.8, bottom=0.14)
    cores = [AZUL if k == escolhido else AZUL_CLARO for k in ks]
    ax.bar(ks, valores, width=0.6, color=cores, edgecolor=FUNDO, linewidth=2, zorder=3)
    topo = max(0.095, melhor * 1.15)
    ax.set_ylim(0, topo)
    ax.set_xticks(ks)
    ax.set_xlabel("tamanho de senha testado (k)")
    ax.set_ylabel("IC médio das colunas")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y, _: num(y, 2)))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

    ax.axhline(v.IC_PORTUGUES, color=TINTA_2, linestyle="--", linewidth=1.2, zorder=4)
    ax.axhline(v.IC_ALEATORIO, color=APAGADO, linestyle=":", linewidth=1.4, zorder=4)
    ax.text(10.55, v.IC_PORTUGUES, f"português\n≈ {num(v.IC_PORTUGUES)}", va="center",
            fontsize=9.5, color=TINTA_2)
    ax.text(10.55, v.IC_ALEATORIO, f"aleatório\n≈ {num(v.IC_ALEATORIO)}", va="center",
            fontsize=9.5, color=APAGADO)
    if melhor > 0:
        # linha de corte de escolher_tamanho(): o menor k que passa dela vence
        ax.axhline(0.9 * melhor, color=LARANJA, linewidth=1, alpha=0.7, zorder=4)
        ax.text(10.45, 0.9 * melhor - 0.0015, "corte: 90% do melhor", ha="right", va="top",
                fontsize=9, color=LARANJA, zorder=5,
                bbox=dict(facecolor=FUNDO, edgecolor="none", pad=1))
    else:
        ax.text(6.0, 0.022, "IC = 0 em todos os tamanhos: as barras nem aparecem",
                ha="center", fontsize=10.5, color=RUIM)
    ax.annotate(f"escolhido: k = {escolhido}\nIC = {num(ics[escolhido])}",
                xy=(escolhido, ics[escolhido]),
                xytext=(escolhido + 0.4, ics[escolhido] + 0.006),
                fontsize=10, color=TINTA, va="bottom",
                arrowprops=dict(arrowstyle="-", color=TINTA_2, linewidth=0.8))
    ax.set_xlim(0.4, 10.5)
    fig.text(0.1, 0.93, titulo, fontsize=14, fontweight="bold", color=TINTA)
    fig.text(0.1, 0.865, nota, fontsize=10, color=TINTA_2)
    salvar(fig, f"04_ic_{nome}.png")
    return r


# ==== 5. frequência de uma coluna (só faz sentido com texto grande) ====

def fig_frequencia(cifrado, nome, titulo, coluna=0, k=7):
    col = cifrado[coluna::k]
    contagem = v.contar_letras(col)
    total = len(col)
    d = v.achar_deslocamento(col)
    pct = [100 * c / total for c in contagem]
    girada = pct[d:] + pct[:d]
    esperado = [100 * f for f in v.FREQ_PT_LISTA]
    letras = list(v.ALFABETO)
    xs = range(26)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.2), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.08, hspace=0.55)
    for ax, dados, legenda in (
        (a1, pct, None),
        (a2, girada, None),
    ):
        ax.bar(xs, dados, width=0.7, color=AZUL, edgecolor=FUNDO, linewidth=2, zorder=3,
               label=legenda)
        ax.plot(xs, esperado, "o", color=LARANJA, markersize=7, markeredgecolor=FUNDO,
                markeredgewidth=1.5, zorder=4, label="português esperado")
        ax.set_xticks(xs)
        ax.set_xticklabels(letras)
        ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
        ax.set_ylabel("% das letras")
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        ax.set_ylim(0, 17)
        # rotula as 3 maiores barras
        for i in sorted(xs, key=lambda i: -dados[i])[:3]:
            ax.text(i, dados[i] + 0.4, letras[i], ha="center", fontsize=10,
                    fontweight="bold", color=TINTA)
    top3 = sorted(xs, key=lambda i: -pct[i])[:3]
    origem = [letras[(i - d) % 26] for i in top3]
    a1.set_title(f"as três mais comuns são {', '.join(letras[i] for i in top3)} …",
                 loc="left", fontsize=11, color=TINTA_2)
    a2.set_title(f"… que são {', '.join(origem)} deslocadas {d} casas: as barras encaixam nos pontos",
                 loc="left", fontsize=11, color=TINTA_2)
    fig.text(0.08, 0.94, titulo, fontsize=14, fontweight="bold", color=TINTA)
    alcas = [matplotlib.patches.Patch(color=AZUL, label="% de cada letra na coluna"),
             matplotlib.lines.Line2D([], [], marker="o", linestyle="", color=LARANJA,
                                     markeredgecolor=FUNDO, markersize=8, label="português esperado")]
    fig.legend(handles=alcas, loc="upper right", bbox_to_anchor=(0.98, 0.975), ncol=2,
               frameon=False, fontsize=10)
    salvar(fig, f"05_frequencia_{nome}.png")


# ==== 6. qui-quadrado ====

def fig_quiquadrado(cifrado, nome, titulo, tamanho, nota):
    colunas = [cifrado[i::tamanho] for i in range(tamanho)]
    por_linha = min(tamanho, 4)
    nlin = -(-tamanho // por_linha)
    alt = 2.9 * nlin + 1.5  # altura em polegadas; margens abaixo são em polegadas / alt
    fig, eixos = plt.subplots(nlin, por_linha, figsize=(3.4 * por_linha, alt),
                              squeeze=False, sharey=True)
    fig.subplots_adjust(left=0.07, right=0.98, top=1 - 1.45 / alt, bottom=0.65 / alt,
                        hspace=0.75, wspace=0.12)
    todos = []
    for idx, ax in enumerate(eixos.flat):
        if idx >= tamanho:
            ax.axis("off")
            continue
        col = colunas[idx]
        cont = v.contar_letras(col)
        scores = [v.qui_quadrado(cont[d:] + cont[:d], len(col)) for d in range(26)]
        melhor = min(range(26), key=lambda d: scores[d])
        ordenados = sorted(scores)
        todos += scores
        ax.plot(range(26), scores, color=AZUL_CLARO, linewidth=2, zorder=2)
        ax.plot(range(26), scores, "o", color=AZUL, markersize=3.5, zorder=3)
        ax.plot([melhor], [scores[melhor]], "o", color=LARANJA, markersize=10,
                markeredgecolor=FUNDO, markeredgewidth=2, zorder=4)
        ax.set_yscale("log")
        ax.set_xticks([0, 4, 8, 12, 16, 20, 25])
        ax.set_xticklabels([v.ALFABETO[i] for i in (0, 4, 8, 12, 16, 20, 25)])
        ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        empates = sum(1 for s in scores if abs(s - ordenados[0]) < 1e-9)
        extra = f" · {empates} empatados" if empates > 1 else f" · 2º: {num(ordenados[1], 1)}"
        ax.set_title(f"col {idx} ({len(col):,} ".replace(",", ".")
                     + ("letra)" if len(col) == 1 else "letras)")
                     + f"\nmenor χ²: '{v.ALFABETO[melhor]}' = {num(scores[melhor], 1)}{extra}",
                     loc="left", fontsize=9.5, color=TINTA_2)
        ax.annotate(v.ALFABETO[melhor], (melhor, scores[melhor]), xytext=(9, -2),
                    textcoords="offset points", fontsize=13, fontweight="bold", color=TINTA)
    # eixo y comum (sharey) com folga para o ponto mínimo e o rótulo
    eixos[0][0].set_ylim(min(todos) / 3, max(todos) * 2)
    fig.supxlabel("deslocamento testado (letra da senha)", fontsize=10, color=TINTA_2,
                  y=0.12 / alt)
    fig.text(0.07, 1 - 0.4 / alt, titulo, fontsize=14, fontweight="bold", color=TINTA)
    fig.text(0.07, 1 - 0.75 / alt, nota, fontsize=10, color=TINTA_2)
    salvar(fig, f"06_quiquadrado_{nome}.png")


# ==== 7. resultado ====

def fig_resultado(casos):
    """Original vs. recuperado, letra por letra, para cada tentativa de quebra."""
    largura = max(len(c["original"]) for c in casos)
    linhas = len(casos) * 3.2 + 0.4
    fig, ax = grade(largura + 6.5, linhas / 1.35, rotulo=4.6)
    titulo_grade(ax, "Resultado: o que o ataque recuperou sem saber a senha",
                 "verde = letra certa · vermelho = letra errada", rotulo=4.6)
    y = -1.9
    for caso in casos:
        orig, rec = caso["original"], caso["recuperado"]
        ax.text(-4.4, y + 1.35, caso["nome"], fontsize=11.5, fontweight="bold", color=TINTA)
        rotulo_linha(ax, y, "original", 4.6)
        rotulo_linha(ax, y - 1.1, "recuperado", 4.6)
        acertos = 0
        for i, (a, b) in enumerate(zip(orig, rec)):
            quadrado(ax, i * PASSO, y, a)
            certo = a == b
            acertos += certo
            quadrado(ax, i * PASSO, y - 1.1, b, fundo=BOM if certo else RUIM, tinta="#ffffff")
        xr = largura * PASSO + 0.5
        ok = caso["senha"] == SENHA
        ax.text(xr, y + 0.5, f"senha achada: {caso['senha']}  {'✓' if ok else '✗'}",
                fontsize=11, color=BOM if ok else RUIM, va="center", fontweight="bold")
        ax.text(xr, y - 0.6, caso.get("resumo", f"{acertos}/{len(orig)} letras certas"),
                fontsize=10.5, color=TINTA_2, va="center")
        y -= 3.2
    salvar(fig, "07_resultado.png")


# ==== montagem ====

def main():
    print("Gerando imagens em", SAIDA)
    fig_visao_geral()

    # --- frases curtas ---
    aye = "Aye Mak Sicur"
    gdm = "G.D.M. IS ONLINE"
    aye_h, gdm_h = v.higienizar(aye), v.higienizar(gdm)
    aye_c, gdm_c = v.cifrar(aye_h, SENHA), v.cifrar(gdm_h, SENHA)

    fig_higienizacao(aye, "aye", "Higienização: 'Aye Mak Sicur'")
    fig_higienizacao(gdm, "gdm", "Higienização: 'G.D.M. IS ONLINE'")

    # --- Dom Casmurro: trecho do capítulo I, na posição real dentro do livro ---
    bruto = v.ler_arquivo(RAIZ / "DomCasmurro.txt")
    trecho = "conheço de vista e\r\nde chapéo."
    pos_bruto = bruto.find(trecho)
    assert pos_bruto >= 0, "trecho não encontrado no DomCasmurro.txt"
    inicio = len(v.higienizar(bruto[:pos_bruto]))  # posição da 1ª letra no texto limpo
    livro = v.higienizar(bruto)
    livro_c = v.cifrar(livro, SENHA)
    trecho_limpo = v.higienizar(trecho)
    assert livro[inicio:inicio + len(trecho_limpo)] == trecho_limpo

    fig_higienizacao("conheço de vista e de chapéo.", "dom",
                     "Higienização: trecho do capítulo I de Dom Casmurro")

    fig_cifra(aye_h, "aye", "Cifra: 'ayemaksicur' com a senha 'segredo'")
    fig_cifra(gdm_h, "gdm", "Cifra: 'gdmisonline' com a senha 'segredo'")
    fig_cifra(trecho_limpo, "dom", "Cifra: o trecho de Dom Casmurro", inicio=inicio,
              nota=f"a 1ª letra está na posição {inicio:,} do livro".replace(",", ".")
                   + f", então a senha começa em '{SENHA[inicio % 7]}'")
    # confere o trecho com a cifra do livro inteiro
    trecho_c = "".join(chr((ord(p) - 97 + ord(SENHA[(inicio + i) % 7]) - 97) % 26 + 97)
                       for i, p in enumerate(trecho_limpo))
    assert livro_c[inicio:inicio + len(trecho_limpo)] == trecho_c

    fig_colunas(aye_c, "aye", "Colunas: 'sckdengagai' em 7 colunas")
    fig_colunas(gdm_c, "gdm", "Colunas: 'yhszwrbdmtv' em 7 colunas")
    fig_colunas(livro_c, "dom", "Colunas: Dom Casmurro cifrado em 7 colunas")

    r_aye = fig_ic(aye_c, "aye", "Índice de Coincidência: 'sckdengagai'",
                   f"11 letras · k = 2 ganha por acaso: as colunas '{aye_c[0::2]}' e '{aye_c[1::2]}' "
                   "têm letras repetidas")
    r_gdm = fig_ic(gdm_c, "gdm", "Índice de Coincidência: 'yhszwrbdmtv'",
                   "11 letras, nenhuma repetida em coluna nenhuma: IC = 0 para todo k, não há o que escolher")
    r_dom = fig_ic(livro_c, "dom", "Índice de Coincidência: Dom Casmurro cifrado",
                   "308.887 letras · só k = 7 deixa cada coluna com um único deslocamento")

    fig_frequencia(livro_c, "dom", "Frequência da coluna 0 do Dom Casmurro cifrado")

    fig_quiquadrado(livro_c, "dom", "Qui-quadrado: Dom Casmurro, as 7 colunas",
                    7, "26 deslocamentos por coluna · um vale sozinho (escala log): s e g r e d o")
    fig_quiquadrado(aye_c, "aye", "Qui-quadrado: 'sckdengagai' com k = 2 (escolha do programa)",
                    r_aye["tamanho"], "com 5–6 letras por coluna o mínimo existe, mas não quer dizer nada")
    fig_quiquadrado(gdm_c, "gdm_t7", "Qui-quadrado: 'yhszwrbdmtv' forçando k = 7",
                    7, "1 ou 2 letras por coluna: vence o deslocamento que leva essas letras para as mais comuns do português")

    r_aye7 = v.quebrar(aye_c, tamanho=7)
    r_gdm7 = v.quebrar(gdm_c, tamanho=7)
    fig_resultado([
        {"nome": "Dom Casmurro (trecho do cap. I, 308.887 letras no total)",
         "original": trecho_limpo,
         "recuperado": r_dom["texto"][inicio:inicio + len(trecho_limpo)],
         "senha": r_dom["chave"],
         "resumo": f"livro inteiro: {sum(a == b for a, b in zip(livro, r_dom['texto'])):,} / "
                   f"{len(livro):,} letras certas".replace(",", ".")},
        {"nome": "'Aye Mak Sicur' — automático (k = 2)", "original": aye_h,
         "recuperado": r_aye["texto"], "senha": r_aye["chave"]},
        {"nome": "'Aye Mak Sicur' — forçando k = 7", "original": aye_h,
         "recuperado": r_aye7["texto"], "senha": r_aye7["chave"]},
        {"nome": "'G.D.M. IS ONLINE' — automático (k = 1)", "original": gdm_h,
         "recuperado": r_gdm["texto"], "senha": r_gdm["chave"]},
        {"nome": "'G.D.M. IS ONLINE' — forçando k = 7", "original": gdm_h,
         "recuperado": r_gdm7["texto"], "senha": r_gdm7["chave"]},
    ])


if __name__ == "__main__":
    main()
