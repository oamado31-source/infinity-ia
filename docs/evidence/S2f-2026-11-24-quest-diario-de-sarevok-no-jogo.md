# Evidência S2f — a quest "O diário perdido de Sarevok" no jogo: ADR-0144, CR-2026-033 e ADR-0145 (2026-11-24)

**Gate:** etapa 1, single player, saves descartáveis (DIARIO-INICIO, DIARIO-ACEITA, DIARIO-VISAO e DIARIO-GREGOR).
**Resultado:**
- **aprovado no laboratório ARM64/VM** do começo da quest até a saída de Gregor (pontos 1 a 3);
- **o esconderijo (ponto 4) fica para uma área nova** (CR-2026-034): as Docas não têm interior livre.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Capítulo 2) e Claude Code (serviço com `--quest-presence`, `lab_action.py`).

## Preparação

- Quest curada `knowledge/quests/sarevok-diary.pt_BR.json`, com as curadorias revistas de Garoll, Tamoko e Gregor.
- Módulo com `CALL`, `ESCAPE` e o plano de chegada, instalado com o jogo fechado; SHA-256 conferido igual ao do ramo a cada instalação; manifesto refixado antes e depois do serviço.

## Os pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | O chamado de Garoll (ADR-0144) | "Alguém pode me ajudar?!" sobre a cabeça dele, sem som, confirmado pelo jogo e repetido a cada 1500 ticks; depois do aceite, não voltou (último às 16:21:28, aceite às 16:22:38). Logo depois de carregar um save, a legenda pode passar sem ser vista: ela só aparece com Garoll na tela |
| 1 | A oferta e o aceite | Textos de Garoll refeitos com o mantenedor durante o teste (detalhes do fantasma, sacerdotisa, ele fica na Coroa, pergunta se o grupo aceita). As palavras de aceite foram ampliadas duas vezes ("Vamos ajudar você", "Iremos investigar", "Podemos ir lá investigar") |
| 1 | O pedido em primeiro e o jeito de falar (CR-2026-033) | Garoll passou a contar do fantasma em vez de pedir bebida, falando como bêbado ("Pra ir lá, no cemitério... hic..."); o mantenedor: "ficou boa a fala dele agora" |
| 2 | A visão de Tamoko | Às 20h16 no Cemitério, nada; depois das 21h, ela apareceu. Primeira fala fraca ("morri aqui", inventado, e o fato da quest ausente); depois do jeito de falar de visão e do fato 2 revisto, "Agentes do Trono de Ferro... eles queriam o diário de Sarevok..." (mantenedor: "Ficou boa") |
| 3 | O casarão (AR0409) com a chegada preparada (ADR-0145) | Plano gravado no aceite. **1ª tentativa:** o módulo agiu antes de o grupo ser posto na área e nada foi criado; presenças retidas. **2ª:** já estavam lá ("Já estavam lá"), mas retidas pela conta de grupo (área +3 para Gregor +1 e carcereiros +2). **3ª:** confirmadas pela soma, sem duplicação; derrota vista; Gregor contou de Kalessia e do galpão e saiu pela porta (`ESCAPE` confirmado às 18:22:16) |
| 4 | O esconderijo | AR0331 (o mantenedor viu minotauros na AR0330 e o sarcófago de Kangaxx) e AR0318 (contrabandistas de pontos de surgimento; nem o plano nem o diretor criaram a célula) descartadas. CR-2026-034: área nova `IA0001` |

## O que apareceu no caminho

1. **Fila do jogo e combate (ADR-0142/0143):** sem problema nesta quest; os carcereiros nasceram juntos.
2. **Retenção e duplicação:** os carcereiros, retidos pela conta de grupo e liberados à mão, não contaram como criados pela quest. Ao morrerem, o diretor os recriou (regra da ADR-0140). Com a correção da conta, isso não voltou.
3. **O passo da quest e a fala:** o diário da quest às vezes registrava algo que a pessoa não tinha dito. A CR-2026-033 (fato marcado `(agora)`, segunda tentativa) reduziu isso; Tamoko segue sendo o caso mais difícil.
4. **Banco preso (`OperationalError`):** uma vez, logo depois de carregar um save, a caixa e o diretor falharam com o banco preso por mais de 5 s. Não se repetiu; a correção (esperar mais ou outro modo do SQLite) fica registrada à parte.
5. **Áreas com pontos de surgimento:** a escolha de interiores passou a olhar também os pontos de surgimento do `ARE`, não só as criaturas fixas e o script.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Suíte com 644 testes; bateria de diálogo 68/68, com os casos novos de Garoll, Tamoko e Gregor.
