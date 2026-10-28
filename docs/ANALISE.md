# Análise da implementação (`vigenere.py`)

Este documento descreve **como** o trabalho foi construído: a função de cada arquivo e de cada
função, o porquê das decisões, o desempenho medido e os casos-limite verificados. Para o uso, veja
[`MANUAL.md`](MANUAL.md); para a teoria da cifra e do ataque, [`TEORIA.md`](TEORIA.md).

---

## 1. Visão geral da arquitetura

Tudo está em um único arquivo, `vigenere.py`, dividido em cinco blocos marcados por comentários
`# ==== … ====`. Cada bloco só usa os blocos acima dele:

```
                 ┌───────────────────────────────┐
                 │  CLI  (main, montar_parser,   │
                 │        cmd_higienizar, ...)   │
                 └───────┬───────────────┬───────┘
          ┌──────────────┘               └──────────────┐
          ▼                                             ▼
   ┌─────────────┐                             ┌──────────────────┐
   │   cifra     │◀────────────────────────────│  criptoanálise   │
   │ cifrar,     │   quebrar() decifra no fim  │  IC, qui-quadrado│
   │ decifrar    │                             │  quebrar         │
   └──────┬──────┘                             └──────────────────┘
          ▼
   ┌─────────────┐      ┌─────────────┐
   │higienização │      │  arquivos   │  (ler_arquivo, salvar_arquivo)
   └─────────────┘      └─────────────┘
```

Fluxo de dados dos três comandos principais:

```
cifrar:    .txt ─ler─▶ str ─higienizar─▶ a-z ─cifrar(senha)─────────▶ texto_criptografado.txt
quebrar:   .txt ─ler─▶ str ─higienizar─▶ a-z ─IC por k─▶ k ─χ² por coluna─▶ senha ─decifrar─▶ texto_quebrado.txt
decifrar:  .txt ─ler─▶ str ─higienizar─▶ a-z ─decifrar(senha)───────▶ texto_decifrado.txt
```

Princípios que guiaram as decisões:

1. **Fiel ao enunciado.** Só a biblioteca padrão do Python, IC de 1 a 10 por padrão, frequência
   comparada com o português, saídas com os nomes sugeridos (`texto_criptografado.txt`).
2. **A lógica não conhece a linha de comando.** `cifrar`, `decifrar` e `quebrar` recebem e devolvem
   strings e dicionários; só as funções `cmd_*` leem arquivos e imprimem. Isso permite testar e
   demonstrar as funções no interpretador (`import vigenere`).
3. **Operações em bloco, não letra a letra.** "Funcionar com arquivos grandes" é requisito. Todas as
   operações por letra usam métodos nativos de `str`/`bytes` (`translate`, `count`, fatiamento),
   que rodam em C. Os laços Python são por **letra da senha**, por **tamanho testado** ou por
   **deslocamento**, nunca por letra do texto.
4. **Código explicável.** Nenhuma biblioteca externa (nada de NumPy ou `collections.Counter`
   escondendo o cálculo); cada fórmula do [`TEORIA.md`](TEORIA.md) aparece de forma reconhecível.

---

## 2. Descrição dos arquivos

| Arquivo | Função |
|---|---|
| `vigenere.py` | Toda a implementação: higienização, cifra, criptoanálise e CLI. |
| `Segurança_de_Sistemas___T1_Venegre.pdf` | Enunciado do professor (a especificação). |
| `DomCasmurro.txt` | Texto de teste recomendado pelo enunciado (Projeto Gutenberg, UTF-8 com BOM, 410 mil caracteres, 308 887 letras após higienizar). |
| `gdm.txt` | Texto curto feito à mão (`G.D.M is online`) para o exemplo passo a passo. |
| `texto_higienizado.txt` | `gdm.txt` higienizado: `gdmisonline`. |
| `texto_criptografado.txt` | `gdmisonline` cifrado com `segredo`: `yhszwrbdmtv`. |
| `texto_quebrado.txt` | Saída do `quebrar` sobre o *Dom Casmurro* cifrado com `segredo` (o texto higienizado completo). |
| `RESUMO.md` | Resumo de uma página: problema, soluções, exemplos e resultados. |
| `docs/TEORIA.md`, `docs/ANALISE.md`, `docs/MANUAL.md` | Esta documentação. |

