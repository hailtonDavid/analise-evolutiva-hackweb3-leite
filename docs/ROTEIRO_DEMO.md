# Roteiro de demonstração — HackWeb 3.0

## 1. Abertura

Apresente a proposta:

> A Análise Evolutiva Web3 é uma plataforma para rastrear e auditar a cadeia produtiva do leite. Ela usa espectrofotometria multiespectral para analisar solo, alimentação, água e leite, gera uma evidência digital e registra o hash em uma camada Web3.

## 2. Problema

Explique que a cadeia do leite possui informações fragmentadas: laudos, coleta, temperatura, alimentação, transporte, qualidade da água e dados de propriedade. Quando essas informações não são rastreáveis, há dificuldade de auditoria, verificação de integridade e confiança entre produtor, cooperativa, indústria e fiscalização.

## 3. Demonstração principal

Abra:

```text
http://127.0.0.1:5000/simulador
```

Escolha um cenário, preferencialmente:

- `Risco integrado na cadeia`, para mostrar todos os módulos; ou
- `Suspeita de adição de água no leite`, para destacar a análise da amostra.

Clique em **Executar processo completo**.

## 4. O que mostrar na tela

Mostre nesta ordem:

1. **Jornada rastreável** — propriedade, solo, alimentação, água, coleta, transporte, bancada e Web3.
2. **KPIs** — status integrado, score da cadeia, risco de adulteração e temperatura.
3. **Captura das ondas** — alterne entre Leite, Solo/Pastagem, Alimentação e Água.
4. **Tabela de canais** — mostre corrente escura, referência, ADC da amostra, sinal normalizado e absorbância.
5. **Diagnóstico técnico** — explique que a própria Análise Evolutiva interpreta a leitura.
6. **Hash da evidência** — mostre que todo o processo vira uma evidência digital.
7. **Verificação pública** — abra o link `/verify/<hash>`.

## 5. Mensagem Web3

Diga:

> A blockchain não precisa armazenar o laudo inteiro. O sistema registra o hash da evidência. Assim, se qualquer campo do laudo ou da cadeia for alterado, o hash muda e a verificação falha.

## 6. Fechamento

Finalize com:

> O MVP demonstra como a cadeia produtiva do leite pode ganhar confiança, rastreabilidade e auditabilidade com análise espectrofotométrica, IA/regras técnicas e Web3.
