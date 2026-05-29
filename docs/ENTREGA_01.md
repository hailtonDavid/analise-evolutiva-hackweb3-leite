# Entrega 01 — MVP técnico

## Entregue

- Backend Flask funcional.
- Simulação de leitura espectrofotométrica do leite.
- Análise técnica automatizada.
- Geração de evidência digital.
- Hash SHA-256 da evidência.
- Registro Web3 simulado.
- Página pública de verificação.
- Smart contract Solidity.
- Ambiente Hardhat.
- Testes automatizados Python.
- Dockerfile e docker-compose.
- Documentação de arquitetura, pitch, submissão e roteiro de demonstração.

## Como validar rapidamente

```bash
python -m pip install -r backend/requirements.txt
python -m pytest -q
cd backend
python app.py
```

Acesse:

```text
http://127.0.0.1:5000
```

## Evolução recomendada

- Integrar espectrofotômetro físico.
- Treinar modelo com dados laboratoriais reais.
- Registrar contrato em testnet.
- Integrar carteira digital.
- Gerar laudo PDF assinado.
- Adicionar QR Code para verificação pública.
