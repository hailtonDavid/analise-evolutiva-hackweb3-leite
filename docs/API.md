# API — Análise Evolutiva Web3

## Saúde

```http
GET /health
```

## Simulação simples do leite

```http
POST /api/samples/simulate
Content-Type: application/json

{
  "scenario": "normal",
  "seed": 42
}
```

## Evidência simples do leite

```http
POST /api/evidence
Content-Type: application/json

{ ...amostra retornada por /api/samples/simulate... }
```

## Simulação completa da cadeia

```http
POST /api/simulator/full-process
Content-Type: application/json

{
  "scenario": "integrated_risk",
  "seed": 42
}
```

Retorna o processo completo com:

- solo/pastagem;
- alimentação;
- água;
- leite;
- captura óptica por canal;
- análise integrada;
- jornada rastreável.

## Evidência completa da cadeia

```http
POST /api/evidence/full-process
Content-Type: application/json

{
  "scenario": "integrated_risk",
  "seed": 42
}
```

Retorna:

- processo completo;
- evidência digital;
- hash SHA-256;
- registro Web3 simulado.

## Verificação pública

```http
GET /verify/<evidence_hash>
```

## Verificação JSON

```http
GET /api/verify/<evidence_hash>
```


## POST /api/spectrometer/session

Executa somente a simulação da sessão do espectrofotômetro.

Payload:

```json
{
  "scenario": "normal",
  "seed": 42
}
```

Retorno principal:

- `session_id`;
- `equipment`;
- `telemetry`;
- `self_test`;
- `workflow`;
- `sample_cycles` com solo, alimentação, água e leite;
- `led_sweep` por comprimento de onda;
- `quality_control` por matriz.