> Os três `texto_*.txt` foram gerados em execuções diferentes (os dois primeiros a partir de
> `gdm.txt`, o último a partir do *Dom Casmurro*); por isso o texto quebrado não corresponde ao texto
> criptografado que está ao lado dele no repositório.

---

## 3. Descrição das funções

Formato: **o que faz**, **por que desse jeito** e **quem depende dela**.

### 3.1 Constantes

#### `ALFABETO`, `A`
- **Faz:** `ALFABETO = "abcdefghijklmnopqrstuvwxyz"` e `A = ord("a") = 97`.
- **Por quê:** a conversão letra → número é `ord(c) − A`; número → letra é `ALFABETO[n]`.

#### `FREQ_PT` / `FREQ_PT_LISTA`
- **Faz:** frequência (%) de cada letra no português sem acentos; a lista é a mesma coisa em
  proporção (0–1), na ordem do alfabeto.
- **Por quê:** o dicionário é legível (dá para conferir letra por letra); a lista é o formato que o
  `qui_quadrado` percorre junto com a contagem, por `zip`. A soma da tabela é 100,01% (arredondamento
  da fonte), o que não afeta a comparação.
- **Dependentes:** `qui_quadrado`.

#### `IC_PORTUGUES = 0.0745`, `IC_ALEATORIO = 1/26`
- **Faz:** os dois valores de referência do IC (TEORIA §4.2).
- **Por quê:** **só aparecem na saída** do `quebrar`, para o usuário comparar. A decisão do tamanho
  não depende deles (ver `escolher_tamanho`), o que torna o ataque independente de o texto ter
  exatamente o IC "médio" do português (o *Dom Casmurro* tem 0,0768).

#### `_NAO_LETRAS`
- **Faz:** os 230 valores de byte (de 0 a 255) que **não** são `a`–`z`.
- **Por quê:** é o argumento `delete` de `bytes.translate`, que apaga todos esses bytes em uma
  única passada em C. Montada uma vez, na carga do módulo.
- **Dependentes:** `higienizar`.

### 3.2 Arquivos

#### `ler_arquivo(caminho)`
- **Faz:** lê os bytes e tenta decodificar como `utf-8-sig`; se falhar, como `latin-1`.
- **Por quê:**
  - `utf-8-sig` aceita UTF-8 com ou sem BOM e **remove** o BOM. O `DomCasmurro.txt` começa com BOM
    (`EF BB BF`); com `utf-8` simples, ele viraria o caractere U+FEFF no início do texto (que a
    higienização descartaria, mas é melhor não depender disso).
  - `latin-1` é o fallback para arquivos salvos no Bloco de Notas antigo ou em Windows-1252. Ele
    nunca falha (todo byte é um caractere válido), então a leitura sempre produz algum texto.
- **Dependentes:** todos os `cmd_*`.

#### `salvar_arquivo(caminho, texto)`
- **Faz:** grava o texto em ASCII.
- **Por quê:** depois da higienização, o texto só tem `a`–`z`. Gravar em `ascii` funciona como
  uma verificação: se algo fora disso escapasse, a escrita levantaria erro em vez de produzir um
  arquivo inconsistente.
- **Dependentes:** todos os `cmd_*`.

### 3.3 Higienização

