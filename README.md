# Análise Evolutiva Web3 — HackWeb 3.0 MVP

MVP funcional para rastreabilidade da cadeia produtiva do leite com análise espectral simulada, IA/regras de conformidade, geração de evidência digital, hash SHA-256, registro Web3 demonstrativo e smart contract Solidity.

## Objetivo

Demonstrar como a Análise Evolutiva pode realizar a análise técnica do leite por espectrofotometria e garantir rastreabilidade, integridade e auditabilidade do processo usando conceitos de Web3.

## Fluxo do MVP

1. Coleta do leite na propriedade.
2. Leitura multiespectral simulada pelo espectrofotômetro.
3. Análise automatizada da amostra.
4. Classificação do lote.
5. Geração do hash da evidência.
6. Registro Web3 demonstrativo.
7. Verificação pública da evidência.

## Estrutura

```text
backend/        API Flask, dashboard, simulador, testes
contracts/      Smart contract Solidity
scripts/        Scripts auxiliares de demonstração
docs/           Documentação da entrega e arquitetura
```

## Executar localmente

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest test_core.py
python app.py
```

Acesse:

```text
http://localhost:5000
```

## Executar com Docker

```bash
docker compose up --build
```

## Endpoints principais

```text
GET  /                         Dashboard
POST /api/amostras/simular     Gera nova amostra simulada
GET  /api/amostras             Lista amostras
GET  /api/verificar/<hash>     Verifica integridade em JSON
GET  /verificar/<hash>         Página pública de verificação
```

## Web3

O contrato `contracts/AnaliseEvolutivaLeiteTrace.sol` registra o hash da evidência, ID da amostra, lote, classificação e URI de metadados. Nesta entrega, o backend gera uma transação simulada. A próxima etapa é integrar Hardhat e rede de teste.

## Observação técnica

Os modelos e regras desta primeira entrega são demonstrativos. A calibração real depende de amostras laboratoriais, curva de calibração, controle de luminosidade, repetibilidade do hardware e validação estatística.
