# Manual do `vigenere.py`

Este manual explica **que comando usar, quando e por quê**. Para os detalhes internos da
implementação, veja [`ANALISE.md`](ANALISE.md); para a teoria da cifra e do ataque,
[`TEORIA.md`](TEORIA.md); para os requisitos, o enunciado em
[`../Segurança_de_Sistemas___T1_Venegre.pdf`](../Segurança_de_Sistemas___T1_Venegre.pdf).

---

## 1. A ideia em uma frase

O programa **cifra** um texto com a Cifra de Vigenère e depois **quebra** essa cifra sem a senha:
descobre o tamanho da senha pelo Índice de Coincidência e cada letra dela pela frequência das letras
do português.

```
 texto.txt ──cifrar(senha)──▶ texto_criptografado.txt ──quebrar──▶ texto_quebrado.txt
                                         │                          + tamanho e senha
                                         └──decifrar(senha)──▶ texto_decifrado.txt
```

---

## 2. Instalação

Nenhuma. Só é preciso Python 3 (testado com 3.13); o programa usa apenas a biblioteca padrão.

```powershell
cd C:\GDM-05\prog\pucrs\Seguranca-De-Sistemas-T1
python vigenere.py --help
```

---

## 3. Qual comando usar?

| Eu quero… | Comando | Por quê |
|---|---|---|
| Cifrar um texto com uma senha | `cifrar` | Higieniza e cifra: é a Parte 1 do enunciado. |
| Quebrar um texto cifrado sem saber a senha | `quebrar` | IC + frequência: é a Parte 2 do enunciado. |
| Decifrar sabendo a senha | `decifrar` | Confere que a cifra é reversível ou desfaz um teste. |
| Ver só o texto higienizado | `higienizar` | Mostra isoladamente o passo obrigatório 1 (minúsculas, sem acento, só `a`–`z`). |

---

## 4. Os comandos em detalhe

Todos os comandos recebem um arquivo de entrada e gravam o resultado em outro arquivo (`-o`).
Qualquer entrada é higienizada antes de ser processada, então é possível passar um `.txt` com
acentos, pontuação e quebras de linha.

### 4.1 `cifrar` — texto → texto cifrado

```powershell
python vigenere.py cifrar DomCasmurro.txt -k segredo
python vigenere.py cifrar DomCasmurro.txt                 # pergunta a senha
python vigenere.py cifrar meu.txt -k segredo -o saida.txt
```

| Opção | Padrão | Efeito |
|---|---|---|
| `-k`, `--chave` | pergunta | Senha. Também é higienizada: `Segrêdo!` equivale a `segredo`. |
| `-o`, `--saida` | `texto_criptografado.txt` | Arquivo de saída. |

Saída: `Texto cifrado (308887 letras) salvo em texto_criptografado.txt`.

### 4.2 `quebrar` — texto cifrado → senha e texto

```powershell
python vigenere.py quebrar texto_criptografado.txt
python vigenere.py quebrar texto_criptografado.txt -m 20      # senhas de até 20 letras
python vigenere.py quebrar texto_criptografado.txt -t 7       # pula a etapa 1, força tamanho 7
```

| Opção | Padrão | Efeito |
|---|---|---|
| `-m`, `--max` | `10` | Maior tamanho de senha testado na etapa 1. Senhas maiores não são encontradas. |
| `-t`, `--tamanho` | (estimado) | Força o tamanho da senha e pula a escolha automática. A tabela de IC ainda é mostrada. |
| `-o`, `--saida` | `texto_quebrado.txt` | Arquivo com o texto decifrado. |
| `--preview` | `300` | Quantas letras do texto decifrado mostrar no terminal. |

Saída com o *Dom Casmurro* cifrado com `segredo`:

```
Índice de Coincidência por tamanho de chave
(português ~ 0.0745, aleatório ~ 0.0385)

    1  0.0468  ########################
    ...
    6  0.0468  ########################
    7  0.0768  ########################################  <<
    8  0.0468  ########################
    ...

Tamanho estimado da senha: 7
Senha encontrada: segredo
Texto decifrado salvo em texto_quebrado.txt

Começo do texto:
theprojectgutenbergebookofdomcasmurrothisebookisfortheuseofanyone...
```

Como ler:

- **A tabela é a etapa 1.** Cada linha é um tamanho testado; a barra é proporcional ao IC. O tamanho
  certo se destaca, com IC perto do português; os errados ficam baixos. `<<` marca o escolhido.
- **Múltiplos também sobem.** Com `-m 20`, o 14 aparece tão alto quanto o 7. O programa escolhe o
  **menor** tamanho com IC a pelo menos 90% do maior (TEORIA §4.5).
- **O começo do texto em inglês é esperado:** o arquivo do Projeto Gutenberg começa com um
  cabeçalho em inglês. O português começa logo depois.

### 4.3 `decifrar` — texto cifrado + senha → texto

```powershell
python vigenere.py decifrar texto_criptografado.txt -k segredo
```

| Opção | Padrão | Efeito |
|---|---|---|
| `-k`, `--chave` | pergunta | Senha. |
| `-o`, `--saida` | `texto_decifrado.txt` | Arquivo de saída. |
| `--preview` | `300` | Letras mostradas no terminal. |

### 4.4 `higienizar` — texto → só `a`–`z`

```powershell
python vigenere.py higienizar DomCasmurro.txt
```

Grava `texto_higienizado.txt` (opção `-o` para mudar) e informa quantas letras sobraram. Útil para
comparar com o resultado do `quebrar`: os dois arquivos devem ser idênticos.

