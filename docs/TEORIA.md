# Teoria da Cifra de Vigenère e do seu ataque

Este documento explica **por que** o trabalho funciona: como a Vigenère esconde a frequência das
letras, por que essa proteção é fraca e por que o Índice de Coincidência e o qui-quadrado conseguem
recuperar a senha sem conhecê-la. Ele não depende do código; quando cita um número, o número foi
medido com a implementação (`vigenere.py`) sobre o *Dom Casmurro*.

- Requisitos: enunciado em [`../Segurança_de_Sistemas___T1_Venegre.pdf`](../Segurança_de_Sistemas___T1_Venegre.pdf).
- Como cada função foi implementada: [`ANALISE.md`](ANALISE.md).
- Que comando usar: [`MANUAL.md`](MANUAL.md).
- Resumo de uma página com exemplos: [`../RESUMO.md`](../RESUMO.md).

---

## 1. Cifras de substituição em uma página

Uma **cifra de substituição** troca cada letra do texto por outra, segundo uma regra secreta. A mais
simples é a **cifra de César**: todas as letras andam o mesmo número de casas no alfabeto.

```
deslocamento 3:   a b c d e f g ... x y z
                  ↓ ↓ ↓ ↓ ↓ ↓ ↓     ↓ ↓ ↓
                  d e f g h i j ... a b c
```

Ela tem dois defeitos fatais:

1. **Só existem 26 chaves.** Basta testar todas.
2. **A frequência das letras sobrevive.** Em português, `a` e `e` somam mais de 25% das letras. Se
   no texto cifrado a letra mais comum é `d`, provavelmente `d` é o `a` deslocado 3 casas. Isso é a
   **análise de frequência**, conhecida desde al-Kindi (século IX).

A Vigenère (século XVI) foi criada para resolver o segundo defeito, e por quase 300 anos foi chamada
de *le chiffre indéchiffrable*. Ela só caiu no século XIX (Babbage, Kasiski) e ganhou a ferramenta
estatística usada neste trabalho em 1920, com o Índice de Coincidência de Friedman.

---

## 2. A Cifra de Vigenère

### 2.1 A fórmula

Cada letra vira um número (`a = 0`, `b = 1`, …, `z = 25`). A senha é repetida ao longo do texto, e
cada letra do texto é somada à letra da senha que está embaixo dela, **módulo 26**:

```
cifrar:    C[i] = (P[i] + K[i mod L]) mod 26
decifrar:  P[i] = (C[i] − K[i mod L]) mod 26

P = texto claro, C = texto cifrado, K = senha, L = tamanho da senha
```

O `mod 26` faz o alfabeto "dar a volta": `o (14) + s (18) = 32`, e `32 mod 26 = 6`, que é `g`.

```
texto:   g d m i s o n l i n e
senha:   s e g r e d o s e g r      ← "segredo" repetida
cifrado: y h s z w r b d m t v
```

O exemplo completo, letra por letra, está no [`RESUMO.md`](../RESUMO.md).

### 2.2 Uma Vigenère são L cifras de César intercaladas

Esta é a observação que derruba a cifra. Com `segredo` (L = 7), as letras nas posições
0, 7, 14, 21… são **todas** somadas a `s`; as posições 1, 8, 15… são somadas a `e`; e assim por
diante:

```
posição:  0 1 2 3 4 5 6 | 7 8 9 10 11 12 13 | 14 15 ...
chave:    s e g r e d o | s e g r  e  d  o  | s  e  ...
           ╰──────────────╯─────────────────────╯
           coluna 0 = posições 0, 7, 14, ... → todas deslocadas por s (18)
```

Se separarmos o texto cifrado em 7 **colunas** (em Python, `texto[i::7]`), cada coluna é uma cifra
de César comum, e César se quebra por frequência. O ataque inteiro se resume a duas perguntas:

1. **Quantas colunas?** (o tamanho L da senha) → Índice de Coincidência, seção 4.
2. **Qual o deslocamento de cada coluna?** (cada letra da senha) → análise de frequência, seção 5.

### 2.3 Por que a frequência "some"

No texto cifrado inteiro, a mesma letra do texto vira letras diferentes conforme a posição: no
exemplo acima, o `i` vira `z` e `m`, e o `n` vira `b` e `t`. O `a` do português (14% das letras) é
espalhado entre 7 letras cifradas diferentes, cada uma recebendo ~2%. O histograma fica **achatado**
e a análise de frequência direta não encontra um pico para seguir.

Mas ele não fica **plano**: a mistura de 7 alfabetos deslocados ainda guarda alguma irregularidade,
e é essa sobra que a seção 4 mede.