#### `higienizar(texto)`
- **Faz:** `lower()` → normalização `NFD` → `encode("ascii", "ignore")` → `translate(None, _NAO_LETRAS)`.
- **Por quê** (cada etapa, na ordem):
  1. `lower()` primeiro, para que `Á` vire `á` e depois `a`.
  2. `NFD` separa letra e acento (`ç` → `c` + U+0327), TEORIA §3.
  3. `encode("ascii", "ignore")` descarta tudo que não é ASCII: os acentos soltos, travessões,
     aspas curvas, letras sem decomposição. Resultado em `bytes`.
  4. `bytes.translate(None, _NAO_LETRAS)` apaga o que sobrou de não letra (espaços, pontuação,
     dígitos, quebras de linha).
  - A alternativa óbvia, `"".join(c for c in texto if c in ALFABETO)`, percorre o texto em Python;
    as quatro etapas acima rodam todas em C. Medido: 6,6 ms para o *Dom Casmurro* inteiro.
- **Limitação conhecida:** letras sem decomposição canônica são **removidas**, não convertidas:
  `ß`, `ø`, `æ` e os ordinais `º`/`ª` somem (`"Nº 5, straße"` → `nstrae`). Para textos em português
  isso é irrelevante; o `º` seria convertido em `o` pela forma `NFKD`, mas o enunciado não pede isso.
- **Dependentes:** `_chave_para_deslocamentos` (a senha também é higienizada) e todos os `cmd_*`.

### 3.4 Cifra

#### `_tabela_deslocamento(desloc)`
- **Faz:** monta a tabela de `str.translate` que leva cada letra `desloc` casas adiante
  (`a→d, b→e, …, z→c` para 3).
- **Por quê:** o alfabeto deslocado é só `ALFABETO[d:] + ALFABETO[:d]`, e a volta no fim do
  alfabeto (o `mod 26`) sai de graça desse fatiamento.
- **Dependentes:** `_aplicar_chave`.

#### `_aplicar_chave(texto, deslocamentos)`
- **Faz:** aplica `deslocamentos[i]` a todas as letras das posições `i, i+L, i+2L, …`.
- **Como:**
  ```python
  saida = [""] * len(texto)
  for i, d in enumerate(deslocamentos):
      saida[i::k] = texto[i::k].translate(_tabela_deslocamento(d))
  return "".join(saida)
  ```
  `texto[i::k]` é a coluna `i` (TEORIA §2.2); ela é cifrada inteira de uma vez (uma César) e
  devolvida às suas posições pela atribuição em fatia estendida `saida[i::k]`.
- **Por quê:** o laço tem **L iterações** (7 para `segredo`), não n. Medido no *Dom Casmurro*:
  3,2 ms, contra 25 ms de uma versão ingênua letra a letra
  (`chr((ord(c) − 97 + k) % 26 + 97)` num gerador), que dá o mesmo resultado. É também a própria
  estrutura do ataque: cifrar por colunas deixa visível por que a Vigenère se decompõe em Césares.
- **Dependentes:** `cifrar`, `decifrar`.

#### `_chave_para_deslocamentos(chave)`
- **Faz:** higieniza a senha e converte cada letra em número (`s` → 18).
- **Por quê:** a senha sofre a mesma higienização que o texto: `Segrêdo!` vira `segredo` (verificado:
  o arquivo cifrado é idêntico byte a byte). Senha sem nenhuma letra (`123`) levanta `ValueError`
  com mensagem clara, em vez de uma divisão por zero mais adiante.
- **Dependentes:** `cifrar`, `decifrar`.

#### `cifrar(texto_limpo, chave)` / `decifrar(texto_cifrado, chave)`
- **Faz:** `C = (P + K) mod 26` e `P = (C − K) mod 26`.
- **Por quê:** decifrar com `K` é cifrar com o inverso `(26 − K) mod 26`, então as duas usam o
  mesmo `_aplicar_chave`. O `% 26` externo trata o caso `K = 0` (`a`), cujo inverso é 0 e não 26.
- **Pré-condição:** o texto já deve estar higienizado. Um caractere fora de `a`–`z` passaria
  intacto pelo `translate`, mas ocuparia uma posição da senha, desalinhando as seguintes. A CLI
  sempre higieniza antes, e `quebrar` recebe texto já higienizado.
- **Dependentes:** `cmd_cifrar`, `cmd_decifrar`, `quebrar`.

