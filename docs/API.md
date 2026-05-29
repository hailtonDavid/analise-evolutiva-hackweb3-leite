# API

## `GET /health`

Retorna status da aplicação.

## `POST /api/samples/simulate`

Gera uma amostra simulada.

Payload:

```json
{
  "scenario": "normal",
  "seed": 123
}
```

Cenários aceitos:

- `normal`
- `water_adulteration`
- `temperature_break`
- `high_solids`

## `POST /api/evidence`

Recebe uma amostra, analisa, gera evidência e registra o hash.

## `GET /api/evidence/<evidence_id>`

Consulta evidência por ID.

## `GET /api/verify/<evidence_hash>`

Verifica evidência por hash.

## `GET /verify/<evidence_hash>`

Tela pública de verificação.
