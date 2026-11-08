# Consequências mecânicas progressivas do alinhamento — desenho preliminar

- **Discovery:** v3.3; **DEC-037 opção B aprovada**, ADR-0032.
- **Tipo:** proposta de arquitetura e cenários para futuras SPECS. **Nenhuma integração com BG2:EE/EEex foi executada.**
- **Referências:** ADR-0030/0031 (alinhamento e avaliação), ADR-0018 (núcleo AD&D 2e), ADR-0007 (host), ADR-0022 (gateway), ADR-0025 (reputação), `35-*` e `36-*`.

## Pipeline de decisão e aplicação

```text
Evento confirmado + autoria individual
  -> Avaliação contextual/gradual DEC-036
  -> Transição de alinhamento consolidada? Não: só tendência narrativa
  -> Sim: verificar versão da regra e perfil da campanha
  -> Mapear efeitos *potenciais* por classe/kit/itens/magias/equips/efeitos/scripts
  -> Preflight: compatibilidade real BG2:EE + mods + EEex + estado de save/multiplayer
      -> ausência de POC/avaliação controversa: NARRATIVE_ONLY / PENDING_VALIDATION
      -> validado: informar impacto, avaliar permissão, preparar comando tipado
  -> Action Gateway + host autoritativo
      -> receipt CONFIRMED: registrar resultado e projeção mecânica
      -> FAILED / UNCERTAIN: reconciliação, sem retry cego
  -> Persistência idempotente e projeções específicas por observador
```

## Estados conceituais candidatos

| Estado | Interpretação | Efeito permitido |
|---|---|---|
| `TREND_ONLY` | Tendência nos dois eixos; sem transição consolidada | Narrativa privada, sem escrita mecânica |
| `TRANSITION_CONFIRMED` | Regra de avaliação confirmou o novo alinhamento projetado | Preflight, informação ao jogador, testes de dependência |
| `PENDING_TECH_VALIDATION` | Consequência não é suportada/validada no motor atual | Nenhum efeito físico; pendência audível |
| `READY_FOR_GATEWAY` | Regra/instalação/permissão verificadas | Apenas proposta tipada; não é confirmação de aplicação |
| `HOST_CONFIRMED` | O host comprovou o resultado da operação | Registrar consequência e vínculo ao save |
| `UNCERTAIN_RECONCILE` | Recebimento/execução incertos ou estado divergente | Bloquear repetição automática; verificar host/save |

Os nomes/estados são **candidatos**, sem API implementada. Não existe garantia de que qualquer mudança em BG2:EE esteja exposta via EEex.

## Perfil de regras e escolhas de campanha

- O anfitrião define, **antes da campanha**, quais módulos mecânicos de alinhamento estão suportados e a política de transparência. Não se aprova ignorar restrições canônicas por padrão.
- A configuração é identificada e versionada no save/campanha; diferenças entre clientes produzem bloqueio/reconciliação, nunca resultados físicos diferentes.
- O jogador deve ter acesso a uma explicação geral das consequências e de quais mudanças afetam sua classe, sem exigir que o sistema revele segredos da história nem de outros personagens.
- Mudanças de regra em campanha já iniciada exigem migração, backup e consentimento específicos; escopo exato ainda será especificado.

## Matriz de efeitos a inventariar nos testes

| Área | O que inspecionar | Risco |
|---|---|---|
| Alinhamento nativo | Leitura/alteração/releitura do campo de alinhamento e seus disparadores | Divergência narrativa/engine |
| Paladinos/rangers/kits | Condições permitidas, eventual status de queda e gatilhos reais de habilidades | Perda inconsistente de poderes |
| Clérigos/druidas | Restrições de alinhamento e consequências **reais por instalação/mod** | Política inventada ou incompatível |
| Itens e equipamentos | Restrições, checks de uso, script, efeitos e inventário | Exploit, perda de item ou bloqueio inesperado |
| Magias e efeitos persistentes | Permissões, memorização, duração, dispels, scripts e resiliência a save/load | Estado corrompido ou efeito duplicado |
| Reputação e relacionamento | Camadas independentes com proveniência e ACL | Rumor mudando caráter automaticamente |
| Multiplayer/host | Perfis de regra iguais, receipt, retry e checkpoints | Clientes divergentes |

A matriz **não afirma** que todas essas classes têm implementação idêntica ou que todos os estados são modificáveis. Parte da investigação usará o manual de BG2:EE e a instalação/modlist exata; nunca aplicar regras de mesa como equivalência automática ao engine.

## Casos de teste prioritários

1. Personagem com tendência crescente mas sem transição não sofre alteração mecânica.
2. Paladino deixa Lawful Good no estado narrativo: avaliar restrições; nenhum *fallen* artificial sem POC.
3. Mudança no campo de alinhamento com efeitos conhecidos: confirmar comportamento antes/depois, salvar, reabrir e repetir.
4. Item com alinhamento restrito: verificar comportamento real, sem equipar/destruir clandestinamente.
5. Magia ou poder temporário ativo durante transição: nenhum efeito incerto assumido como confirmado.
6. Causa moral contestada: review antes de efeito; nenhuma punição via LLM.
7. Host confirma mas cliente desconecta: reconciliar idempotente, sem aplicar duas vezes.
8. Migração entre modlists incompatíveis: bloquear e relatar, backup seguro.
9. Jogador age sozinho: nenhuma punição em outro personagem ou modo Original.
10. Redenção e recuperação de habilidades: apenas após DEC-038 e SPECS; sem restauro automático.
11. Avaliação de segredo: textos e logs filtrados para jogadores/NPCs não autorizados.
12. Captura de combate que altera o campo incorretamente: nunca inferir estado correto de narrativa sem evidência.

## Dívidas técnicas e decisões abertas

- Formulação das regras quantitativas, transições e frequência de avisos (SPECS de DEC-036).
- Verificação real de hooks e alterações seguras no BG2:EE/EEex, por classe e por modpack.
- Esquema formal de migrações de save, consentimento e rollback.
- DEC-038: redenção, reconsagração/renovação de juramentos, recuperação de poderes e eventual reorientação de classe — **em aberto**.
- Teste de 2 clientes, modo Original isolado, falha da bridge e reconciliação após reiniciar.

**Status:** documentação de Discovery, sem efeito no executável ou nos saves do usuário.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Consequências de alinhamento dependem do host, não de observação semântica de quests.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
