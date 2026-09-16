# Guia de estudo — Listas 3, 4 e 5 (CE309 · Inferência Estatística)

Cada exercício traz: **onde está no resumo**, **o que estudar antes** e **só a resposta final**.

Resumos gerados anteriormente, referenciados pelo número:

| # | Resumo (PDF) |
|---|---|
| R1 | Variáveis Aleatórias Bidimensionais e Transformações |
| R2 | Transformações, Modelos Probabilísticos e Amostra Aleatória |
| R3 | Convergência, Desigualdades e Leis dos Grandes Números |
| R4 | Teorema Central do Limite e Distribuições Amostrais |
| R5 | Distribuições Amostrais: da Proporção à Razão de Variâncias |
| R6 | Dados Pareados, Proporções e Intervalos de Confiança |

---

## LISTA 3 — Ferramentas avançadas de probabilidade e convergências

### 1. Receita diária (limite para P(Y ≥ 12.000))
1. **Onde:** R3, seção 4 (Desigualdade de Markov) — coluna direita, topo.
2. **Conteúdo:** Markov exige apenas que Y seja **não negativa** e que E(Y) exista. Nada de variância, nada de distribuição. Saber identificar ε e aplicar P(Y ≥ ε) ≤ E(Y)/ε. Vale revisar a leitura da tabela do R3 (linha "Moeda viciada"), que mostra como esse limite costuma ser frouxo.
3. **Resposta:** P(Y ≥ 12.000) ≤ **0,25**.

### 2. Tamanho mínimo de n para P(|Ȳ − µ| < 0,5) ≥ 0,95
1. **Onde:** R3, seção 5 (Chebyshev) + seção 6 (lei fraca) e, na tabela central, a linha "Vida de lâmpada", que é exatamente esse tipo de conta.
2. **Conteúdo:** aplicar Chebyshev **à média amostral**, não a uma observação: Var(Ȳ) = σ²/n. Passar de "probabilidade de estar dentro" para "probabilidade de estar fora" (complementar) e isolar n.
3. **Resposta:** **n ≥ 720**.

### 3. 100 lançamentos: limite para P(X ≥ 60 ou X ≤ 40)
1. **Onde:** R3, seção 5 (Chebyshev); os parâmetros da binomial estão no R2, seção 4 (catálogo de distribuições).
2. **Conteúdo:** reconhecer que o evento "≥ 60 ou ≤ 40" é |X − 50| ≥ 10, com E(X) = np e Var(X) = np(1−p). Chebyshev aqui é aplicada ao total X, não à média.
3. **Resposta:** P(|X − 50| ≥ 10) ≤ **0,25**.

### 4. Basquete: P(acertar ao menos 9 em 20), exata e por TCL
1. **Onde:** R2, seção 4 (binomial: E = np, Var = np(1−p)) e R4, seção 4 (TCL) — inclusive o caso Bernoulli/proporção.
2. **Conteúdo:** somatório da binomial para o valor exato; para a aproximação, padronizar usando N(np, np(1−p)). Vale saber que a **correção de continuidade** (usar 8,5 no lugar de 9) melhora muito o resultado quando a variável é discreta.
3. **Resposta:** exata = **0,7483**; TCL sem correção = 0,6726; TCL com correção de continuidade = **0,7488**.

### 5. Média amostral de uma exponencial(λ = 100)
1. **Onde:** R2, seção 4 (linha Exponencial: E(X) = 1/λ, Var(X) = 1/λ²) e R4, seção 4 (TCL).
2. **Conteúdo:** o TCL não exige população normal — só µ e σ² finitos. Basta substituir a média e a variância da exponencial em N(µ, σ²/n). Atenção à parametrização: com f(x) = λe^(−λx), λ é **taxa**.
3. **Resposta:** Ȳ ~ᴬ N(1/λ ; 1/(nλ²)) = **N(0,01 ; 0,0001/n)**.

