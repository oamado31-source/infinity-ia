# CR-2026-034 — Uma área nova para o esconderijo da célula

**Estado:** APROVADA (mantenedor, 2026-11-24: "Aprovar como proposta", D1 a D3 na opção recomendada). **Fase 1 (pesquisa) pendente.**

**Origem:** o teste da quest "O diário perdido de Sarevok" (ADR-0145, evidência S2f) mostrou que as Docas não têm interior livre para a célula de Kalessia:

| Área | O que é |
|---|---|
| AR0331 | início da quest de Kangaxx (o Crânio Dourado), atrás de minotauros na AR0330 |
| AR0318 | pontos de surgimento de contrabandistas (`RDSMUG`) |
| AR0321 a AR0324 | Thief Stronghold |
| AR0328 | Shadow Thief Stronghold |
| AR0304 | outro lugar da história |

O BG2 não tem nenhuma área do Trono de Ferro em Athkatla: no texto do jogo, o Trono de Ferro só aparece em falas do BG1, do Trono de Bhaal e de companheiros da EE.

**Relaciona-se com:**
- SPEC-010, que é proposta e deixa "criar mapas" e "instalar mods" fora do escopo; esta CR abre uma exceção só de laboratório;
- CR-2026-032 (recursos convertidos), ADR-0145 (chegada preparada) e ADR-0144 (operações do gateway).

## Mudança

1. **Fase 1, pesquisa (D1), sem instalar nada:**
   - candidatos com interior pequeno, tipo galpão ou armazém:
     - Dark Tidings (AciferBG, áreas do distrito portuário de Athkatla);
     - IWD1_EET;
     - NWNForBG;
     - um recorte de sala vazia do próprio BG2 com nome nosso;
   - de cada um: licença, tamanho, arquivos (`ARE`, `WED`, `TIS`, `MOS` e os três `BMP`) e se o `ARE` precisa de conversão para o BG2:EE;
   - escolher, com o mantenedor no jogo, uma porta do cenário das Docas que hoje não abre.
   - **a ideia do mantenedor (2026-11-24), um barco:** a célula escondida num navio atracado nas Docas, e o grupo entrando pela prancha. Nenhum navio das Docas tem interior livre: o único interior de navio, a AR0310, é o barco dos piratas, com o capitão, que se entra pela taverna da AR0313. A fase 1 procura então um **porão de navio** entre os candidatos importados; a "porta" seria a prancha de um navio do cenário das Docas, pelo `TRAVEL` (D3).
2. **Fase 2, laboratório:**
   - a área escolhida entra só no override da VM com nome nosso (`IA0001`), nunca no repositório;
   - registro no inventário local de recursos convertidos (CR-2026-032), com aceite por projeto quando não houver licença aberta.
3. **A porta (D3):**
   - porta nossa, pelo gateway, sem mexer nas Docas. O jogo guarda no save uma cópia de cada área visitada, e uma porta escrita no `AR0300.ARE` só apareceria num jogo novo;
   - operação nova `TRAVEL`: com o líder parado no ponto marcado e a quest no passo certo, o módulo leva o grupo para a área nova com a ação do próprio jogo de trocar de área, de modelo fixo;
   - só para áreas nossas (`IA*`) e de volta à área de origem;
   - a área nova tem a saída de volta para o mesmo ponto;
   - a operação terá ADR própria na fase 2.
4. **Fase 3, quest:** a chegada `esconderijo` e o plano de chegada já apontam para `IA0001`.

## Enquanto isso (D2)

- O PR das mecânicas testadas (ADR-0144, CR-2026-033 e ADR-0145) e da quest sai já, com o esconderijo em `IA0001`.
- Até a área existir, a quest para no passo do esconderijo, sem efeito no jogo. O plano de chegada lista a célula para `IA0001`, uma área que nunca carrega.

## Rollback

Voltar a chegada `esconderijo` e as presenças `kalessia` e `agentes` para uma área do jogo.