### 3.5 Criptoanálise

#### `contar_letras(texto)`
- **Faz:** lista com as 26 contagens, `[texto.count("a"), …, texto.count("z")]`.
- **Por quê:** 26 chamadas de `str.count` (cada uma uma varredura em C) são mais rápidas que um
  laço Python por letra, e mais transparentes que `Counter` para explicar.
- **Dependentes:** `indice_coincidencia`, `achar_deslocamento`.

#### `indice_coincidencia(texto)`
- **Faz:** `Σ f(f − 1) / (n(n − 1))`, TEORIA §4.1. Devolve 0 para textos com menos de 2 letras.
- **Por quê:** é a fórmula exata (sem reposição), não a aproximação `Σ p²`. Para colunas pequenas
  a diferença importa: uma coluna de 1 letra teria `Σ p² = 1`, um IC "perfeito" e falso.
- **Dependentes:** `ic_por_tamanho`.

#### `ic_por_tamanho(texto, tamanho_max)`
- **Faz:** para cada `k` de 1 a `tamanho_max`, divide em `k` colunas e calcula o IC médio.
  Devolve `{k: IC}`.
- **Por quê:** a média, e não a soma ou o mínimo, torna os valores comparáveis entre `k`
  diferentes (TEORIA §4.3).
- **Dependentes:** `quebrar`.

#### `escolher_tamanho(ics)`
- **Faz:** devolve o **menor** `k` cujo IC é pelo menos 90% do maior IC.
- **Por quê:** os múltiplos do tamanho certo empatam com ele, e os divisores ficam no meio
  (TEORIA §4.5). Pegar o máximo devolveria 14 em vez de 7 sempre que o múltiplo tiver IC uma fração
  maior por acaso. O limiar de 90% foi escolhido porque:
  - fica **acima** do maior divisor visto nos testes (`k = 6` de `criptografia`: 0,0625 / 0,0768 =
    81%);
  - deixa folga de sobra para que o `k` certo passe mesmo se um múltiplo tiver IC um pouco maior
    por flutuação estatística (no *Dom Casmurro*, 7 e 14 deram 0,0768 os dois, iguais até a 4ª
    casa).
- **Observação:** o `return` final (`max(ics, key=ics.get)`) nunca é alcançado: o próprio `k` do
  máximo sempre satisfaz a condição. Ficou como garantia.
- **Dependentes:** `quebrar` (quando `-t` não é passado).

#### `qui_quadrado(contagem, total)`
- **Faz:** `Σ (O − N·p)² / (N·p)`, TEORIA §5.4.
- **Por quê:** nenhuma frequência da tabela é zero (a menor é 0,01%), então não há divisão por zero.
- **Dependentes:** `achar_deslocamento`.

#### `achar_deslocamento(coluna)`
- **Faz:** conta as letras da coluna **uma vez**, testa os 26 deslocamentos girando a contagem
  (`contagem[d:] + contagem[:d]`, TEORIA §5.3) e devolve o de menor χ².
- **Por quê:** girar a lista de 26 contagens custa 26 operações; decifrar a coluna 26 vezes custaria
  26 varreduras do texto. Coluna vazia (só acontece forçando `-t` maior que o texto) devolve 0.
- **Dependentes:** `quebrar`.

#### `quebrar(texto_cifrado, tamanho_max=10, tamanho=None)`
- **Faz:** IC por tamanho → tamanho (ou o forçado) → um deslocamento por coluna → senha →
  decifra. Devolve `{"ics", "tamanho", "chave", "texto"}`.
- **Por quê:** devolver tudo, e não só o texto, permite que a CLI mostre o gráfico de IC (a "prova"
  da etapa 1, exigida na saída) e permite reutilizar a função no interpretador.
- **Dependentes:** `cmd_quebrar`.

### 3.6 CLI

