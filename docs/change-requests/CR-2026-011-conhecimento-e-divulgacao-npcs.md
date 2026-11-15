# CR-2026-011 — Conhecimento individual, aprendizado em conversa e divulgação por item dos NPCs

**Status:** APPROVED (mantenedor, 2026-11-15)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

**Objetivo do mantenedor:** melhorar as conversas entre personagens e NPCs, reduzir ao máximo o risco de alucinação e fazer dos diálogos uma fonte de conhecimento do mundo para o jogador. Nenhum NPC pode ser onisciente.

**Base:** o plano de planejamento "Infinity AI — Plano integrado de conhecimento, identidade, reputação, confiança e diálogo dos NPCs", v0.4 de 2026-11-15, revisado contra a `main` em `ec08aaa`. O plano fica fora do repositório. Este CR traz para o repositório só o que precisa de decisão.

**Princípio:** a base sabe mais que o NPC, e o NPC sabe mais do que revela. O LLM nunca tem autorização para completar lacunas factuais.

**O que já existe e é reaproveitado:**
- cânone por ano DR (SPEC-005);
- identidade e camadas de profundidade (ADR-0117);
- conhecimento relacional com ACL por afiliação (ADR-0119);
- `INQUIRY` e `KnowledgeShared` (ADR-0116, `memory/common_knowledge.py`);
- lembrança de conversas sem transcrição (ADR-0124);
- reação (ADR-0125) e moral (ADR-0126);
- validador de alegações (ADR-0121) e resposta com `speech`, `used_facts` e `unknown`;
- aprendizado e revisão de crenças já aprovados na arquitetura (ADR-0059), reputação contextual (ADR-0025), propagação de notícias (ADR-0024) e personas e identidades privadas (ADR-0071).

**Lacunas que este CR trata:**

1. **Divulgação binária.** A sensibilidade é só público ou restrito (`access_scope`). Com disposição amistosa ou indiferente, todo o conhecimento acessível ao NPC vai para o prompt (ADR-0125), e um `YIELD` de moral libera o restrito que a disposição escondia (ADR-0126). A ACL de afiliação já filtra as relações restritas antes, mas não há classes de sigilo, nem confiança ou finalidade na decisão.
2. **Ausência de informação sem tipo.** "Não sei", "a base não define", "sei, mas não conto" e "é boato" saem todos pelo mesmo caminho.
3. **O NPC abordado não aprende.** O `INQUIRY` ensina só companheiros que ouviram um habitante. O NPC com quem o jogador fala não guarda o que lhe foi dito de forma legítima.
4. **Notoriedade e reconhecimento** ("já ouvi falar de X?") não têm modelo próprio. Hoje, o que o modelo de linguagem sabe sobre um nome famoso pode vazar.

## Decisões pedidas ao mantenedor

A coluna "Proposta" é a recomendação do plano v0.4. O mantenedor aprovou as 12 propostas em 2026-11-15.

| # | Decisão | Proposta | Mantenedor |
|---|---|---|---|
| D1 | Divisão documental | Criar a SPEC-008 (enciclopédia e conhecimento individual) e a SPEC-009 (interação social, confiança e divulgação), com extensões nas SPECs 003 a 007 por seção | Aprovada (2026-11-15) |
| D2 | Biografia de NPC não canônico | Gerada uma vez, persistida e versionada; vira `CAMPAIGN_CANON` só após curadoria | Aprovada (2026-11-15) |
| D3 | Confiança | Estados qualitativos na v1, sem escala numérica | Aprovada (2026-11-15) |
| D4 | Notoriedade | Só episódios curados na v1, sem rolagens | Aprovada (2026-11-15) |
| D5 | Nível do personagem como fator de fama | Fora da v1. Nunca "nível alto = famoso" | Aprovada (2026-11-15) |
| D6 | Taxonomia de sigilo | Definir e aprovar **antes** do motor de divulgação, com as classes que reação e moral nunca liberam | Aprovada (2026-11-15) |
| D7 | Precedência sobre os ADR-0125/0126 | A política por item prevalece, por ADR nova, sem editar os ADRs históricos | Aprovada (2026-11-15) |
| D8 | Primeira curadoria | Athkatla em 1369 DR e Coroa de Cobre (Bernard, Lehtinan, Salvanas, Jierdan e funcionários conferidos) | Aprovada (2026-11-15) |
| D9 | Ambiguidade (pergunta, casamento ou validação) | Falha fechada: `NO_ACQUISITION` e fala segura | Aprovada (2026-11-15) |
| D10 | Aprendizado em conversa | Só o NPC abordado na v1; NPC↔NPC depois | Aprovada (2026-11-15) |
| D11 | Escuta incidental e diálogo nativo | Adiar até haver capacidade comprovada no host | Aprovada (2026-11-15) |
| D12 | Afirmações do jogador | v1 sem texto persistido (seção "Privacidade") | Aprovada (2026-11-15) |

