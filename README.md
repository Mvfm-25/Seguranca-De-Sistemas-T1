# Cifra de Vigenère: criptografia e criptoanálise

Trabalho 1 de Segurança de Sistemas (PUCRS). Implementação em Python da **Cifra de Vigenère** e de um
**ataque** que a quebra sem conhecer a senha: o tamanho da senha vem do Índice de Coincidência e
cada letra vem da análise de frequência do português (qui-quadrado). Enunciado em
[`Segurança_de_Sistemas___T1_Venegre.pdf`](Segurança_de_Sistemas___T1_Venegre.pdf).

- [`RESUMO.md`](RESUMO.md): o problema, as soluções e os exemplos passo a passo, em uma página.
- [`docs/MANUAL.md`](docs/MANUAL.md): que comando usar, quando e por quê; roteiro da apresentação.
- [`docs/ANALISE.md`](docs/ANALISE.md): como a implementação funciona, função por função, e o
  desempenho medido.
- [`docs/VISUALIZACAO.md`](docs/VISUALIZACAO.md): passo a passo em imagens — higienização, cifra
  com `segredo` e quebra de `Aye Mak Sicur`, `G.D.M. IS ONLINE` e *Dom Casmurro*.
- [`docs/TEORIA.md`](docs/TEORIA.md): por que funciona — Vigenère, Índice de Coincidência,
  qui-quadrado e quando o ataque falha.

## Uso

Só Python 3 (biblioteca padrão).

```powershell
python vigenere.py cifrar     DomCasmurro.txt -k segredo     # → texto_criptografado.txt
python vigenere.py quebrar    texto_criptografado.txt        # → tamanho, senha, texto_quebrado.txt
python vigenere.py decifrar   texto_criptografado.txt -k segredo
python vigenere.py higienizar DomCasmurro.txt                # → texto_higienizado.txt
```

Opções úteis:

- `-k` omitido: a senha é perguntada no terminal.
- `quebrar -m N`: testa senhas de até N letras (padrão 10).
- `quebrar -t N`: força o tamanho da senha.
- `-o arquivo`: muda o arquivo de saída; `--preview N`: letras mostradas no terminal.

## Resultado

*Dom Casmurro* (308 887 letras) cifrado com `segredo` e quebrado em ~0,05 s:

```
    6  0.0468  ########################
    7  0.0768  ########################################  <<
    8  0.0468  ########################

Tamanho estimado da senha: 7
Senha encontrada: segredo
```

## Licença

GPL-3.0 — ver [`LICENSE`](LICENSE).
