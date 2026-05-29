# Conformidade HackWeb 3.0 - Desafio ImpactLedger

## Desafio escolhido

**Desafio 3 - ImpactLedger | Trilha Blockchain + Smart Contracts**.

A Análise Evolutiva Web3 registra e certifica evidências de impacto ambiental, produtivo e sanitário da cadeia do leite. O MVP transforma leituras espectrofotométricas simuladas de solo/pastagem, alimentação, água e leite em evidências digitais verificáveis.

## Problema de impacto

A cadeia produtiva do leite depende de registros técnicos dispersos: laudos, temperatura, origem do lote, qualidade da água, alimentação do rebanho, condição de pastagem e análise da amostra. Esses registros podem ficar em planilhas, PDFs e sistemas internos, dificultando auditoria, certificação e confiança entre produtor, cooperativa, laticínio e consumidor.

## Ação de impacto registrada

A ação registrada é a **análise técnica e rastreável de um lote de leite**, incluindo contexto produtivo e evidência óptica. O registro demonstra impacto em:

- segurança alimentar;
- redução de fraudes;
- rastreabilidade de origem;
- auditoria ambiental/produtiva;
- valorização de boas práticas no campo.

## Evidências usadas

- leitura espectrofotométrica simulada 365-910 nm;
- corrente escura;
- branco de referência;
- leitura ADC;
- absorbância;
- diagnóstico técnico;
- status do lote;
- hash SHA-256 da evidência completa;
- endereço e transação do registro Web3 em modo simulado ou testnet.

## On-chain e off-chain

- **Off-chain:** evidência completa, laudo, dados técnicos e metadados sensíveis.
- **On-chain:** hash da evidência, lote, produtor pseudonimizado, URI/referência, status e certificação.

## Smart contract

O contrato `AnaliseEvolutivaLeiteTrace.sol` registra evidências e permite emitir certificação digital para uma evidência já registrada, representando aprovação, rastreabilidade ou selo de conformidade.

## Itens atendidos

| Requisito | Atendimento no projeto |
|---|---|
| Uso de blockchain | Camada Web3 simulada + contrato Solidity |
| Registro verificável de ações de impacto | Evidência técnica da cadeia do leite com hash |
| Histórico auditável | Banco local, tela de verificação e eventos do contrato |
| Smart contract funcional | Contrato Solidity com testes Hardhat |
| Repositório GitHub funcional | Estrutura pública preparada |
| Código minimamente comentado | Backend, contrato e documentos explicativos |
| README explicando funcionamento | README completo na raiz |
| Vídeo-pitch | Deve ser gravado e publicado no YouTube como não listado |
| Apresentação de slides | PDF incluído em `docs/Apresentacao_HackWeb_Analise_Evolutiva.pdf` |

## Pontos que dependem de execução externa

- publicar o repositório GitHub como público;
- gravar e subir o vídeo-pitch no YouTube como não listado;
- preencher o formulário oficial;
- opcionalmente, fazer deploy do contrato em Sepolia ou Polygon Amoy e atualizar o README com endereço/link da testnet.
