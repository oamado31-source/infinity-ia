# ADR-0034 — Diretor híbrido de histórias pessoais e marcos narrativos

- **Decisão:** DEC-039 (arcos pessoais dos personagens do Living World).
- **Estado:** APROVADA — opção C.
- **Data da decisão:** 2026-11-06.
- **Escopo:** geração, oferta, acompanhamento e desfecho de missões pessoais vinculadas ao histórico e às ações dos personagens.
- **Dependências:** DEC-004/008/009/010/011/012/014/019/020/021/022/023/025/027/028/029/030/034/035/036/037/038, DEC-005-E e DEC-005-R.

## Contexto

As decisões anteriores aprovaram históricos pessoais versionados, um Living World compartilhado, missões procedurais validadas, reputação e alinhamento dinâmicos, arcos clássicos paralelos e jornadas de redenção. Falta uma entidade responsável por transformar esses sinais em **histórias individuais contínuas**, evitando missões desconexas, falta de conclusão, mudanças indevidas do cânone e monopolização do tempo do grupo.

## Decisão

Adotar a **opção C — Personal Story Director com geração híbrida**:

1. **Planejamento estruturado:** um diretor lógico por campanha coordena propostas de arcos vinculadas a personagens, vínculos, conflitos, motivações, escolhas e fatos confirmados. Mantém objetivos e marcos verificáveis, sem roteiros rígidos que eliminem a agência do jogador.
2. **Conteúdo híbrido:** combinar estruturas/arquetipos narrativos previamente validados e recursos do jogo com geração local sob demanda (diálogos, pistas, personagens candidatos, variações e ligações causais). O LLM não produz diretamente efeitos mecânicos nem declara vitórias ou eventos históricos.
3. **Estado persistente e versionado:** registrar identificador de campanha/personagem, origem/proveniência do gancho, estágio, marcos, dependências, janela temporal, histórico das escolhas, desfechos e versões de regras/conteúdo. Propostas, ofertas e missões confirmadas permanecem distintas.
4. **Agência do jogador:** aceitar, adiar, rejeitar ou tomar rumos alternativos. A recusa não provoca punição artificial; o mundo pode continuar mudando por causas já autorizadas e confirmadas. Um arco pessoal não fica predestinado a um único desfecho.
5. **Compatibilidade temporal e de cânone:** qualquer NPC, cidade, ordem, entidade, evento ou missão é validado quanto ao ano e à região; divergências só entram na campanha sob DEC-009/034, com impacto e autorização apropriados.
6. **Sigilo e acesso:** um gancho derivado de histórico secreto não se torna automaticamente diálogo público, quest grupal ou dado acessível a outros participantes. A recuperação da memória deve filtrar por personagem, propósito e proveniência **antes** do LLM (DEC-019/028).
7. **Participação cooperativa:** um arco tem personagem protagonista, mas pode oferecer funções e objetivos a outros jogadores **sem expor segredos ou exigir participação**. A política detalhada de equilíbrio, preferência do grupo e prioridade entre arcos é pendência da **DEC-040**.
8. **Progressão e conclusão por evidências:** critérios objetivos são avaliados por regras; ações físicas e recompensas exigem operação autorizada pelo gateway e confirmação do host (DEC-011/012/027). Evento com resultado `UNCERTAIN` fica pendente de reconciliação, sem completar a etapa ou duplicar recompensa.
9. **Desempenho:** diretor avalia oportunidades em checkpoints/eventos relevantes, não a cada tick e não com LLM sempre ativo. Respeita níveis de atividade e relógio híbrido (DEC-021/022).
10. **Isolamento:** histórico e estado do modo Original permanecem inalterados; arcos são escopados por campanha e personagem, mantendo rastreabilidade de compartilhamento grupal.

## Fluxo lógico candidato

```text
CONFIRMED_EVENTS + VERSIONED_BACKSTORY + WORLD/CANON + ALLOWED_KNOWLEDGE
    -> candidate hook (rules / lightweight scoring)
    -> story outline (validated templates + optional local LLM proposal)
    -> CHECK (timeline, lore, permissions, risks, available assets, agency)
    -> OFFERED -> ACCEPTED | DEFERRED | DECLINED
    -> MILESTONES (requirements; evidence; alternative paths)
    -> outcome proposal -> gateway / host receipts for mechanical consequences
    -> CONFIRMED outcome + event log + reputation/alignment/world updates
```

**O fluxo é conceitual**, não uma API aprovada ou uma feature disponível no BG2:EE.

## Critérios de aceitação candidatos

1. A partir de um histórico com pista e familiar desaparecido, gerar proposta coerente com época, recursos existentes e estado da campanha; não assumir desfecho antecipado.
2. Gerar missões pessoais distintas de uma mesma origem sem repetir ganchos/recompensas quando o estado não mudou.
3. O personagem pode adiar/recusar, e o sistema registra sem bloquear histórias do restante do grupo.
4. Personagens que não conhecem um segredo não recebem pista, prompt, log ou diálogo que o revele.
5. Uma prova falsa/boato não vira fato nem conclui etapa sem condição definida.
6. Alterar um histórico versionado não reescreve marcos e fatos já confirmados em jogo sem autorização.
7. Duas quests que dependem do mesmo NPC/recurso histórico são analisadas quanto a incompatibilidade e causalidade.
8. Cada etapa conserva proveniência e o resultado mecânico só é considerado após `host_receipt` confirmado; falha e `UNCERTAIN` não duplicam recompensas.
9. A progressão offline respeita o teto configurado de catch-up e não aplica resultados históricos HIGH sem autorização.
10. O save reaberto e clientes multiplayer recuperam o mesmo estado sem vazamento de conteúdo individual.
11. O jogo Original permanece sem flags ou scripts novos.
12. Um LLM indisponível não impede operações determinísticas validadas, nem força mudança de arcos já persistidos.

## Exclusões e pendências

- Não fixa algoritmo de seleção/prioridade, orçamento de tempo por jogador, número máximo de arcos simultâneos nem justiça de distribuição: **DEC-040**.
- Não aprova geração de mapas em tempo real; novos recursos físicos dependem da DEC-010, de SPECS e POCs do BG2:EE.
- Não define sistema de diálogos, interface ou apresentação dos ganchos (DEC-007/016 ainda abertas).
- Não autoriza criar arbitrariamente poderes, classes, itens, gold, XP, mortes, mudanças de cânone ou estados mecânicos sem o host.
- Não decide modelos LLM, dispositivos, custo ou política de API remota (DEC-006).
- Estruturas, templates e regras de avaliação ainda precisarão de SPECS, testes e ajuste narrativo.

## Consequências

**Benefícios:** histórias contínuas derivadas do histórico real dos personagens; maior agência; reaproveitamento de conteúdo; consistência, sigilo e auditabilidade.

**Custos:** gerenciar concorrência de arcos, disponibilidade de NPCs, ambiguidade em histórias abertas, validação de lore e regras, pacing do grupo, dependência de integração com save/host e moderar repetição.

**Situação técnica:** aprovação de arquitetura em Discovery; nenhuma integração com BG2:EE/EEex/multiplayer foi implementada ou validada por esta decisão.

**Próxima discussão:** DEC-040 — equilíbrio e participação do grupo em histórias pessoais simultâneas.