| Função | Faz |
|---|---|
| `_pegar_chave(args)` | Usa `-k`; se ausente, pergunta com `input("Chave: ")` (útil para não deixar a senha no histórico do terminal). |
| `cmd_higienizar` | Só higieniza e salva (padrão `texto_higienizado.txt`). Útil para conferir a etapa obrigatória 1 isoladamente. |
| `cmd_cifrar` | Lê, higieniza, cifra e salva (padrão `texto_criptografado.txt`). |
| `cmd_decifrar` | Lê, **higieniza de novo** (remove a quebra de linha que um editor pode ter acrescentado), decifra, salva e mostra o começo. |
| `cmd_quebrar` | Lê e higieniza; recusa texto com menos de 2 letras; imprime a tabela de IC com barras proporcionais ao maior IC e `<<` no escolhido, o tamanho, a senha e o começo do texto. Se todos os ICs forem 0, divide por 1 em vez de 0 (ver §6). |
| `montar_parser` | Define os subcomandos e opções (`argparse`). |
| `main` | Força a saída do terminal em UTF-8 (os acentos de "Índice" e "Começo" saem quebrados no console do Windows sem isso) e converte `ValueError`/`OSError` em mensagem `Erro: …` com código de saída 1, sem *traceback*. |

---

## 4. Desempenho

Medido com Python 3.13 no *Dom Casmurro* (308 887 letras), melhor de 5 execuções:

| Etapa | Tempo |
|---|---|
| `ler_arquivo` | 0,6 ms |
| `higienizar` | 6,6 ms |
| `cifrar` / `decifrar` | 3,2 ms / 3,1 ms |
| `ic_por_tamanho` (k = 1..10) | 42 ms |
| `quebrar` completo (k = 1..10) | 50 ms |
| `quebrar` completo (k = 1..20) | 92 ms |
| `quebrar` com o livro repetido 10× (3,1 milhões de letras) | 504 ms |

O tempo cresce de forma **linear** com o tamanho do texto (10× o texto, 10× o tempo), como
esperado pela complexidade:

| Operação | Tempo | Espaço extra |
|---|---|---|
| Higienizar | O(n) | O(n) |
| Cifrar / decifrar | O(n) (L fatias que somam n) | O(n) (lista de saída) |
| IC para k = 1..m | O(26 · n · m): para cada k, as colunas somam n letras e cada uma é varrida 26 vezes por `count` | O(n) (colunas de um k por vez) |
| Achar a senha | O(26 · n) para contar + O(L · 26²) para os χ² | O(1) além das colunas |

O termo dominante é o IC. Ele é proporcional ao tamanho máximo testado: dobrar `-m` dobra o tempo.

---

## 5. Decisões e dificuldades

1. **Escolher o tamanho sem cair nos múltiplos.** A ideia mais direta, pegar o maior IC, falha porque
   `k` e `2k` empatam. Comparar com o valor fixo 0,0745 ("o mais próximo do português") também é
   frágil: o IC de um texto real varia (0,0768 no *Dom Casmurro*), e textos com outro estilo
   ficariam com outro valor. A regra relativa ("menor `k` a 90% do melhor") usa o próprio texto
   como referência.

2. **Desempenho sem bibliotecas.** A forma "de livro" da Vigenère é um laço por letra com
   `ord`/`chr`. Ela é correta, mas o requisito de arquivos grandes e a ausência de NumPy levaram à
   cifragem por colunas com `str.translate` (8× mais rápida) e à contagem com `str.count`. O ganho
   veio de perceber que **a mesma decomposição em colunas** que quebra a cifra também a acelera.

3. **Higienização sem tabela manual de acentos.** Uma tabela `{"á": "a", "ã": "a", "ç": "c", …}`
   sempre esquece algum caractere (`ü`, `ñ`, `ò`). A NFD resolve qualquer letra latina com acento
   sem listar nenhuma.

4. **Codificação dos arquivos.** Os arquivos de entrada podem vir em UTF-8 com BOM (Projeto
   Gutenberg), UTF-8 sem BOM ou Windows-1252 (editores antigos). A leitura tenta UTF-8 e cai para
   Latin-1 em vez de exigir um formato.

