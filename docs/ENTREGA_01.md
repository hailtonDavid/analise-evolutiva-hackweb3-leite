# Entrega 01 — Análise Evolutiva Web3 para a Cadeia Produtiva do Leite

## 1. Proposta

A Análise Evolutiva Web3 é um MVP para registrar e verificar evidências técnicas da cadeia produtiva do leite. O sistema simula o processo completo: coleta da amostra, leitura multiespectral pelo espectrofotômetro, análise de conformidade, geração de hash, registro Web3 e verificação pública da integridade da evidência.

## 2. Problema

A cadeia produtiva do leite depende de análises de qualidade, registros de origem, transporte, recebimento e rastreabilidade. Em muitos cenários, os dados ficam espalhados em planilhas, PDFs, laudos e sistemas isolados. Isso dificulta comprovar se uma amostra pertence a determinado produtor, se o laudo foi alterado, quando a análise foi feita e qual lote foi afetado.

## 3. Solução

O MVP usa a Análise Evolutiva como agente técnico de análise. A plataforma recebe ou simula leituras espectrais, interpreta os dados, classifica o lote, cria uma evidência digital e gera um hash SHA-256. Esse hash pode ser registrado em smart contract, preservando a integridade do laudo sem expor dados sensíveis na blockchain.

## 4. Fluxo de demonstração

1. Coleta da amostra na propriedade.
2. Transporte resfriado e recebimento na cooperativa.
3. Leitura pelo espectrofotômetro multiespectral.
4. Análise automatizada de conformidade.
5. Geração do hash da evidência.
6. Registro Web3 em modo demonstrativo.
7. Verificação pública do hash e da cadeia registrada.

## 5. Componentes entregues

- Backend Flask com API REST.
- Simulador de leitura multiespectral do leite.
- Motor de análise de conformidade/adulteração para o MVP.
- Banco SQLite local.
- Tela web de dashboard.
- Tela pública de verificação de evidência.
- Smart contract Solidity para registro de evidências.
- Testes unitários do núcleo de simulação e integridade.
- Dockerfile e docker-compose.

## 6. Como executar

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest test_core.py
python app.py
```

Depois, acesse:

```text
http://localhost:5000
```

Ou via Docker:

```bash
docker compose up --build
```

## 7. Onde publicar

Para submissão, recomenda-se disponibilizar:

- Código-fonte em repositório público no GitHub.
- README com instalação, execução, arquitetura e prints.
- Smart contract na pasta `contracts/`.
- Vídeo curto de demonstração com o fluxo completo.
- Link do deploy do frontend/backend, quando possível.
- Link público de verificação de uma evidência gerada.

## 8. Próxima entrega

A Entrega 02 deve evoluir este MVP para uma versão com integração Web3 mais concreta: Hardhat, deploy em rede local/testnet, conexão com carteira, chamada real do contrato e gravação do hash em blockchain de teste.