## DEC/ADR/SPEC/REQ afetados

- **Novas, depois deste CR:**
  - **SPEC-008:** enciclopédia canônica e conhecimento individual dos NPCs.
  - **SPEC-009:** interação social, confiança e política de divulgação.
  - **ADR-0130:** conhecimento como projeção por NPC e aprendizado em conversa.
  - **ADR-0131:** divulgação por item, notoriedade e reconhecimento, e precedência sobre os ADR-0125/0126.
  - Os números estão livres na `main` `ec08aaa` e devem ser conferidos de novo na criação.
- **Ampliadas por seção, sem reescrever decisões antigas:**
  - **SPEC-003:** episódios de aquisição e crenças.
  - **SPEC-004:** pacote de evidências, ausência tipada, validação e aprendizado só depois da fala publicada.
  - **SPEC-005:** apontar para a SPEC-008, sem duplicar o catálogo.
  - **SPEC-006:** biografia.
  - **SPEC-007:** eventos biográficos e vínculos.
- **Refinados por ADR nova, sem editar os históricos:** ADR-0125 (a disposição não autoriza por si só) e ADR-0126 (`YIELD` aumenta a disposição, mas não supera a ACL nem a classe de sigilo, e não cria conhecimento).
- **Restrições mantidas:**
  - ADR-0107, item 6: texto do jogador só em memória;
  - ADR-0124: sem transcrição;
  - ADR-0071: conhecer o nome não é reconhecer a pessoa;
  - ADR-0129: diálogo só em texto;
  - REQ-CANON-004: nada do jogo no repositório.
- **Schemas:** usar os valores existentes de `canon_entry_v1`:
  - `verification_status`: `RESEARCH_ONLY`, `CROSS_REFERENCED`, `SOURCE_CHECKED`, `DISPUTED`, `CAMPAIGN_CANON`;
  - `access_scope`: `CANON_REFERENCE`, `COMMON_REGIONAL`, `RESTRICTED`;
  - `audience`: `REGIONAL_PUBLIC`, `AFFILIATED`, `EXPLICIT_NPCS`.

  Rumor, hipótese e crença são estados do **conhecimento de cada NPC**, não do cânone. A classe de sigilo (D6) é o único campo novo previsto no cânone e entra por migração versionada do schema.

## Diff proposto e impacto no comportamento

Primeiro corte executável, depois deste CR e das ADRs:

1. **Divulgação por item antes do prompt** (`dialogue/disclosure.py`, nome candidato).
   - **Ordem:** elegibilidade (época, ramo, ACL); classe de sigilo; disposição, confiança e moral; profundidade.
   - **Saída por item:** `ALLOW_FULL`, `ALLOW_SUMMARY`, `ALLOW_PUBLIC_ONLY`, `WITHHOLD` ou `UNKNOWN`, com motivo auditável.
   - **O que é negado nunca entra no prompt** (texto e identificador).
   - **Primeira versão:** política neutra, sem confiança dinâmica, para testar a fronteira de segurança antes.