### 2.4 Senhas que são menores do que parecem

O que importa não é o comprimento da senha digitada, e sim o seu **período**. `abab` cifra
exatamente como `ab`; `aaaa` não cifra nada (`a = 0`). Medido no projeto: o ataque devolve `ab`
para um texto cifrado com `abab`, `se` para `sese` e `a` para `aaaa`. As três respostas estão
corretas: decifram o texto.

---

## 3. Higienização: por que só `a` a `z`

A fórmula da seção 2.1 só faz sentido num alfabeto fixo de 26 símbolos. Por isso, antes de cifrar,
o enunciado pede:

| Passo | Exemplo | Motivo |
|---|---|---|
| Minúsculas | `A` → `a` | `A` e `a` são a mesma letra para a estatística. |
| Remover acentos | `ç` → `c`, `ã` → `a` | `ã` não tem número no alfabeto de 26. |
| Remover pontuação, números e espaços | `"Bentinho, 1899"` → `bentinho` | Não são letras; espaços, se mantidos, entregariam o tamanho das palavras. |

A remoção de acentos usa a **normalização Unicode NFD** (*Canonical Decomposition*). Em Unicode,
`á` pode ser escrito como um único caractere ou como `a` seguido do acento agudo "combinante"
(U+0301). A NFD força a segunda forma; depois disso, basta descartar tudo que não é `a`–`z`, e os
acentos soltos vão junto:

```
"Ação"  ──lower──▶ "ação" ──NFD──▶ "a" "c" "◌̧" "a" "◌̃" "o" ──só a-z──▶ "acao"
```

A higienização tem um custo para o ataque: o português sem acentos tem uma distribuição de letras um
pouco diferente da do português acentuado (o `a` absorve `á`, `à`, `â`, `ã`). Por isso a tabela de
frequências usada na seção 5 é a de **letras já sem acento**.

---

## 4. Etapa 1: o Índice de Coincidência

### 4.1 Definição

O **Índice de Coincidência** (IC) de um texto é a probabilidade de que duas letras sorteadas ao
acaso (sem reposição) sejam **iguais**:

```
        Σ  f_c · (f_c − 1)
IC  =  ─────────────────────        f_c = quantas vezes a letra c aparece
             n · (n − 1)              n = total de letras
```

Exemplo à mão, `banana` (n = 6; `a` = 3, `n` = 2, `b` = 1):

```
IC = (3·2 + 2·1 + 1·0) / (6·5) = 8/30 = 0,267
```

Para um texto longo, o IC tende a `Σ p_c²`, a soma dos quadrados das frequências da língua.

### 4.2 Os dois valores de referência

| Texto | IC | De onde vem |
|---|---|---|
| Aleatório (letras uniformes) | **1/26 ≈ 0,0385** | Cada letra com p = 1/26; `26 · (1/26)² = 1/26`. |
| Português higienizado | **≈ 0,0745–0,078** | Poucas letras muito comuns (`a`, `e`, `o`) elevam a soma dos quadrados. |
| *Dom Casmurro* higienizado (medido) | **0,0768** | 308 887 letras. |

O ponto central: **o IC não muda quando o alfabeto é permutado.** Uma cifra de César troca os nomes
das letras, mas não altera quantas vezes cada uma aparece; `Σ f_c(f_c − 1)` é a mesma soma, em outra
ordem. Logo, um texto cifrado por César tem o mesmo IC do português (0,0768), e uma Vigenère, que
mistura vários alfabetos, tem IC menor.

### 4.3 O teste: dividir em k colunas

Para cada tamanho candidato `k` (de 1 a 10, como pede o enunciado), o texto cifrado é dividido em
`k` colunas e calcula-se a **média** do IC das colunas:

- **k certo (k = L):** cada coluna usa uma única letra da senha, ou seja, é uma César pura. O IC de
  cada coluna é o do português. **IC alto.**
- **k errado:** cada coluna mistura posições de várias letras da senha. A distribuição fica achatada.
  **IC baixo.**

Resultado medido com o *Dom Casmurro* cifrado com `segredo`:

```
k     IC médio
1..6  0,0468
7     0,0768   ← igual ao IC do texto claro (seção 4.2)
8..13 0,0468
14    0,0768   ← múltiplo de 7
15..20 0,0468
```

### 4.4 Por que exatamente 0,0468 nos tamanhos errados

Com `k = 7`, cada coluna é uma César; o IC é o do português. Com `k` **não múltiplo** de 7, a coluna
`i` contém as posições `i, i+k, i+2k, …`, e essas posições caem em **todas** as 7 letras da senha
(7 é primo, então `k` e 7 não têm divisor comum). A coluna se torna uma mistura igual dos 7
alfabetos deslocados, e o IC dessa mistura pode ser calculado direto das frequências do texto claro
(`p`, medidas no *Dom Casmurro* higienizado):