### 6. Poisson(λ): convergência e distribuição aproximada da média
1. **Onde:** R4, tabela central, linha "Média de Poisson" (resume os itens a e b) + seções 4 (TCL) e 5; a convergência em si está no R3, seção 6.
2. **Conteúdo:** E(Y) = Var(Y) = λ (equidispersão, R2 seção 4). Para (a), Chebyshev/lei fraca com Var(Ȳ) = λ/n → 0. Para (b), TCL. Para (c), simular muitas amostras, montar o histograma de Ȳ e sobrepor a densidade normal.
3. **Resposta:** (a) Ȳ →ᴾ λ; (b) **Ȳ ~ᴬ N(λ ; λ/n)**; (c) o histograma simulado se aproxima da N(λ; λ/n) à medida que n cresce.

### 7. σ̂² = (1/n)Σ(Yᵢ − µ)²
1. **Onde:** R3, seção 6 (leis dos grandes números) e R4, seção 4 (TCL).
2. **Conteúdo:** o truque é enxergar Wᵢ = (Yᵢ − µ)² como uma **nova amostra i.i.d.** com E(Wᵢ) = σ². Aí (a) é a lei dos grandes números aplicada a W e (b) é o TCL aplicado a W — o que exige o quarto momento µ₄ = E(Y − µ)⁴ finito.
3. **Resposta:** (a) σ̂² →ᴾ σ²; (b) **σ̂² ~ᴬ N(σ² ; (µ₄ − σ⁴)/n)**, que no caso normal vira N(σ² ; 2σ⁴/n); (c)–(d) a aderência à normal melhora de n = 50 para 1000.

### 8. Consistência de S² e de S
1. **Onde:** R3, seção 6 (lei fraca) e R4, seção 2 (Slutsky — item "se h(·) é contínua, h(Yₙ) →ᴾ h(c)").
2. **Conteúdo:** escrever S² em função de médias amostrais, aplicar a LGN a cada pedaço e juntar com Slutsky; o fator n/(n−1) → 1. Em (b), usar que a raiz quadrada é função contínua.
3. **Resposta:** (a) S² →ᴾ σ²; (b) **S →ᴾ σ** (o desvio padrão populacional).

### 9. A estatística t converge para N(0,1)?
1. **Onde:** R4, seção 2 (Slutsky) e seção 4 (TCL); complementar com R5, seção 3 (t de Student, "quando ν → ∞, T → N(0,1)").
2. **Conteúdo:** decompor t como o produto de dois fatores: (Ȳ − µ)/(σ/√n), que vai para N(0,1) pelo TCL, e σ/S, que vai para 1 em probabilidade (exercício 8). Slutsky junta os dois.
3. **Resposta:** a afirmação é **verdadeira** — t →ᴰ N(0,1); em (b) e (c), com n = 50, 250 e 1000 a t empírica fica praticamente indistinguível da normal padrão.

### 10. Razão R com duas Poisson independentes
1. **Onde:** R4, seção 2 (Slutsky, versão em distribuição) e seção 4 (TCL); parâmetros da Poisson no R2, seção 4.
2. **Conteúdo:** numerador: soma de duas variáveis centradas e independentes, com variância n + m → normal pelo TCL. Denominador: √(Xₙ + Yₘ) dividido por √(n+m) converge em probabilidade a 1 (lei dos grandes números). Slutsky fecha o argumento.
3. **Resposta:** **R →ᴰ Z ~ N(0,1)**; a simulação em (b) reproduz o histograma da normal padrão.

---

## LISTA 4 — Distribuição amostral (Módulo 5)

### 1. Moscas: distribuição amostral da proporção de fêmeas
1. **Onde:** R4, seção 5 (população, parâmetro, amostra, estatística) e o bloco central, exemplo dos três domicílios — mesma mecânica de enumeração.
2. **Conteúdo:** listar todas as amostras equiprováveis (com reposição), calcular a estatística em cada uma e agrupar valores iguais. Conceito-chave: **estimador não viesado** — E(p̂) = p.
3. **Resposta:** p̂ = 0 com 1/16; p̂ = 0,5 com 6/16; p̂ = 1 com 9/16. Média da distribuição amostral = **0,75**; **sim**, é igual à proporção populacional de fêmeas (3/4).

