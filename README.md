# Análise Evolutiva HackWeb 3.0 — Cadeia Produtiva do Leite

> Rastreabilidade Web3 da cadeia produtiva do leite com espectrofotometria multiespectral, análise da própria Análise Evolutiva, geração de evidência digital, hash criptográfico e smart contract.

## Visão geral

A **Análise Evolutiva Web3** é um MVP criado para o HackWeb 3.0 com foco na cadeia produtiva do leite. A proposta é demonstrar como a própria Análise Evolutiva pode analisar o contexto produtivo e a amostra de leite usando um fluxo espectrofotométrico multiespectral e, depois, transformar esse resultado em uma evidência digital verificável.

Esta versão inclui um **simulador completo para usuário, investidor e banca avaliadora** na rota `/simulador`. O simulador agora reproduz a captura do espectrofotômetro em modo operacional: energização do ESP32, auto-teste, corrente escura, branco de referência, acionamento sequencial dos LEDs UV/VIS/NIR, leitura ADC, correção do sinal, absorbância, pacote JSON e registro Web3. O fluxo geral é:

```text
Propriedade → Solo/Pastagem → Alimentação do rebanho → Água → Coleta do leite
→ Transporte refrigerado → Captura multiespectral 365-910 nm → Diagnóstico técnico
→ Evidência digital → Hash SHA-256 → Registro Web3 → Verificação pública
```

A blockchain não armazena o laudo completo. Ela registra a prova de integridade da evidência, preservando dados sensíveis, reduzindo custo e permitindo auditoria futura.

## Problema

A cadeia produtiva do leite depende de análises de qualidade, laudos, registros de coleta, transporte, temperatura, alimentação do rebanho, qualidade da água e condições da pastagem. Na prática, essas informações podem ficar espalhadas em planilhas, PDFs, sistemas internos e documentos difíceis de auditar.

Isso dificulta responder com segurança:

- a amostra analisada corresponde ao lote informado?
- o solo, a alimentação e a água foram considerados no contexto produtivo?
- quem realizou a análise e quando ela foi gerada?
- o laudo foi alterado depois do registro?
- existe evidência verificável para auditoria, cooperativa, indústria ou fiscalização?
- o lote foi aprovado, reprovado ou ficou em atenção?

## Solução

O MVP demonstra uma plataforma capaz de:

1. simular a captura espectrofotométrica do solo/pastagem;
2. simular a análise da alimentação do rebanho;
3. simular a leitura da água operacional;
4. simular a coleta e a análise multiespectral do leite;
5. calcular corrente escura, branco de referência, ADC bruto, sinal corrigido, normalização e absorbância por canal;
6. classificar o processo como `APROVADO`, `ATENÇÃO` ou `REPROVADO`;
7. gerar evidência digital em JSON;
8. calcular o hash SHA-256 da evidência;
9. registrar o hash em camada Web3 simulada ou smart contract;
10. disponibilizar página pública de verificação.

## Simulador completo

Acesse:

```text
http://127.0.0.1:5000/simulador
```

O simulador apresenta:

- cenários de cadeia em conformidade, adulteração, quebra de frio, risco alimentar, estresse de solo e risco integrado;
- simulação viva do espectrofotômetro, com LEDs acionando em sequência;
- captura das ondas de 365 nm a 910 nm;
- corrente escura com LEDs desligados;
- captura do branco/referência;
- integração por canal óptico com corrente do LED e tempo de exposição;
- leitura ADC da amostra, sinal corrigido, sinal normalizado e absorbância;
- seleção visual entre leite, solo/pastagem, alimentação e água;
- tabela de leitura por canal óptico;
- diagnóstico técnico da Análise Evolutiva;
- score integrado da cadeia;
- recomendações técnicas;
- evidência digital com hash;
- registro Web3;
- link de verificação pública.

## Diferencial Web3

O diferencial está em transformar uma análise técnica completa da cadeia do leite em uma evidência digital verificável. O hash do relatório permite comprovar que o conteúdo não foi alterado. O smart contract cria uma trilha de auditoria pública, transparente e resistente a adulterações.

## Estrutura do repositório

```text
.
├── backend/                 # Aplicação Flask, regras de análise, persistência e páginas web
├── contracts/               # Smart contract Solidity
├── hardhat/                 # Ambiente Hardhat para teste/deploy do contrato
├── data/                    # Amostras simuladas
├── docs/                    # Documentação para banca, arquitetura, pitch e submissão
├── scripts/                 # Scripts de demonstração
├── tests/                   # Testes automatizados Python
├── docker-compose.yml       # Execução via Docker
├── Makefile                 # Comandos úteis
├── LICENSE                  # Apache-2.0
└── NOTICE                   # Avisos de propriedade intelectual
```



## Simulador do espectrofotômetro

Além da simulação da cadeia produtiva, esta versão inclui uma camada visual e técnica do espectrofotômetro da Análise Evolutiva. O painel `/simulador` demonstra o funcionamento da bancada óptica como se o equipamento estivesse executando a captura: auto-teste, câmara escura, LEDs UV/VIS/NIR acionados um a um, cubeta/porta-amostra, detector, ADC, normalização, absorbância, controle de qualidade por SNR/saturação e envio do pacote JSON para gerar a evidência Web3.

Endpoints disponíveis:

```http
POST /api/spectrometer/session
```

Retorna a sessão do equipamento com telemetria, auto-teste, workflow, ciclos de amostra e varredura por canal para solo, alimentação, água e leite.