```
p_mistura(c) = (1/7) · Σ_d p(c − d)     d ∈ {s, e, g, r, e, d, o}
IC_mistura   = Σ_c p_mistura(c)²  =  0,0469  (calculado)   vs.  0,0468  (medido)
```

Ela fica **acima** do aleatório (0,0385) porque 7 alfabetos não bastam para achatar totalmente a
distribuição, e porque `segredo` usa o `e` duas vezes (esse alfabeto pesa em dobro). Com `segrxdo`,
que tem 7 letras distintas, o IC do texto cifrado inteiro cai para 0,0434; com `abcdefg`, para
0,0416.

### 4.5 Senhas de tamanho composto: os divisores aparecem

Quando o tamanho da senha não é primo, os tamanhos errados não ficam todos iguais. Com
`criptografia` (L = 12), uma coluna de tamanho `k` contém `12 / mdc(k, 12)` posições diferentes da
senha. Quanto menos posições misturadas, maior o IC:

| k | mdc(k, 12) | Posições da senha por coluna | IC médio (medido) |
|---|---|---|---|
| 1, 5, 7, 11, 13… | 1 | 12 | 0,0415 |
| 2, 10, 14 | 2 | 6 | 0,0458 |
| 4, 8, 16, 20 | 4 | 3 | 0,0512 |
| 3, 9, 15 | 3 | 4 | 0,0514 |
| 6, 18 | 6 | 2 | 0,0625 |
| **12** | 12 | **1** | **0,0768** |

(As linhas de mdc 3 e 4 ficam quase empatadas e fora da ordem esperada porque a senha repete
letras: `r`, `i` e `a` aparecem duas vezes cada.)

Isso explica por que **não basta pegar o maior IC**:

- Os **múltiplos** do tamanho certo (14 para `segredo`, 24 para `criptografia`) têm o mesmo IC que
  ele: cada coluna continua sendo uma César, só que com menos letras. Escolher o máximo pode
  devolver o dobro da senha (que ainda decifraria, mas é a resposta errada para "tamanho da senha").
- Os **divisores** (6 para `criptografia`) têm IC intermediário, que pode parecer "bom" se comparado
  só com o aleatório.

A regra usada no projeto resolve os dois casos: **o menor `k` cujo IC chega a 90% do maior IC
medido**. No exemplo, 90% de 0,0768 é 0,0691; o `k = 6` (0,0625) fica abaixo, e o primeiro `k` que
passa é 12.

### 4.6 Outras formas de achar o tamanho (contexto)

O enunciado pede o IC por colunas, mas vale conhecer as alternativas clássicas:

- **Teste de Friedman:** estima L direto do IC do texto inteiro, sem dividir em colunas,
  `L ≈ (0,0768 − 0,0385) / (IC − 0,0385)`. É uma estimativa grosseira, porque assume que os alfabetos
  da senha se misturam como se fossem aleatórios. Medido: `segredo` → 4,6 (o certo é 7), `segrxdo`
  → 7,8, `abcdefg` → 12,1. Serve como palpite inicial, não como resposta.
- **Método de Kasiski:** procura sequências repetidas no texto cifrado (`the`, `que`…) e mede a
  distância entre elas; o tamanho da senha divide essas distâncias. Funciona bem com o olho humano,
  mas é mais trabalhoso de automatizar e mais sensível a coincidências.

O teste por colunas é o mais direto: em vez de estimar L, ele **verifica** cada candidato.

---

## 5. Etapa 2: análise de frequência com qui-quadrado

### 5.1 O problema de cada coluna

Com o tamanho conhecido, cada coluna é uma César com um deslocamento `d` desconhecido (0 a 25).
Basta descobrir qual dos 26 deslocamentos, quando desfeito, deixa a coluna **mais parecida com o
português**. Isso exige duas coisas: uma tabela de frequências de referência e uma medida de
"parecido".

### 5.2 A tabela de referência

Frequência das letras no português sem acentos (valores clássicos da literatura, os mesmos usados no
código), comparada com o *Dom Casmurro* higienizado:

| Letra | Tabela (%) | *Dom Casmurro* (%) |
|---|---|---|
| a | 14,63 | 14,25 |
| e | 12,57 | 13,07 |
| o | 10,73 | 10,24 |
| s | 7,81 | 7,57 |
| r | 6,53 | 6,10 |
| i | 6,18 | 6,29 |
| … | … | … |
| k, w, y | ≤ 0,02 | 0,05–0,14 |

