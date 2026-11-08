# CR-2026-001 — Laboratório Windows 11 ARM64 em VMware Fusion para os gates P0/P1

**Status:** PROPOSED  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-08

## Motivo e contexto

O ADR-0005 aprovou **Windows nativo** como primeiro ambiente de execução e testes. A máquina disponível ao mantenedor é um Mac com Apple Silicon (M1 Max) que roda **Windows 11 ARM64 em VMware Fusion**. Nesse ambiente o BG2:EE (binário x86/x64) roda sob a emulação x86/x64 do Windows on ARM, dentro de uma VM. Isso não é o "Windows nativo" do ADR-0005 nem as alternativas B (macOS/CrossOver) e C (Linux/Proton/Wine) consideradas nele.

## DEC/ADR/SPEC/REQ afetados

- ADR-0005 (DEC-002): **não é alterado**. Este CR adiciona um ambiente de laboratório, sem substituir o ambiente-alvo.
- ADR-0108 (gates P0–P4): a evidência coletada no laboratório é registrada como **"Windows 11 ARM64 / VMware Fusion / emulação x86-x64"** e vale apenas para esse ambiente.
- SPEC-001: `assess_manifest` sinaliza `HOST_ARM64` e `VIRTUAL_MACHINE` como `REVIEW` em todo manifesto coletado nesse ambiente.

## Diff proposto e impacto no comportamento

1. Permitir P0 (jogo limpo, manifesto, save descartável) e P1 (loader EEex) no laboratório ARM64.
2. Todo relatório de evidência deve registrar arquitetura do processador, hipervisor e o `pe_machine` do executável.
3. Resultado **positivo** no laboratório = evidência para esse ambiente; não declara suporte em Windows nativo x86-64.
4. Resultado **negativo** no laboratório (por exemplo, o loader do EEex falhar sob emulação) **não reprova** o ADR-0005: registra-se como `BLOCKED_CAPABILITY` do ambiente e o gate fica pendente até repetição em Windows x86-64 nativo.
5. P4 (host + dois clientes) exige decidir a topologia: dois clientes no mesmo laboratório não comprovam rede real. Fica fora deste CR.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Compatibilidade:** a injeção do EEex num processo emulado é incerta; é exatamente o que o P1 mede.
- **Desempenho:** emulação e VM podem causar timeouts ou falhas de temporização que não ocorreriam em hardware nativo; registrar antes de concluir.
- **Privacidade:** o coletor não grava usuário, nome da máquina nem caminhos absolutos; saves e arquivos do jogo não saem da VM.
- **Acesso remoto:** se for usado SSH do Mac para a VM, somente por chave, porta liberada só para o IP do host na rede NAT do VMware, sem exposição à LAN ou à internet.
- **Licenças:** cópia legítima do jogo do mantenedor; nada do jogo entra no repositório.

## Migração e rollback

Sem migração. Para reverter: rejeitar este CR e repetir P0/P1 em Windows x86-64 nativo; as evidências do laboratório continuam válidas apenas como registro histórico do ambiente ARM64.

## Testes de regressão e evidência

- `tests/test_bridge_spec001.py::ManifestTests::test_arm64_vm_host_is_flagged_for_review`.
- Evidência real: manifesto P0 coletado com `tools/windows-lab/p0-collect-manifest.ps1` e avaliado com `scripts/p0_assess_manifest.py`, registrado conforme `docs/architecture/testing.md`.

## Aprovação do mantenedor / ADR substituto quando necessário

Pendente. Se o laboratório ARM64 virar ambiente oficial (e não só laboratório), abrir novo ADR que complemente o ADR-0005.