### 2. Idades dos presidentes: distribuição amostral da média
1. **Onde:** R4, seção 5 e bloco central (exemplo dos domicílios, incluindo E(R̄) = µ).
2. **Conteúdo:** 4² = 16 amostras com reposição, cada uma com probabilidade 1/16; agrupar as médias repetidas. Comparar E(Ȳ) com µ populacional.
3. **Resposta:** µ = **52,25**. Distribuição amostral das médias: 46 (1/16), 47,5 (2/16), 49 (1/16), 51 (2/16), 52 (2/16), 52,5 (2/16), 53,5 (2/16), 56 (1/16), 57 (2/16), 58 (1/16). Média das médias = **52,25 = µ**.

### 3. Mesmo exercício com a mediana
1. **Onde:** R4, seção 5 (estatística é *qualquer* função da amostra — a mediana também tem distribuição amostral).
2. **Conteúdo:** perceber que, para **n = 2**, a mediana é a própria média dos dois valores. Logo a distribuição amostral é idêntica à do exercício 2. Cuidado: isso é uma peculiaridade de n = 2; para n maior a mediana é geralmente viesada.
3. **Resposta:** distribuição **idêntica** à do exercício 2; média das medianas = **52,25 = µ** (aqui a mediana também é não viesada).

### 4. Vacina: p = 0,80 e n = 25
1. **Onde:** R4, seção 5 (definições de população/parâmetro/estimador/estimativa/distribuição amostral) e seção 4 (caso Bernoulli: p̂ ~ᴬ N(p, p(1−p)/n)); R5, seção 1 reforça a proporção.
2. **Conteúdo:** em (a), separar **parâmetro** (valor populacional, fixo), **estimador** (a regra p̂ = X/n, que é v.a.) e **estimativa** (o número observado). Em (b), a conta pode ser feita exata pela binomial ou aproximada pelo TCL — vale comparar as duas, já que n = 25 é pequeno.
3. **Resposta:** (a) população = todos os vacinados; parâmetro = p (afirmado 0,80); estimador = p̂ = X/25; estimativa = o valor de p̂ observado; distribuição amostral = X ~ Bin(25; 0,8), ou p̂ ~ᴬ N(0,8; 0,0064). (b) exatas: P(p̂ < 0,75) = **0,2200** e P(p̂ > 0,85) = **0,2340**; pela normal, ambas ≈ 0,266.

### 5. Y ~ N(100; 10²)
1. **Onde:** R2, seção 4 (normal) e R4, seção 5 / bloco central: Ȳ ~ N(µ, σ²/n) **exata** sob normalidade.
2. **Conteúdo:** a diferença entre os itens é só o erro padrão: σ em (a), σ/√n em (b). Padronização Z = (Y − µ)/σ.
3. **Resposta:** (a) **0,6827**; (b) **0,9999** (≈ 0,99994).

### 6. Probabilidades com t, χ² e F
1. **Onde:** R5 — seção 2 (χ²), seção 3 (t), seção 5 (F) e o quadro "Relações entre as distribuições".
2. **Conteúdo:** saber que a t é **simétrica** (P(Y < −a) = P(Y > a)), que a χ² tem suporte positivo e é assimétrica à direita, e que as tabelas costumam trazer a **cauda superior** — daí a necessidade de complementar.
3. **Resposta:**
   - **t₂₀:** P(−2,85 ≤ Y ≤ 2,85) = 0,9901; P(Y < −2,85) = 0,00495; P(Y > 2,85) = 0,00495; P(Y > 2,12) = 0,0234; P(Y < −3,01) = 0,00346.
   - **χ²₁₆:** P(8,91 < Y < 32,85) = 0,9093; P(Y > 8,91) = 0,9171; P(Y > 32,85) = 0,0077; P(Y > 22,80) = 0,1192; P(Y < 10,12) = 0,1397.
   - **F₍₁₀,₇₎:** P(Y > 3,18) = 0,0691; P(Y > 0,15) = 0,9959; P(Y > 5,35) = 0,0182; P(Y < 7,41) = 0,9928; P(Y < 1) = 0,4834.

### 7. Quantis das três distribuições
1. **Onde:** R5, mesmas seções do exercício 6 (é o caminho inverso da tabela).
2. **Conteúdo:** converter o enunciado para a convenção da sua tabela: P(Y > y) = 0,975 equivale a P(Y < y) = 0,025. Para a t, quantis inferiores são os simétricos dos superiores.
3. **Resposta:**
   - **t₂₀:** (a) 1,325; (b) −2,086; (c) −2,528; (d) −2,086.
   - **χ²₁₆:** (a) 23,542; (b) 6,908; (c) 5,812; (d) 6,908.
   - **F₍₁₀,₇₎:** (a) 2,703; (b) 0,253; (c) 0,192; (d) 0,253.

