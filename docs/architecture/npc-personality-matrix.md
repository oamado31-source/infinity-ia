# Arquitetura — matriz de personalidade, ações e alinhamento

Documento de referência da [SPEC-006](../../specs/006-personalidade-alinhamento-npc/spec.md), em estado **PROPOSTO** (2026-11-09).

## Representação em camadas

| Camada | Variáveis | Frequência / Origem | Pode mudar? |
|---|---|---|---|
| Identidade | npc_id, criação, tipo, fonte, versão | Após gate de identidade | Não silenciosamente |
| Personalidade-base | H/E/X/A/C/O (0–100) | Curadoria oficial ou sorteio único de NPC novo | Revisão explícita, futura |
| Alinhamento inicial | LG/NG/CG/LN/TN/CN/LE/NE/CE | Fonte canônica ou sorteio único independente | Inicial, não reescrever |
| Valores e motivadores | ranked values, drives, vulnerabilities | Curadoria/sorteio inicial | Evolução autorizada futura |
| Estado emocional | medo, raiva, alegria, cansaço etc. | Episódio/condição, TTL verificável | Transitório |
| Relações e crenças | confiança, memória, opinião, rumor | Experiências e conhecimento legítimos | Sim, auditável e por ramo |
| Alinhamento narrativo | dois eixos e evidência contextual | Eventos confirmados + regra | Gradualmente, sem engine |
| Alinhamento do jogo | valor mecânico BG2:EE | Leitura com capacidade validada | Apenas host/gateway/POC |

## Aleatoriedade controlada

Sorteio é **uma vez por nova identidade**, nunca por fala, mapa, cliente ou recarregamento. A chave de geração inclui política, campanha, ramo de criação, world seed e npc_id; o snapshot deve ser armazenado com proveniência e usado como autoridade após a criação. Alterar pesos, RNG, versão ou mundo não reescreve NPC existente. Em ramo divergente, só NPC criado **depois** do fork pode receber outro perfil, sem perder a memória do ancestral. Os pesos da matriz de alinhamento aceitam zero e bloqueiam negativos, NaN, infinitos e distribuições de soma zero. A distribuição neutra 1:1 em nove classes é apenas um baseline sintético.

## Matriz de alinhamento AD&D

| Ética | GOOD | NEUTRAL | EVIL |
|---|---|---|---|
| LAWFUL | LG | LN | LE |
| NEUTRAL | NG | TN | NE |
| CHAOTIC | CG | CN | CE |

Os eixos medem orientação narrativa para regras/autoridade e preocupação moral, **não** organizam automaticamente HEXACO. O rótulo de alinhamento é orientação inicial, não garantia de atitude. Personagens oficiais preservam valores do jogo conferidos; não se deve criar o alinhamento que falta para preencher o JSON.

## Exemplo de reação (hipotético)

Ao ouvir **por canal válido** que um comerciante foi acusado injustamente:
- Um NPC CG e extrovertido pode defender o comerciante em público, se seu desejo de justiça superar o risco.
- Um NPC LG e reservado pode procurar provas e canais institucionais, se confiar nas instituições.
- Um NPC LE e amável pode tentar instrumentalizar a acusação para obter favores, se a oportunidade e seus objetivos forem coerentes.

O exemplo não gera evento, quest flag, moralidade automática nem segredo adquirido. Antes de reagir, o motor checa: conhecimento válido no branch/tempo → perfil e relações autorizados → regras e risco → proposta narrativa → saída validada. Somente o host pode confirmar efeitos mecânicos.

## Uso no diálogo

O contexto de personalidade deve ser independente dos itens F/K e **nunca** criar novos fatos. O prompt recebe traços e estilo com orçamento limitado apenas para o próprio NPC; segredos pessoais só quando a finalidade e ACL permitem. `unknown=true` continua válido quando falta conhecimento; voz e LLM falhos não afetam estado. Testes devem verificar que duas personas diferem no modo de expressar o mesmo F/K **sem divergência factual**, e que loading de save não troca a personalidade.

## Limitações verificadas

Há **gerador e primeiro-contato sintéticos**, incluindo perfis temporários, atribuição append-only para identidades verificadas em eventos de teste e resposta textual local independente, em `src/infinity_ai/personality/`. Ainda não existem schema formal, observação real do clique/identidade via EEex, vínculo de NPCs oficiais, memória dinâmica de figurantes nem POC real. O diálogo da party existente permanece inalterado. A política de pesos/defaults é passível de revisão do mantenedor.

## Referências

- HEXACO (descrições dos fatores): https://www.hexaco.org/scaledescriptions — terminologia de inspiração científica, sem cópia de itens do inventário.
- `docs/35-*`, `docs/36-*`, `docs/37-*`: distinção narrativa/mecânica, moralidade, reputação e classe em AD&D.
- ADR-0042: autonomia narrativa e preservação do personagem clássico; ADR-0062: promoção com identidade positiva.
- `specs/003-*`: memória por campanha e ramo; `specs/004-*`: diálogo e limites de conhecimento.

## Todos os habitantes são NPCs potenciais

No sentido do Infinity AI, **NPC abrange qualquer pessoa** que esteja presente em cena: mendigo, aldeão, plebeu, guarda, comerciante, viajante, nobre, aventureiro, inimigo ou companheiro. Não significa uma classe, grupo de combate nem somente personagem com diálogo original. A matriz só é materializada em resposta a interação elegível: a população de fundo não recebe um LLM/estado persistente a cada tick.

```text
Clique / tentativa de diálogo → probe comprovado (ainda PENDENTE)
  → NpcDialogueStarted (observação autorizada; cena, alvo, tempo, sessão)
    → CANONICAL: personagem curado, não randomizar
    → CANDIDATE / AMBIGUOUS / STALE: perfil de encontro efêmero
    → VERIFIED + prova correspondente: consultar ou gravar snapshot append-only
      → diálogo sob demanda + validação (sem facts/knowledge inventados)
      → memória / relações / evolução SOMENTE após gates próprios
```

Reencontrar o mesmo ator **na sessão/cena** com token de instância confiável reutiliza perfil efêmero; reabrir save/instância sem identidade validada não autoriza vincular memórias. NPC verificado recebe perfil estável no banco de campanha, herdado apenas pelos ramos que contêm sua atribuição inicial. Alinhamento da matriz não altera automaticamente `engine_alignment`.

**Contratos no código:** `FirstContactService`, `NpcEncounterDialogue`, endpoint laboratorial `POST /v1/encounter-dialogue` que referencia evento já gravado. **Não confundir com POC:** o probe atual não emite `NpcDialogueStarted` nem comprova clique universal em criaturas no BG2:EE.
