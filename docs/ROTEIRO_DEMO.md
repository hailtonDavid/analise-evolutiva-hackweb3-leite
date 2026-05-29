# Roteiro da demonstração

## Tempo sugerido: 3 a 5 minutos

### 1. Apresentar o problema

Explicar que a cadeia do leite precisa comprovar qualidade, origem, temperatura, análise e integridade dos laudos.

### 2. Abrir o sistema

Acessar:

```text
http://127.0.0.1:5000
```

### 3. Explicar o fluxo

Mostrar na tela:

```text
Produtor → Coleta → Transporte → Cooperativa → Espectrofotômetro → Análise Evolutiva → Hash → Smart Contract → Verificação pública
```

### 4. Rodar uma amostra normal

Selecionar `Leite normal` e clicar em `Gerar evidência rastreável`.

Mostrar:

- lote;
- produtor;
- status;
- score de conformidade;
- hash;
- transaction hash simulado.

### 5. Rodar uma amostra com problema

Voltar para a página inicial e selecionar:

- `Suspeita de adição de água`; ou
- `Quebra de temperatura`.

Explicar que o sistema altera o score e recomenda revisão ou bloqueio.

### 6. Mostrar verificação pública

Abrir o link `/verify/<hash>`.

Explicar que o hash permite comprovar se a evidência foi alterada.

### 7. Mostrar o smart contract

Abrir o arquivo:

```text
contracts/AnaliseEvolutivaLeiteTrace.sol
```

Explicar que o contrato registra o hash, lote, produtor, status, registrador e timestamp.

### 8. Encerramento

Reforçar:

- aderência Web3;
- impacto na cadeia do leite;
- viabilidade técnica;
- evolução futura com hardware real e rede blockchain pública/testnet.
