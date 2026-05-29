# Arquitetura técnica

## Objetivo

Demonstrar um fluxo Web3 aplicado à cadeia produtiva do leite, no qual a própria Análise Evolutiva realiza a análise da amostra com base em leitura espectrofotométrica e gera uma evidência digital rastreável.

## Camadas

### 1. Coleta e leitura espectrofotométrica

No MVP, a leitura é simulada. Em evolução produtiva, o módulo pode receber dados reais de um espectrofotômetro multiespectral, incluindo comprimentos de onda como 415, 445, 480, 515, 555, 590, 630, 680 e 910 nm.

### 2. Análise técnica

O backend executa regras demonstrativas para calcular:

- consistência espectral;
- risco de adulteração por água;
- risco por quebra de temperatura;
- índice de sólidos;
- score de conformidade;
- status final do lote.

### 3. Evidência digital

O resultado da análise é consolidado em JSON canônico. O sistema calcula o SHA-256 do conteúdo para criar uma prova de integridade.

### 4. Registro Web3

A arquitetura usa o padrão:

```text
evidência completa off-chain + hash on-chain
```

Isso preserva privacidade, reduz custo e mantém auditabilidade.

### 5. Smart contract

O contrato Solidity registra:

- hash da evidência;
- identificador do lote;
- identificador do produtor;
- URI/referência do laudo;
- status da análise;
- registrador;
- timestamp do bloco.

### 6. Verificação pública

A tela `/verify/<hash>` permite verificar se uma evidência foi registrada e se o hash local ainda confere com o conteúdo salvo.

## Decisão arquitetural

O MVP usa modo Web3 simulado no backend para permitir avaliação imediata sem carteira, chave privada ou RPC. O smart contract real está incluso e testável via Hardhat.
