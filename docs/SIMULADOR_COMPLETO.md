# Simulador completo — Análise Evolutiva Web3

## Objetivo

O simulador completo foi incluído para demonstrar ao avaliador, usuário ou investidor como o sistema final poderá funcionar na prática. Em vez de mostrar apenas uma amostra de leite isolada, o MVP simula a cadeia produtiva de forma integrada:

```text
Solo/Pastagem → Alimentação do rebanho → Água → Coleta do leite
→ Transporte refrigerado → Espectrofotômetro → Diagnóstico → Hash → Web3
```

## Captura multiespectral simulada

A simulação representa um espectrofotômetro demonstrativo com faixa de 365 nm a 910 nm, cobrindo UV, VIS e NIR. Para cada canal óptico, o sistema gera:

- comprimento de onda;
- banco de luz utilizado;
- corrente escura;
- leitura de branco/referência;
- leitura ADC da amostra;
- sinal corrigido;
- sinal normalizado;
- absorbância.

Essas informações permitem ao investidor visualizar não apenas o resultado final, mas a lógica de aquisição do dado técnico.

## Matrizes analisadas

O simulador considera quatro matrizes:

1. **Leite** — avalia consistência espectral, risco de adulteração/diluição, temperatura e índice de sólidos.
2. **Solo/Pastagem** — gera proxies de umidade, matéria orgânica e suporte produtivo da pastagem.
3. **Alimentação** — gera proxies de matéria seca, fermentação/mofo e score nutricional.
4. **Água** — gera proxies de transparência, sinal orgânico e risco de turbidez.

## Cenários disponíveis

- Cadeia em conformidade;
- Suspeita de adição de água no leite;
- Quebra da cadeia fria;
- Leite com sólidos elevados;
- Risco na alimentação do rebanho;
- Estresse de solo/pastagem;
- Risco integrado na cadeia.

## Valor para a apresentação

A tela `/simulador` deve ser usada como principal demonstração do MVP, porque comunica o produto inteiro:

- mostra o problema real da cadeia produtiva;
- demonstra análise técnica realizada pela própria Análise Evolutiva;
- evidencia a captura espectral por ondas;
- conecta dados produtivos, ambientais e laboratoriais;
- gera evidência digital;
- registra hash Web3;
- permite verificação pública.

## Observação técnica

Os dados são sintéticos e demonstrativos. A versão produtiva exigirá calibração real do espectrofotômetro, curvas laboratoriais por matriz, validação metrológica e base de amostras reais.
