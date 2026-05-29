# Roteiro da demonstração

## Tempo sugerido: 3 a 5 minutos

### 1. Apresentar o problema

Explicar que a cadeia do leite precisa comprovar qualidade, origem, temperatura, análise e integridade dos laudos.

### 2. Abrir o simulador do MVP

Acessar:

```text
http://127.0.0.1:5000/simulador
```

Explicar que esta tela foi criada para demonstrar a visão de produto para banca, usuário e investidor.

### 3. Explicar o fluxo

Mostrar na tela:

```text
Produtor → Coleta → Transporte → Cooperativa/Laboratório → Espectrofotômetro → Análise Evolutiva → Hash → Smart Contract → Verificação pública
```

### 4. Rodar uma amostra normal

Selecionar `Leite normal` e clicar em `Executar análise completa`.

Mostrar:

- status do lote;
- score de conformidade;
- risco de adulteração;
- temperatura da amostra;
- jornada rastreável;
- gráfico espectrofotométrico;
- recomendação técnica;
- hash da evidência;
- link de verificação pública.

### 5. Rodar uma amostra com problema

Selecionar:

- `Suspeita de adição de água`; ou
- `Quebra de temperatura`.

Explicar que o sistema altera os indicadores, gera nova evidência e recomenda revisão técnica, bloqueio preventivo ou contraprova conforme o cenário.

### 6. Mostrar verificação pública

Abrir o link `/verify/<hash>` gerado pelo simulador.

Explicar que o hash permite comprovar se a evidência foi alterada e que a estratégia do MVP é `off-chain evidence + on-chain hash`.

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
- experiência visual do produto;
- viabilidade técnica;
- evolução futura com hardware real, calibração laboratorial e rede blockchain pública/testnet.
