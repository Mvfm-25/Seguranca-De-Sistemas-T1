# Cifra de Vigenère: criptografia e criptoanálise

## O problema

O trabalho pede dois algoritmos em Python, Java ou C++:

1. **Criptografia:** ler um `.txt`, higienizar o texto (minúsculas, sem acentos, só `a` a `z`) e cifrar com a Cifra de Vigenère usando uma senha dada pelo usuário.
2. **Criptoanálise:** recuperar o texto original **sem conhecer a senha**, assumindo que o texto está em português. O ataque tem duas etapas:
   - descobrir o tamanho da senha pelo Índice de Coincidência (IC);
   - descobrir cada letra da senha por análise de frequência.

O código também precisa ser organizado, funcionar com arquivos grandes e ser explicável por qualquer integrante do grupo.

## As soluções

Tudo está em `vigenere.py`, usado pela linha de comando:

```
python vigenere.py cifrar   DomCasmurro.txt -k segredo
python vigenere.py quebrar  texto_criptografado.txt
python vigenere.py decifrar texto_criptografado.txt -k segredo
```

| Problema | Solução |
|---|---|
| **Higienizar o texto** | O texto vai para minúsculas e passa pela normalização Unicode NFD, que separa cada acento da sua letra (`á` vira `a` + `´`). Depois disso, todo caractere que não é de `a` a `z` é descartado, o que inclui os acentos soltos, a pontuação, os números e os espaços. |
| **Cifrar e decifrar** | Cada letra usa a fórmula `C = (P + K) mod 26`, e decifrar usa `P = (C − K) mod 26`. Todas as letras que usam a mesma letra da chave são deslocadas de uma vez com `str.translate`, e não uma por uma. |
| **Descobrir o tamanho da senha** | Para cada tamanho *k* de 1 a 10, o texto é dividido em *k* colunas e o programa calcula o IC médio delas. O tamanho certo dá um IC perto do português (~0,074); os errados ficam perto do aleatório (~0,038). Como os múltiplos do tamanho certo também dão IC alto, o programa escolhe o **menor tamanho que chega a 90% do melhor IC**. |
| **Descobrir cada letra da senha** | Em cada coluna, o programa testa os 26 deslocamentos possíveis e compara a frequência das letras com a do português usando o **qui-quadrado**. O deslocamento com a menor distância é a letra da chave naquela posição. |
| **Reconstruir o texto** | Com a senha encontrada, o texto é decifrado normalmente e salvo em `texto_quebrado.txt`. |
| **Arquivos grandes** | Tanto a cifra quanto a contagem de letras usam operações nativas de string do Python. O *Dom Casmurro* inteiro (~309 mil letras) é cifrado ou quebrado em cerca de 0,2 s. |

## Exemplo passo a passo: cifrando `gdmisonline`

Senha: `segredo`. Cada letra vira sua posição no alfabeto (a=0 … z=25), a senha se repete até cobrir o texto e cada par é somado com `C = (P + K) mod 26`:

| Pos. | Texto (P) | Senha (K) | P + K | mod 26 | Cifrado |
|---|---|---|---|---|---|
| 0 | g = 6 | s = 18 | 24 | 24 | **y** |
| 1 | d = 3 | e = 4 | 7 | 7 | **h** |
| 2 | m = 12 | g = 6 | 18 | 18 | **s** |
| 3 | i = 8 | r = 17 | 25 | 25 | **z** |
| 4 | s = 18 | e = 4 | 22 | 22 | **w** |
| 5 | o = 14 | d = 3 | 17 | 17 | **r** |
| 6 | n = 13 | o = 14 | 27 | 1 | **b** |
| 7 | l = 11 | s = 18 | 29 | 3 | **d** |
| 8 | i = 8 | e = 4 | 12 | 12 | **m** |
| 9 | n = 13 | g = 6 | 19 | 19 | **t** |
| 10 | e = 4 | r = 17 | 21 | 21 | **v** |

Resultado: **`yhszwrbdmtv`**. Decifrar com `segredo` devolve `gdmisonline`. ✔

- Nas posições 6 e 7 a soma passa de 25, e o `mod 26` faz a volta no alfabeto.
- A mesma letra do texto vira letras diferentes: o `i` vira `z` e `m`, e o `n` vira `b` e `t`. Isso esconde a frequência das letras, e por isso a análise de frequência direta não funciona contra a Vigenère.
- No código, as letras que usam a mesma letra da senha (posições `i`, `i+7`, `i+14`…) são deslocadas juntas com `str.translate`. Por exemplo, as posições 0 e 7 (`gl`) recebem +18 de uma vez e viram `yd`. Cada um desses grupos é, na prática, uma cifra de César.