As diferenças são pequenas: um romance de Machado não é a média do português, mas fica perto o
bastante. As letras `k`, `w` e `y` aparecem mais no livro do que na tabela por causa do cabeçalho e
da licença do Projeto Gutenberg, que estão em inglês (~15 mil das 309 mil letras, seção 6.3).

### 5.3 Desfazer um deslocamento é girar o histograma

Se a coluna foi deslocada `d` casas, a letra `c` do texto claro aparece como `c + d`. Então a
contagem do texto claro para a letra `c` é a contagem da letra cifrada `c + d`. Não é preciso
decifrar a coluna 26 vezes: basta **girar** a lista de 26 contagens.

```
contagem cifrada:   [a, b, c, ..., z]
desfazer d = 3:     [d, e, f, ..., z, a, b, c]    ← contagem[3:] + contagem[:3]
```

Testar os 26 deslocamentos custa 26 × 26 operações, não importa o tamanho do texto.

### 5.4 A medida: qui-quadrado (χ²)

Para cada deslocamento candidato, compara-se a contagem observada `O_c` com a esperada
`E_c = N · p_c` (N = letras na coluna, p_c = frequência do português):

```
         (O_c − E_c)²
χ²  =  Σ ────────────
            E_c
```

- Se a coluna, desfeito o deslocamento, parece português, cada `O_c` fica perto de `E_c` e o χ² é
  **pequeno**.
- Se o deslocamento está errado, as letras comuns (`a`, `e`, `o`) caem onde se esperavam letras
  raras. Dividir por um `E_c` pequeno (por exemplo, o do `k`, 0,02%) faz o termo explodir.

O deslocamento com **menor** χ² é a letra da senha naquela posição.

Medido na coluna 0 do *Dom Casmurro* com `segredo` (~44 mil letras):

| Deslocamento | Letra | χ² |
|---|---|---|
| 18 | **s** | **1 437** |
| 3 | d | 338 735 |
| 17 | r | 338 868 |
| 19 | t | 463 427 |
| 22 | w (o pior) | 12 157 822 |

O certo é ~235 vezes menor que o segundo colocado. Com textos longos, a decisão não tem dúvida.

### 5.5 Por que qui-quadrado e não "a letra mais comum é o `a`"

O atalho "a letra mais comum da coluna é o `a`" funciona com textos grandes, mas usa **uma** letra
só. Basta uma coluna curta em que o `e` passe o `a` (no *Dom Casmurro*, a diferença é de 1,2 ponto
percentual) para a resposta errar por 4 casas. O χ² usa as **26** letras ao mesmo tempo: mesmo que
`a` e `e` troquem de lugar, o padrão do resto do alfabeto (as raras `k`, `w`, `y`, `x` no lugar
certo) ainda aponta o deslocamento correto.

Uma alternativa equivalente seria maximizar o produto escalar `Σ O_c · p_c` (correlação). O χ² foi
escolhido por ser a medida estatística padrão de "esta amostra segue esta distribuição?" e por
punir fortemente letras raras em excesso.

---

## 6. Quando o ataque falha

O ataque é **estatístico**: ele só funciona quando há letras suficientes para que as frequências
apareçam. A cifragem e a decifragem, ao contrário, são exatas e funcionam com qualquer tamanho.

### 6.1 Texto curto demais

Experimento: 10 trechos do *Dom Casmurro* em posições diferentes, cifrados com `segredo` e
quebrados com o tamanho máximo padrão (10).

| Letras no trecho | Letras por coluna (≈) | Senhas certas |
|---|---|---|
| 100 | 14 | 5 / 10 |
| 200 | 29 | 8 / 10 |
| 300 a 1 500 | 43 a 214 | 9 / 10 |
| 2 000 ou mais | 286 ou mais | 10 / 10 |

Há dois modos de falha, e eles atacam etapas diferentes:

- **Tamanho errado (IC).** Com 14 letras por coluna, quase nenhuma letra se repete e o IC de cada
  coluna é dominado pelo acaso. Em um dos trechos de 100 letras, o tamanho escolhido foi 8.
- **Tamanho certo, letras erradas (χ²).** É o caso mais comum: o IC acerta 7, mas uma coluna de 14
  letras não tem distribuição para comparar. Resultados como `ssrxrec`, `regnedo` e `segredg` erram
  uma ou outra letra; o texto decifrado sai "quase legível", com uma a cada sete letras trocada.

No limite, `gdmisonline` (11 letras) dá IC = 0 para todos os tamanhos: com 1 ou 2 letras por
coluna, nunca há duas iguais (detalhes no [`RESUMO.md`](../RESUMO.md)).