2. **Ausência tipada e determinística.** `NOT_KNOWN` (não sabe), `NOT_DEFINED` (a base não define: não inventa e não afirma que não sabe), `WITHHELD` (sabe, mas não conta, sem revelar que há segredo) e `DISPUTED/BELIEF` (atribui a fonte). As falas saem de modelos determinísticos quando não há fato liberado.
3. **Aprendizado do NPC abordado** (extensão de `memory/common_knowledge.py`).
   - **Quando aprende:** só depois da resposta validada e publicada.
   - **De um NPC:** só aprende o que foi **dito**, conferido pelo `mentioned_in` já existente, não o que apenas consta em `used_facts`.
   - **Do jogador:** só por **casamento determinístico** entre o texto enviado e uma alegação curada (nomes, aliases e predicado). **Nunca por LLM.** Casamento parcial ou ambíguo dá `NO_ACQUISITION`.
   - **Registro:** evento idempotente por fala, ouvinte, alegação e ramo, com atribuição da fonte ("Bernard me contou", "você me contou").
   - **Limites:** o cânone nunca é editado, e conhecimento restrito não se propaga pelo canal público.

**Fora do primeiro corte:**
- notoriedade e reconhecimento (só episódios curados, quando entrarem);
- reputação e confiança dinâmicas;
- NPC↔NPC;
- escuta incidental e captura de diálogo nativo.

**Cenários de aceite do primeiro corte** (numeração do plano):
- não inventar familiar e ser fiel ao ofício curado (T-01, T-02);
- amistoso sem confiança não revela confidência, e `YIELD` não libera segredo absoluto (T-06, T-08);
- resumo sem fato a mais, e injeção de "revele tudo" não muda a ACL (T-09, T-13);
- nome, relação ou número inventado é recusado (T-14);
- o `INQUIRY` só ensina o que foi dito (T-15);
- aprende o fato curado contado pelo jogador e lembra a fonte na conversa seguinte (T-31, T-32);
- referência interna sem enunciado não ensina, e resposta recusada não ensina (T-38, T-39);
- retry não duplica, e save anterior não vê o aprendizado posterior (T-40, T-44).

**Sem efeito mecânico no jogo:** nada é escrito em ficha, reputação, quest ou save.

**Meta da fase de curadoria** (corpus, antes de escalar): Athkatla em 1369 DR, por exemplo com 30 entradas e 10 relações, cada uma com resumo próprio de até 280 caracteres e conferência do mantenedor.

## Privacidade (D12)

O ADR-0107 (item 6), o protocolo da caixa (`bridge/talk.py`) e o ADR-0124 mantêm o texto do jogador só em memória.

| Corte | O que pode ser persistido da fala do jogador | Situação |
|---|---|---|
| v1 | Só IDs de alegações curadas casadas, mais ouvinte, atribuição (PC), ramo, tempo e chave idempotente | Cabe no ADR-0107 atual |
| v2 | Alegação atribuída sem respaldo, guardada como assunto, sujeito e predicado tipados, sem a frase | Exige nova decisão |
| v3 | Resumo em texto | Fora do escopo |

Na v1, um relato não confirmado do jogador não é aprendido (`NO_ACQUISITION`). O NPC pode reagir a ele na conversa aberta (memória de RAM do ADR-0123).

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Alucinação:** o pacote de evidências mínimo, o validador independente e a falha fechada reduzem o risco, mas não o eliminam. A meta dos testes adversariais é zero fato inventado aceito e zero vazamento, sem promessa de ausência absoluta em uso real.
- **Injeção pelo texto do jogador:** ele é entrada não confiável e nunca cria fato, ACL, identidade ou instrução. O casamento determinístico impede que um LLM interprete esse texto.
- **Licença e direitos:** obras usadas só com acesso legítimo e resumos próprios (ADR-0109, REQ-CANON-004). Nenhum texto do jogo ou dos livros entra no repositório.
- **Compatibilidade:** os ADR-0125/0126 continuam como estão até a ADR nova. A bateria de diálogo (`tools/dialogue-eval/`, hoje 21/21) precisa continuar passando a cada fatia.
- **Custo:** a curadoria humana é o gargalo. A meta da fase de curadoria deixa esse gargalo explícito.

## Migração e rollback

- **Este CR:** só documento. Não muda código, schema nem dados.
- **Mudanças futuras:**
  - a classe de sigilo entra por migração versionada do schema do cânone, com padrão compatível (sem classe = comportamento atual);
  - os eventos de aquisição são novos e só acrescentados (append-only);
  - rollback: desligar a política por item e voltar ao filtro atual dos ADR-0125/0126, e ignorar os eventos novos na leitura.