## Exemplo passo a passo: quebrando a cifra

### Etapa 1: tamanho da senha (Índice de Coincidência)

O texto cifrado é dividido em *k* colunas e o programa calcula o IC médio delas. Com o *Dom Casmurro* cifrado com `segredo`, o resultado foi:

```
k    IC médio
1    0.0468
...
6    0.0468
7    0.0768   <<  perto do português (~0.0745)
8    0.0468
...
10   0.0468
```

- **Com o k errado:** cada coluna mistura deslocamentos diferentes, a distribuição fica achatada e o IC se aproxima do aleatório (~0,038).
- **Com k = 7:** cada coluna usa um único deslocamento, a distribuição do português se mantém e o IC sobe.

### Etapa 2: letras da senha (frequência + qui-quadrado)

Para cada coluna (~44 mil letras cada), o programa testa os 26 deslocamentos e fica com o de menor χ² em relação ao português:

| Coluna | Letras cifradas mais comuns | Melhor (χ²) | 2º melhor (χ²) | Letra da senha |
|---|---|---|---|---|
| 0 | s w g | **s** (1.437) | d (338.735) | **s** |
| 1 | e i s | **e** (1.136) | d (325.971) | **e** |
| 2 | g k u | **g** (1.630) | f (325.137) | **g** |
| 3 | r v f | **r** (1.569) | q (323.395) | **r** |
| 4 | e i s | **e** (1.128) | d (358.772) | **e** |
| 5 | d h r | **d** (1.414) | c (352.365) | **d** |
| 6 | o s c | **o** (1.121) | n (334.491) | **o** |

Na coluna 0, as letras `s`, `w` e `g` são **a, e, o** (as mais comuns do português) deslocadas 18 casas, e 18 é a letra `s`. A diferença entre o melhor e o segundo melhor χ² é enorme, então não há dúvida sobre a letra.

### Etapa 3: reconstrução

Com a senha `segredo`, o texto é decifrado com `P = (C − K) mod 26`. O resultado é idêntico ao original higienizado.

## Resultados dos testes

### ✔ O que funcionou

| Teste | Tamanho do texto | Tamanho encontrado | Senha encontrada |
|---|---|---|---|
| *Dom Casmurro* completo, senha `segredo` | ~309 mil letras | 7 | `segredo` ✔ |
| *Dom Casmurro* completo, senha `criptografia` (com `-m 20`) | ~309 mil letras | 12 | `criptografia` ✔ |
| Trecho do *Dom Casmurro*, senha `abacaxi` | ~3.000 caracteres | 7 | `abacaxi` ✔ |
| Cifrar e decifrar `gdmisonline` com `segredo` | 11 letras | não se aplica | `yhszwrbdmtv` e de volta `gdmisonline` ✔ |

### ✘ O que não funcionou

| Teste | Resultado | Esperado |
|---|---|---|
| Quebrar `yhszwrbdmtv` sem a senha | IC = 0,0000 em todos os tamanhos, o programa escolhe k = 1, senha `n`, texto `lufmjeoqzgi` | k = 7, `segredo` |
| O mesmo, forçando o tamanho certo (`-t 7`) | senha `ktpvwrb`, texto sem sentido | `segredo` |

### Por quê

A **cifragem e a decifragem** são operações exatas: com a senha em mãos, funcionam para qualquer tamanho de texto, até uma única letra.

A **quebra** é **estatística**. Ela depende de duas coisas que só aparecem com volume:

1. **O IC precisa de letras repetidas dentro de cada coluna.** Com 11 letras divididas em 7 colunas, cada coluna tem 1 ou 2 letras, nenhuma repetição acontece e o IC dá zero para todos os tamanhos. Sem diferença entre os tamanhos, não há como escolher o certo.
2. **A análise de frequência precisa de uma amostra que se pareça com o português.** Uma coluna com as letras `y` e `d` não tem distribuição nenhuma para comparar, e qualquer deslocamento parece tão bom quanto os outros.

Em outras palavras, o ataque explora o fato de a senha se **repetir muitas vezes**, o que transforma a Vigenère em várias cifras de César, cada uma quebrável por frequência. Em `gdmisonline` a senha de 7 letras mal chega a se repetir, então não há padrão para explorar.

**Regra prática:** o ataque precisa de algumas centenas de letras por coluna. Nos testes, cerca de 3.000 caracteres bastaram para uma senha de 7 letras. Senhas mais longas pedem textos proporcionalmente maiores.