Com texto curto, o IC também pode dar **alto demais**, e isso é tão enganoso quanto zero. Exemplo:
`Aye Mak Sicur` higienizado (`ayemaksicur`) e cifrado com `segredo` vira `sckdengagai`. Com k = 2,
as colunas são `skeggi` (o `g` repete) e `cdnaa` (o `a` repete):

```
IC(skeggi) = 2 / (6·5) = 0,0667     IC(cdnaa) = 2 / (5·4) = 0,1000     média = 0,0833
```

0,0833 fica **acima** do português (0,0768), então o programa escolhe tamanho 2 e senha `sa`, e
devolve `acsdmnoaoaq`. Uma única repetição numa coluna de 5 letras já basta para o IC disparar. Mesmo
forçando o tamanho certo (`-t 7`), cada coluna tem 1 ou 2 letras e o χ² não tem o que comparar: o
texto sai `saooaaaaeet`. O IC só significa algo quando as colunas têm letras suficientes para que
as repetições reflitam a língua, e não o acaso.

### 6.2 Senha maior que o tamanho máximo testado

O ataque só encontra o tamanho se ele estiver entre os candidatos. Com `abcdefghijk` (11 letras) e o
padrão de testar até 10, o programa devolveu tamanho 1 e senha `d`: nenhum candidato tinha IC alto,
e a regra dos 90% ficou com o primeiro. Com `-m 20`, o mesmo texto deu 11 e `abcdefghijk`.

Além disso, cada coluna tem `n / L` letras. Senhas longas pedem textos proporcionalmente maiores
(seção 6.1). No extremo, uma senha **aleatória do tamanho do texto, usada uma única vez** não tem
coluna nenhuma para analisar: é a *one-time pad*, a única cifra com segurança provada (Shannon,
1949). A Vigenère é fraca exatamente porque **repete** a senha.

### 6.3 Texto que não é português

O χ² compara com o português. Trechos em outra língua puxam a resposta para o lado errado. O
*Dom Casmurro* do Projeto Gutenberg começa com ~770 letras de cabeçalho em inglês e termina com
~14,6 mil letras de licença em inglês. No livro inteiro isso é ruído (5% do total); mas no
experimento da seção 6.1, o único trecho de 1 500 letras que falhou foi justamente o primeiro, que
começa em inglês (senha encontrada: `sdhredo`). Em inglês, o `e` é a letra mais comum, e não o `a`.

---

## 7. Por que a Vigenère é insegura, em resumo

| Propriedade | César | Vigenère | One-time pad |
|---|---|---|---|
| Esconde a frequência global | Não | Em parte | Sim |
| Senha se repete | (tamanho 1) | Sim, a cada L letras | Nunca |
| Ataque | Testar 26 chaves | IC + frequência por coluna | Nenhum |
| Custo do ataque neste projeto | — | ~0,1 s para 309 mil letras, 20 tamanhos | — |

A lição geral, que vale para cifras modernas: **qualquer regularidade que sobrevive à cifragem é
uma porta de entrada**. A Vigenère achata a frequência, mas a repetição da senha cria uma
regularidade de segunda ordem (as colunas), e o IC a encontra.

---

## 8. Glossário

| Termo | Significado |
|---|---|
| **Texto claro** | O texto original, antes de cifrar (*plaintext*). |
| **Texto cifrado** | O resultado da cifragem (*ciphertext*). |
| **Senha / chave** | O segredo que define os deslocamentos. Neste trabalho, uma palavra de `a` a `z`. |
| **Período (L)** | Quantas letras a senha tem antes de se repetir. `abab` tem período 2. |
| **Coluna** | Letras do texto cifrado que usam a mesma letra da senha (`texto[i::L]`). |
| **Cifra de César** | Substituição em que todas as letras andam o mesmo número de casas. |
| **Cifra polialfabética** | Usa vários alfabetos de substituição alternadamente; a Vigenère é a mais conhecida. |
| **`mod 26`** | Resto da divisão por 26; faz o alfabeto dar a volta (`z + 1 = a`). |
| **NFD** | Forma de normalização Unicode que separa letras de seus acentos. |
| **IC** | Índice de Coincidência: chance de duas letras sorteadas do texto serem iguais. |
| **χ² (qui-quadrado)** | Medida de distância entre uma contagem observada e uma distribuição esperada. Menor = mais parecido. |
| **mdc** | Máximo divisor comum. |
| **One-time pad** | Cifra com chave aleatória do tamanho do texto, usada uma vez. Inquebrável em teoria. |
