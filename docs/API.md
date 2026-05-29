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


## Ecossistema completo

### POST /api/ecosystem/simulation

Gera a simulação completa da Análise Evolutiva V11, incluindo módulos de gotículas, solo, raiz, predição, irrigação, leite Web3, hortifrúti, dashboards e governança.

### POST /api/ecosystem/evidence

Gera uma evidência digital do ecossistema completo com hash SHA-256 e registro Web3 simulado.


## Site institucional integrado

### `GET /site`

Disponibiliza o site oficial da Análise Evolutiva dentro do MVP, com visualização incorporada e botão de abertura em nova aba.

### `GET /api/site/meta`

Retorna metadados da integração do site institucional.