---

## 5. Receitas

```powershell
# Teste recomendado no enunciado: cifrar e quebrar o Dom Casmurro com "segredo"
python vigenere.py cifrar  DomCasmurro.txt -k segredo
python vigenere.py quebrar texto_criptografado.txt

# Conferir que o texto quebrado é idêntico ao original higienizado
python vigenere.py higienizar DomCasmurro.txt
fc.exe texto_higienizado.txt texto_quebrado.txt          # Git Bash: cmp texto_higienizado.txt texto_quebrado.txt

# Senha longa: aumentar o tamanho máximo testado
python vigenere.py cifrar  DomCasmurro.txt -k criptografia
python vigenere.py quebrar texto_criptografado.txt -m 20

# Ver a tabela de IC mostrar os divisores da senha (6 aparece alto para "criptografia")
python vigenere.py quebrar texto_criptografado.txt -m 20 --preview 0

# Arquivo fornecido pelo professor na apresentação, sem saber a senha
python vigenere.py quebrar arquivo_do_professor.txt -m 20

# Exemplo pequeno do RESUMO.md (cifrar e decifrar funcionam; quebrar erra, de propósito)
python vigenere.py cifrar   gdm.txt -k segredo                 # yhszwrbdmtv
python vigenere.py decifrar texto_criptografado.txt -k segredo # gdmisonline
python vigenere.py quebrar  texto_criptografado.txt            # IC 0 em tudo; senha n, texto errado
```

---

## 6. Roteiro para a apresentação

O enunciado pede que cada integrante saiba explicar **a cifra, o ataque e o código**. Uma sequência
que cobre os três em poucos minutos:

| Passo | Mostrar | Explicar | Onde está |
|---|---|---|---|
| 1 | `higienizar` em um texto com acentos | Por que só 26 letras; NFD separa o acento | TEORIA §3, `higienizar` |
| 2 | `cifrar gdm.txt -k segredo` | `C = (P + K) mod 26`, a senha repetida; a mesma letra vira letras diferentes | RESUMO (exemplo passo a passo), TEORIA §2 |
| 3 | `cifrar DomCasmurro.txt -k segredo` | Arquivo grande em milissegundos: cifra por colunas com `translate` | ANALISE §3.4 |
| 4 | `quebrar` e a tabela de IC | Vigenère = 7 Césares; IC alto só no tamanho certo; múltiplos e a regra dos 90% | TEORIA §4 |
| 5 | A senha encontrada | χ² por coluna; o certo é ~235× menor que o segundo | TEORIA §5 |
| 6 | `quebrar` no `texto_criptografado.txt` de `gdm.txt` | Por que o ataque falha em texto curto: IC 0 em todos os tamanhos | TEORIA §6.1, RESUMO |

Perguntas prováveis e onde está a resposta:

- *Por que o IC do tamanho certo é igual ao do português?* — TEORIA §4.2: César não muda o IC.
- *Por que os tamanhos errados dão 0,0468 e não 0,0385?* — TEORIA §4.4.
- *Por que não pegar simplesmente o maior IC?* — TEORIA §4.5 e ANALISE `escolher_tamanho`.
- *Por que qui-quadrado e não "a letra mais comum é o `a`"?* — TEORIA §5.5.
- *Quanto texto o ataque precisa?* — TEORIA §6.1: ~2 000 letras para uma senha de 7.
- *O que tornaria a Vigenère segura?* — TEORIA §6.2: senha aleatória do tamanho do texto (*one-time
  pad*).

---

## 7. Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `Erro: a chave precisa ter pelo menos uma letra de a a z` | Senha só com números ou símbolos | Use uma senha com letras. |
| `Erro: [Errno 2] No such file or directory` | Caminho errado | Confira o nome; caminhos com espaço vão entre aspas. |
| `Texto cifrado vazio ou curto demais.` | Arquivo sem letras | Confira se é o arquivo certo. |
| Tamanho estimado 1 e senha de uma letra, texto ilegível | Senha maior que `-m` | Rode de novo com `-m 20` (ou maior). |
| Tamanho certo, senha com uma letra errada (`segredg`), texto "quase" legível | Texto curto: poucas letras por coluna | Use um texto maior; ver TEORIA §6.1. |
| Senha encontrada é a "metade" da usada (`ab` para `abab`) | A senha é periódica | Não é erro: `ab` decifra o texto igual (TEORIA §2.4). |
| IC igual a 0 em todos os tamanhos, tabela sem barras | Texto muito curto (cada coluna com 1–2 letras, sem repetição) | O ataque não se aplica; é preciso mais texto. |
| Um tamanho pequeno com IC **acima** do português (ex.: 0,0833) | Texto curto: duas letras iguais numa coluna de 5 já dão IC alto por acaso | O valor não significa nada com tão poucas letras; ver TEORIA §6.1. |
| Texto decifrado começa em inglês | Cabeçalho do Projeto Gutenberg | Esperado; o romance começa depois. |
| Acentos quebrados na saída (`Ã­ndice`) | Console antigo sem UTF-8 | O programa já força UTF-8; use o Windows Terminal ou `chcp 65001`. |

---

## 8. Limitações

- O ataque assume **texto em português**; textos em outra língua quebram pior ou não quebram.
- Senhas maiores que `-m` não são encontradas, e o programa não avisa.
- Precisa de texto suficiente: algumas centenas de letras **por coluna** (~2 000 letras para uma
  senha de 7).
- Letras sem decomposição (`ß`, `ø`, `º`) são removidas na higienização, não convertidas.