### 8. Máquina de empacotar
1. **Onde:** R2, seção 2 (combinação linear de normais — a soma de 4 pacotes) e R4 (distribuição amostral da média).
2. **Conteúdo:** em (a), inverter a padronização a partir do quantil 10% da normal. Em (b), lembrar que o **total** de 4 pacotes tem variância 4σ² (equivalentemente, 2 kg no total = média de 500 g).
3. **Resposta:** (a) µ = **512,82 g**; (b) P(total < 2 kg) = **0,0052**.

### 9. Idades em Davis (n = 100)
1. **Onde:** R4, seção 4 (TCL) e a linha "Fila de banco" da tabela central — é a mesma estrutura de conta.
2. **Conteúdo:** "dentro de dois anos da média" é P(|Ȳ − µ| < 2); µ não precisa ser conhecido porque a expressão só depende do erro padrão σ/√n. Em (b), raciocinar sobre o efeito de σ menor na dispersão de Ȳ.
3. **Resposta:** (a) **0,8176**; (b) **maior** — com σ = 10 a probabilidade sobe para 0,9545, pois o erro padrão cai.

### 10. GRE (µ = 1050, σ = 200)
1. **Onde:** R2, seção 4 (normal) e R4, seção 4 / seção 5 (distribuição amostral da média).
2. **Conteúdo:** (a) padronização simples; (b) é **probabilidade condicional** P(Y > 1400 | Y > 1200); (c) trocar σ por σ/√25 — é o ponto do exercício: a média de 25 alunos tem dispersão 5 vezes menor.
3. **Resposta:** (a) (i) **0,7734**, (ii) **0,2266**; (b) **0,1768** (≈ 17,7%); (c) P(Ȳ ≥ 1200) ≈ **0,000088** — cerca de 9 em 100.000, daí ser um resultado muito incomum.

---

## LISTA 5 — Distribuições amostrais e intervalos de confiança

### Exercício 1 — Treinamento de gestão (n = 25, s = 6%)
1. **Onde:** R5, seção 3 (média com σ² desconhecida: t de Student).
2. **Conteúdo:** como σ é desconhecido e a população é normal, a padronização usa S e segue t com n − 1 = 24 g.l. O enunciado pede P(|Ȳ − µ| ≤ 5), ou seja, uma probabilidade **bilateral** na t.
3. **Resposta:** ≈ **0,9997**. Interpretação: é praticamente certo que a média amostral fique a menos de 5 pontos percentuais de µ — logo, observar 15% quando se supõe µ = 10% é um resultado extremamente improvável, o que lança dúvida sobre a suposição de µ = 10%.

### Exercício 2 — Variância amostral dos gastos (n = 16)
1. **Onde:** R5, seção 2 (variância amostral e qui-quadrado) e a linha "Bateria" da tabela central, que é a mesma conta.
2. **Conteúdo:** (n−1)S²/σ² ~ χ²₁₅. Atenção à escala: o enunciado dá **desvio padrão** 600, então σ² = 360.000.
3. **Resposta:** P(S² > 700) ≈ **1** (praticamente 1). Interpretação: 700 é desprezível diante de σ² = 360.000, então é quase impossível observar variância amostral menor do que isso.

### Exercício 3 — GRE: diferença entre dois grupos
1. **Onde:** R5, seção 4 (diferença de médias, caso **σ² conhecidas**).
2. **Conteúdo:** X̄ₐ − X̄ᵦ é normal com média µₐ − µᵦ e variância σₐ²/nₐ + σᵦ²/nᵦ (as variâncias **somam** porque as amostras são independentes). Depois é só padronizar.
3. **Resposta:** **0,1671** (≈ 16,7%). Interpretação: mesmo com a vantagem real de 30 pontos, observar diferença amostral acima de 50 pontos não é raro — cerca de 1 em cada 6 repetições do estudo.