```http
POST /api/spectrometer/live-sequence
```

Retorna a sequência operacional da captura, com eventos de energia, auto-teste, calibração, acionamento dos LEDs, leitura ADC, processamento do sinal, pacote JSON e preparação para Web3.

Documentação complementar: `docs/SIMULADOR_ESPECTROFOTOMETRO.md`.

## Como executar localmente

### 1. Backend Flask

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://127.0.0.1:5000
```

### 2. Testes Python

Na raiz do projeto:

```bash
python -m pip install -r backend/requirements.txt
python -m pytest -q
```

### 3. Docker

```bash
docker compose up --build
```

Acesse:

```text
http://127.0.0.1:5000
```

## Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Interface de demonstração |
| GET | `/simulador` | Simulador completo para usuário/investidor |
| GET | `/health` | Saúde da aplicação |
| POST | `/api/samples/simulate` | Gera leitura espectrofotométrica simulada do leite |
| POST | `/api/simulator/full-process` | Simula o processo completo: solo, alimentação, água e leite |
| POST | `/api/evidence` | Analisa uma amostra de leite, gera evidência e registra hash |
| POST | `/api/evidence/full-process` | Gera evidência completa da cadeia e registra hash Web3 |
| GET | `/api/evidence/<evidence_id>` | Consulta uma evidência pelo ID |
| GET | `/verify/<evidence_hash>` | Página pública de verificação |
| GET | `/api/verify/<evidence_hash>` | Verificação em JSON |

## Exemplo rápido via cURL

Simular o processo completo:

```bash
curl -X POST http://127.0.0.1:5000/api/evidence/full-process \
  -H "Content-Type: application/json" \
  -d '{"scenario":"integrated_risk", "seed":42}'
```

## Smart contract

O contrato `AnaliseEvolutivaLeiteTrace.sol` registra:

- hash da evidência;
- lote;
- produtor;
- URI ou referência do laudo;
- status da análise;
- endereço registrador;
- data/hora do bloco.

### Testar o contrato

```bash
cd hardhat
npm install
npm test
```

### Deploy local

```bash
cd hardhat
npm run node
npm run deploy:local
```

## Como apresentar para a banca

A demonstração deve seguir esta ordem:

1. abrir a tela inicial;
2. entrar em `/simulador`;
3. explicar o problema de rastreabilidade na cadeia do leite;
4. escolher um cenário, por exemplo risco integrado ou suspeita de adição de água;
5. executar o processo completo;
6. mostrar a jornada do lote, do solo e da alimentação até a análise do leite;
7. alternar entre os gráficos de leite, solo/pastagem, alimentação e água;
8. mostrar a tabela de captura das ondas com ADC, referência, normalização e absorbância;
9. mostrar o diagnóstico da Análise Evolutiva;
10. mostrar o hash da evidência e o registro Web3;
11. abrir a tela pública de verificação;
12. explicar que qualquer alteração no laudo mudaria o hash;
13. mostrar o contrato Solidity e os testes.

Documentos úteis:

- [`docs/PITCH.md`](docs/PITCH.md)
- [`docs/ROTEIRO_DEMO.md`](docs/ROTEIRO_DEMO.md)
- [`docs/REGRAS_HACKWEB_CHECKLIST.md`](docs/REGRAS_HACKWEB_CHECKLIST.md)
- [`docs/SUBMISSAO.md`](docs/SUBMISSAO.md)
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md)
- [`docs/SIMULADOR_COMPLETO.md`](docs/SIMULADOR_COMPLETO.md)

## Limitações do MVP

Este repositório usa dados simulados para demonstração. O uso produtivo exige calibração real do espectrofotômetro, validação laboratorial, política de privacidade, governança de dados, proteção de dados sensíveis e integração com hardware real.

## Licença

O código-fonte deste repositório está sob a licença **Apache License 2.0**.

A marca **Análise Evolutiva**, identidade visual, calibrações reais, bases laboratoriais, dados de produtores, modelos proprietários e metodologia comercial não estão licenciados para uso sem autorização expressa.


## Visão completa da Análise Evolutiva V11

Além do fluxo central do leite, esta versão inclui uma página para investidor e banca em `/ecossistema`. Ela simula todos os blocos estratégicos da Análise Evolutiva: bioinsumos/gotículas, solo e pastagem, raiz e predição, irrigação/ROI, leite Web3, hortifrúti, dashboards, laudos, governança e topologia IoT.

Endpoints adicionais:

```http
POST /api/ecosystem/simulation
POST /api/ecosystem/evidence
```

A estratégia é manter o leite como demonstração Web3 central e, ao mesmo tempo, mostrar que a plataforma tem expansão comercial para AgriTech/FoodTech em múltiplas matrizes de análise.


## Site institucional

Acesse `/site` para visualizar o site oficial da Análise Evolutiva dentro do MVP.


## Casos comerciais da cadeia do leite

A rota `/casos-leite` consolida os casos de uso comerciais extraídos do posicionamento institucional da Análise Evolutiva: Leite A2A2 Certificado, Leite Orgânico, Leite de Raça Específica, Detecção de Fraude, Rastreamento de Contaminação e Rastreabilidade de Lote. Essa tela foi adicionada para que avaliadores e investidores vejam claramente como a captura espectrofotométrica, a IA e a Web3 se convertem em produtos com potencial de retorno.

Endpoint correspondente:

```http
GET /api/use-cases/milk
```
