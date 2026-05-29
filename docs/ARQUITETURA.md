# Arquitetura do MVP

```text
[Produtor / Fazenda]
        |
        v
[Coleta da Amostra de Leite]
        |
        v
[Espectrofotômetro Multiespectral]
        |  leitura AS7341 simulada: 415nm a 910nm
        v
[Backend Flask]
        |  análise, classificação, armazenamento
        v
[Hash SHA-256 da Evidência]
        |
        +------------------> [SQLite / Histórico]
        |
        v
[Smart Contract Solidity]
        |  registra hash + metadados mínimos
        v
[Verificação Pública]
```

## Decisão técnica

O laudo completo não deve ser gravado na blockchain. O sistema registra o hash e metadados mínimos. Assim, reduz custo, preserva privacidade e permite auditoria da integridade do documento.