5. **Mostrar a etapa 1, não só o resultado.** O enunciado pede para "comparar os resultados" do IC.
   Por isso o `quebrar` imprime a tabela inteira com barras, e não apenas o tamanho escolhido: é o
   que permite explicar a decisão na apresentação.

---

## 6. Casos-limite verificados

| Caso | Resultado |
|---|---|
| Ida e volta no *Dom Casmurro*: `higienizar` vs. `cifrar` + `quebrar` | Arquivos idênticos (`cmp`). |
| Senha com acento e pontuação (`Segrêdo!`) | Higienizada para `segredo`; cifra idêntica. |
| Senha sem letras (`123`) | `Erro: a chave precisa ter pelo menos uma letra de a a z`. |
| Arquivo inexistente | `Erro: [Errno 2] No such file or directory: …`, sem *traceback*. |
| Texto cifrado com menos de 2 letras | `Texto cifrado vazio ou curto demais.` |
| Senha `a` (deslocamento 0) | Texto cifrado = texto claro; `quebrar` devolve `a`. |
| Senha periódica (`abab`, `sese`, `aaaa`) | Devolve o período (`ab`, `se`, `a`); decifra corretamente (TEORIA §2.4). |
| Senha de 12 letras (`criptografia`) com `-m 20` | Tamanho 12, senha correta. |
| Senha de 11 letras com o padrão `-m 10` | Tamanho 1, senha `d` (errada): o tamanho real não foi testado. |
| Texto de 11 letras (`gdmisonline`) | IC = 0 em todos os tamanhos; tamanho 1, senha `n` (errada, TEORIA §6.1). Antes da correção, o comando `quebrar` travava aqui com `ZeroDivisionError` (ver abaixo). |
| `Aye Mak Sicur` → `ayemaksicur` → cifrado com `segredo` → `sckdengagai` | IC 0,0833 em k = 2 (maior que o do português!) e 0 de k = 3 em diante; tamanho 2, senha `sa`, texto `acsdmnoaoaq`. Com `-t 7`: senha errada, texto `saooaaaaeet`. |

> **Erro corrigido: divisão por zero na tabela de IC.** Em `cmd_quebrar`, a barra é desenhada com
> `round(40 * ic / maior)`. Num texto tão curto que nenhuma coluna tem letra repetida
> (`yhszwrbdmtv`), todos os ICs são 0, `maior` era 0 e o programa terminava com *traceback* antes de
> mostrar o tamanho e a senha. A função `quebrar()` não tinha o problema, só a impressão.
> Correção: `maior = max(r["ics"].values()) or 1`. Achado ao conferir as receitas do
> [`MANUAL.md`](MANUAL.md).
| Trechos de 100 a 5 000 letras | Ver tabela em TEORIA §6.1: confiável a partir de ~2 000 letras para senha de 7. |

---

## 7. Pontos em aberto

- **Senhas maiores que `-m`** passam despercebidas, e o programa não avisa. Uma melhoria simples
  seria alertar quando nenhum `k` chega perto do IC do português (por exemplo, quando o melhor IC
  fica abaixo de 0,06).
- **O limiar de 90%** foi definido por raciocínio e confirmado nos testes, não por uma varredura
  sistemática. Senhas com muitos divisores e textos curtos podem aproximar um divisor do limiar.
- **Texto curto com tamanho certo** gera senhas "quase certas" (uma letra trocada). Não há
  segunda tentativa: um refinamento possível seria testar o segundo melhor χ² das colunas em que a
  diferença para o primeiro é pequena.
- **Trechos em inglês** do arquivo do Projeto Gutenberg entram na estatística. Não atrapalham no
  livro inteiro, mas atrapalham em trechos do início (TEORIA §6.3).
- **Tabela de frequências fixa.** A tabela é do português em geral; o ataque não se adapta a outra
  língua nem a textos técnicos com distribuição muito diferente.
