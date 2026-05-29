# Análise Evolutiva HackWeb 3.0 — Cadeia Produtiva do Leite

> Rastreabilidade Web3 da cadeia produtiva do leite com espectrofotometria, análise automatizada, geração de evidência digital, hash criptográfico e smart contract.

## Visão geral

A **Análise Evolutiva Web3** é um MVP criado para o HackWeb 3.0 com foco na cadeia produtiva do leite. A proposta é demonstrar como uma análise técnica realizada pela própria Análise Evolutiva, a partir de leituras espectrofotométricas, pode gerar uma evidência digital verificável e rastreável.

O sistema simula o fluxo completo:

```text
Produtor rural → Coleta da amostra → Transporte resfriado → Cooperativa/Laboratório
→ Espectrofotômetro → Análise Evolutiva → Hash da evidência
→ Registro Web3/Smart Contract → Verificação pública → Auditoria do lote
```

A blockchain não armazena o laudo completo. Ela registra a prova de integridade da evidência, reduzindo custo, preservando dados sensíveis e permitindo auditoria futura.

## Problema

A cadeia produtiva do leite depende de análises de qualidade, laudos, registros de coleta, transporte, temperatura e conformidade. Na prática, essas informações podem ficar espalhadas em planilhas, PDFs, sistemas internos e documentos difíceis de auditar.

Isso dificulta responder com segurança:

- a amostra analisada corresponde ao lote informado?
- quem realizou a análise?
- quando a evidência foi gerada?
- o laudo foi alterado depois da análise?
- o lote foi aprovado, reprovado ou ficou em atenção?
- existe histórico rastreável da cadeia produtiva?

## Solução

O MVP demonstra uma plataforma capaz de:

1. simular ou receber uma leitura espectrofotométrica do leite;
2. analisar a amostra com regras técnicas demonstrativas;
3. classificar o lote como `APROVADO`, `ATENÇÃO` ou `REPROVADO`;
4. gerar uma evidência digital em JSON;
5. calcular o hash SHA-256 da evidência;
6. registrar o hash em uma camada Web3 simulada ou smart contract;
7. disponibilizar uma página pública de verificação.

## Diferencial Web3

O diferencial está em transformar uma análise técnica da cadeia do leite em uma evidência digital verificável. O hash do relatório permite comprovar que o conteúdo não foi alterado. O smart contract cria uma trilha de auditoria pública, transparente e resistente a adulterações.

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
| GET | `/health` | Saúde da aplicação |
| POST | `/api/samples/simulate` | Gera leitura espectrofotométrica simulada |
| POST | `/api/evidence` | Analisa a amostra, gera evidência e registra hash |
| GET | `/api/evidence/<evidence_id>` | Consulta uma evidência pelo ID |
| GET | `/verify/<evidence_hash>` | Página pública de verificação |
| GET | `/api/verify/<evidence_hash>` | Verificação em JSON |

## Exemplo rápido via cURL

```bash
curl -X POST http://127.0.0.1:5000/api/samples/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"normal"}'
```

Depois envie a leitura retornada para:

```bash
curl -X POST http://127.0.0.1:5000/api/evidence \
  -H "Content-Type: application/json" \
  -d @data/sample_payload.json
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
2. explicar o problema de rastreabilidade na cadeia do leite;
3. simular uma amostra normal;
4. gerar a análise da Análise Evolutiva;
5. mostrar o hash da evidência;
6. mostrar o registro Web3;
7. abrir a tela pública de verificação;
8. explicar que qualquer alteração no laudo mudaria o hash;
9. mostrar o contrato Solidity e os testes.

Documentos úteis:

- [`docs/PITCH.md`](docs/PITCH.md)
- [`docs/ROTEIRO_DEMO.md`](docs/ROTEIRO_DEMO.md)
- [`docs/REGRAS_HACKWEB_CHECKLIST.md`](docs/REGRAS_HACKWEB_CHECKLIST.md)
- [`docs/SUBMISSAO.md`](docs/SUBMISSAO.md)
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md)

## Limitações do MVP

Este repositório usa dados simulados para demonstração. O uso produtivo exige calibração real do espectrofotômetro, validação laboratorial, política de privacidade, governança de dados, proteção de dados sensíveis e integração com hardware real.

## Licença

O código-fonte deste repositório está sob a licença **Apache License 2.0**.

A marca **Análise Evolutiva**, identidade visual, calibrações reais, bases laboratoriais, dados de produtores, modelos proprietários e metodologia comercial não estão licenciados para uso sem autorização expressa.