### Exercício 4 — Variabilidade das notas (razão de variâncias)
1. **Onde:** R5, seção 5 (razão de variâncias: F de Snedecor) e a linha "Acupuntura" da tabela central.
2. **Conteúdo:** sob σₐ² = σᵦ², o fator de correção some e resta S²ₐ/S²ᵦ ~ F₍ₙₐ₋₁, ₙᵦ₋₁₎ = F₍₁₄,₁₉₎. A F **não é simétrica**: importa qual variância vai no numerador.
3. **Resposta:** P(F₍₁₄,₁₉₎ ≥ 2,5) ≈ **0,032**. Interpretação: probabilidade baixa (≈ 3%), o que sugere que as variabilidades das duas turmas **não** são iguais.

### Exercício 5 — IC para a altura média (três cenários)
1. **Onde:** R6, seção 3 (construção do IC) e o formulário da seção 5, **primeira linha** (µ com σ² conhecida → quantil z).
2. **Conteúdo:** σ populacional é dado, então usa-se z mesmo com n = 10 (desde que a população seja normal). Observar como a amplitude reage a n (via √n) e ao nível de confiança (via z).
3. **Resposta:** (a) [**160,70 ; 179,30**]; (b) [**165,84 ; 174,16**]; (c) [**167,53 ; 172,47**]. Comentário esperado: aumentar n estreita o intervalo; reduzir a confiança de 95% para 90% também estreita, mas ao custo de errar mais vezes.

### Exercício 6 — IC otimista para a proporção (n = 625)
1. **Onde:** R6, seção 4 (otimista × conservador) e formulário, linha **p**.
2. **Conteúdo:** "otimista" significa substituir p por p̂ na margem de erro; o conservador usaria 0,5. Nível de 90% ⇒ z = 1,645.
3. **Resposta:** [**0,6698 ; 0,7302**], isto é, 0,70 ± 0,0302.

### Exercício 7 — Interpretar IC[µ; 0,95] = [21,5; 32,5]
1. **Onde:** R6, seção 4, primeiro tópico ("o intervalo é aleatório, não o parâmetro").
2. **Conteúdo:** o parâmetro µ é fixo e desconhecido; quem varia de amostra para amostra é o intervalo. A confiança é uma propriedade **do procedimento**, não de um intervalo já calculado.
3. **Resposta:** o procedimento usado produz intervalos que contêm o verdadeiro µ em 95% das repetições; repetindo a amostragem 100 vezes, espera-se que cerca de 95 dos intervalos construídos contenham µ. **Não** se deve dizer que "há 95% de probabilidade de µ estar entre 21,5 e 32,5", pois µ não é aleatório.

### Exercício 8 — Válvulas (n = 400)
1. **Onde:** R6, seção 3 (margem de erro e = z·σ/√n) e formulário, primeira linha.
2. **Conteúdo:** com n = 400 o desvio amostral pode substituir σ e usa-se z. Em (b), o que se pede é o **dimensionamento da amostra**: isolar n na expressão da margem de erro para e = 7,84 e 95%.
3. **Resposta:** (a) [**787,12 ; 812,88**] horas; (b) **n = 625**.

### Exercício 9 — IC de 95% para a variância (n = 25, s² = 16.000)
1. **Onde:** R6, formulário, linha **σ²**; a base teórica está no R5, seção 2.
2. **Conteúdo:** intervalo **assimétrico**, com dois quantis distintos da χ²₂₄ — e atenção à inversão: o quantil superior vai no denominador do limite **inferior**.
3. **Resposta:** [**9.755,1 ; 30.964,9**] (com χ²₀,₀₂₅;₂₄ = 39,364 e χ²₀,₉₇₅;₂₄ = 12,401).

---

### Observações sobre a cobertura dos resumos

- Os resumos R1 e R2 cobrem a base (transformações e modelos) usada pontualmente nas Listas 3 e 4; o grosso das três listas está em R3, R4, R5 e R6.
- Dois temas aparecem nas listas e **não** estão nos resumos por não terem sido dados em aula até aqui: a **correção de continuidade** (Lista 3, ex. 4) e o **dimensionamento de amostra** a partir da margem de erro (Lista 5, ex. 8b) — este último já está listado como "próximo passo" no R6.
- Os itens computacionais (Lista 3, exercícios 6c, 7c–d, 9b–c e 10b) não têm resposta fechada: são simulações para comparar a distribuição empírica com a aproximada.
