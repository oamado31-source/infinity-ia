# Evidência S1z — ADR-0138: presença decidida pela quest (2026-11-22)

**Gate:** etapa 1, single player, save descartável; ADR-0138 sobre o gateway do P3 (ADR-0136).
**Resultado:** **APROVADO no laboratório ARM64/VM.** A quest de teste pôs e tirou a visão de Tamoko do mapa sozinha, pelo avanço da quest, com o jogo confirmando cada ação. Os sete pontos da proposta passaram.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Coroa de Cobre, AR0406, saves descartáveis no Capítulo 2) e Claude Code (serviço do laboratório com `--quest-presence` e `--local-quests`).

## Preparação

- **Quest de teste só local** (`~/.infinity-ai/quests/local/teste-presenca.pt_BR.json`, fora do repositório, D4):
  - Bernard oferece ("fantasma") e o grupo aceita ("vou investigar");
  - o passo é falar com a visão, e a entrega volta a Bernard;
  - presença: `IATAMOKO` (nome `INFAI_TAMOKO`) na AR0406, da quest aceita até a quest resolvida.
- **Quest de falha, também local** (`teste-falha`): a presença pede `IAFALTA`, que não está instalado.
- O serviço mostrou as criaturas nossas instaladas (`IAP3TEST`, `IATAMOKO`) ao ligar o diretor.

## Os sete pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Aceitar cria | ramo `br-9533daced9ec`: quest `ACEITA(0)`; o diretor pediu `ENTER IATAMOKO` sozinho, `HOST_CONFIRMED`; ela apareceu perto do grupo |
| 2 | Sair e voltar | saída e volta pela porta da taverna (`AreaEntered` duas vezes), sem nenhum pedido ao jogo; uma Tamoko só |
| 3 | Salvar e recarregar | salvo num slot novo e recarregado (`SessionStarted`), sem pedido; uma Tamoko só |
| 4 | Save anterior | o save ANTES-ACEITAR abriu o ramo `br-ef5b03145070`: quest `NOVA`, registro vazio, Tamoko ausente, sem pedido |
| 5 | Resolver remove | ramo `br-00f34ef9515e`, numa linha só desde o ANTES-ACEITAR: aceita (`ENTER`, `HOST_CONFIRMED`), passo com a visão (`ACEITA(1)`), entrega a Bernard (`RESOLVIDA`); o diretor pediu `LEAVE INFAI_TAMOKO`, `HOST_CONFIRMED`; ela sumiu |
| 6 | Falha forçada | quest `teste-falha` aceita: o gateway recusou antes do jogo (`REFUSED:UNKNOWN_TEMPLATE`); a presença ficou suspensa (`QuestPresenceSuspended`), com um aviso só; nenhum pedido gravado nem enviado, nenhuma nova tentativa |
| 7 | Sem `--quest-presence` | serviço sem a opção: quest aceita (`ACEITA(0)`), nenhum pedido; Tamoko não apareceu |

## O que apareceu no caminho

1. **Registro herdado de outra linha do tempo.** O primeiro save carregado era de outra linha, com tempo de jogo posterior ao da criação do teste de 18/11. O ramo acreditava que Tamoko estava na taverna, e o diretor não a criou.
   - O `despawn` do mantenedor recebeu do módulo `NOT_FOUND` com contagem 0.
   - Correção: essa resposta passou a valer como confirmação de que não sobrou nenhuma (`HOST_CONFIRMED`). Na leitura seguinte, o diretor criou Tamoko.
   - Teste novo em `tests/test_quest_presence.py`; ADR-0138, item 9.
2. **Save posterior de outra linha não abre ramo.** O save do ponto 3, carregado depois do ANTES-ACEITAR, passou por continuação do ramo, e Tamoko respondeu sem o fato do passo.
   - O diretor não fez nada errado, mas, nesse estado, aceitar de novo criaria uma segunda criatura.
   - Registrado na ADR-0138 (item 9). A contagem antes de criar entra com a peça G. O ponto 5 foi refeito numa linha só.
3. **Pontos 2 e 3, primeira tentativa:** rodaram em saves de 18/11, com a quest `NOVA` e a Tamoko daquele teste. Foram refeitos no ramo certo e só valem na segunda vez.
4. **Reação de Bernard:** uma rolagem ameaçadora (2d10 = 17) fecha a conversa, e nenhuma quest anda (ADR-0125). Bastou recarregar.
5. **Saída da Coroa no Capítulo 1** leva o jogo ao Capítulo 2 (script do jogo); o teste seguiu no Capítulo 2.

## Limites

- A verificação automática da presença no jogo, ao entrar e antes de criar, espera a operação de contagem (peça G).
- O ponto fixo de aparição fica para quando o lugar for curado (D2); hoje ela aparece perto do líder.
- "À noite" e objetivos de área são da peça B. Multiplayer (P4) está fora.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
