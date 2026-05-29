# Visão do Investidor — Análise Evolutiva Web3

## Objetivo

Esta página transforma o MVP técnico em uma narrativa de investimento. O avaliador ou investidor não deve ver apenas uma simulação de espectrofotômetro, mas uma plataforma com potencial de retorno: hardware + SaaS + taxa por análise + dados proprietários + rastreabilidade Web3.

## Rota

```text
/investidor
```

## Endpoint

```http
POST /api/investor/impact
```

Parâmetros principais:

- `scenario`: cenário técnico da cadeia produtiva;
- `monthly_liters`: volume mensal protegido pela plataforma;
- `milk_price_brl`: preço demonstrativo por litro;
- `baseline_loss_pct`: perda operacional estimada sem rastreabilidade;
- `loss_reduction_pct`: redução estimada de perdas por diagnóstico/rastreabilidade;
- `monthly_saas_brl`: assinatura mensal da plataforma;
- `analysis_fee_brl`: taxa demonstrativa por análise;
- `analyses_per_month`: volume mensal de análises.

## O que apresentar ao investidor

1. Primeiro abrir `/simulador` e mostrar a origem física da evidência: LEDs, ADC, referência, amostra, absorbância e pacote JSON.
2. Depois abrir `/investidor` e explicar o retorno potencial: redução de perdas, bônus por qualidade, menor custo de auditoria e receita recorrente.
3. Fechar com a tese defensável: base proprietária de curvas espectrais, integração hardware + IA + Web3, pilotos com cooperativas/laticínios e expansão para solo, folha, hortifrúti e bioinsumos.

## Observação

Todos os valores são simulações para pitch e devem ser validados em piloto real com dados da cadeia produtiva.
