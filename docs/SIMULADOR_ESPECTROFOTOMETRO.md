# Simulador do espectrofotômetro — Análise Evolutiva Web3

Esta versão do MVP inclui uma simulação operacional do espectrofotômetro usado pela Análise Evolutiva para demonstrar, ao investidor, avaliador ou banca técnica, como a bancada de análise executa uma captura real em ambiente simulado.

## Objetivo

O objetivo não é apenas mostrar o resultado final da análise do leite. O simulador apresenta também o processo de captura óptica, incluindo:

- inicialização do ESP32, sensor e bancos de LED;
- auto-teste do equipamento;
- estabilização da câmara óptica;
- leitura de corrente escura;
- leitura do branco/referência;
- inserção da amostra;
- varredura UV/VIS/NIR de 365 nm a 910 nm;
- acionamento sequencial dos LEDs UV, VIS e NIR;
- exibição do feixe óptico ativo no painel;
- captura do ADC bruto por canal;
- correção do sinal;
- normalização;
- cálculo de absorbância;
- controle de qualidade por saturação e SNR;
- envio do pacote JSON para o backend da Análise Evolutiva;
- geração da evidência e registro Web3.

## Matrizes simuladas

A sessão do equipamento simula quatro matrizes da cadeia produtiva:

1. Solo/Pastagem.
2. Alimentação do rebanho.
3. Água de consumo/limpeza.
4. Leite cru refrigerado.

Cada matriz possui um ciclo de medição próprio, com preparo de amostra, tipo de medição, canal óptico, corrente do LED, tempo de exposição, leitura do ADC, sinal normalizado, absorbância e qualidade da captura.

## Componentes representados

O painel `/simulador` representa:

- bancos de LED UV, VIS e NIR;
- câmara escura;
- cubeta de 10 mm para leite e água;
- suporte óptico para solo e alimentação;
- detector multicanal;
- ADC de 16 bits;
- ESP32 enviando HTTP/JSON;
- telemetria de temperatura, umidade, tensão, ruído escuro e deriva da referência.


## Simulação viva da captura

O painel `/simulador` possui uma área chamada **Simulação viva da captura óptica**. Ela percorre uma sequência operacional com eventos temporais, representando o que aconteceria no equipamento:

1. energização do ESP32, detector e bancos de LED;
2. carregamento do firmware;
3. auto-teste de comunicação, sensor, câmara escura e LEDs;
4. estabilização térmica e ruído eletrônico;
5. inserção da matriz analisada;
6. travamento da câmara escura;
7. leitura de corrente escura com todos os LEDs desligados;
8. captura do branco/referência;
9. acionamento individual de cada LED;
10. leitura ADC da amostra;
11. cálculo do sinal corrigido, sinal normalizado e absorbância;
12. controle de qualidade por SNR e saturação;
13. montagem do pacote JSON enviado ao backend;
14. análise integrada e preparação do hash para registro Web3.

Essa visualização permite que um avaliador entenda que a evidência Web3 nasce de uma captura física simulada, não apenas de um formulário preenchido manualmente.

## Endpoints

```http
POST /api/spectrometer/session
```

Retorna a sessão simulada do espectrofotômetro, incluindo `live_sequence`.

```http
POST /api/spectrometer/live-sequence
```

Retorna apenas a sequência de eventos da captura viva do equipamento.

```http
POST /api/evidence/full-process
```

Executa a cadeia completa, incluindo o espectrofotômetro, análise integrada, evidência digital, hash SHA-256 e registro Web3 simulado.

## Observação técnica

Os dados são sintéticos e têm finalidade demonstrativa. A versão produtiva precisa usar calibração real, curvas de referência laboratoriais, validação metrológica e dados reais do equipamento.
