# Tarefas — SPEC-009

- [x] Aprovar a taxonomia de sigilo do ADR-0131 (mantenedor, 2026-11-15).
- [x] Acrescentar o campo opcional de classe ao schema do cânone (`secrecy`, compatível: sem classe, o comportamento de antes). `tests/test_disclosure.py`.
- [x] Decisão por item antes do prompt, com `reason_code` auditável e política neutra (`dialogue/disclosure.py`; retidos no log do serviço como `retidos=[<entrada>:<motivo>]`, fora do JSON da resposta).
- [x] Montar o contexto do modelo só com os itens liberados; o validador confere contra o pacote (o contexto já é o pacote: o validador só conhece os itens liberados).
- [ ] Modelos determinísticos de fala para `NOT_KNOWN`, `NOT_DEFINED` e `WITHHELD`.
- [x] Testes de compatibilidade dos ADR-0125/0126 para itens sem classe (todas as combinações de escopo, disposição e moral); casos novos de reação, moral e confiança.
- [ ] Casos novos na bateria de diálogo: recusa sem vazamento e injeção.
- [ ] Confiança qualitativa e direcional por evento (fase 4b).
- [ ] Teste no laboratório (`lab-s1f`) e evidência.
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
