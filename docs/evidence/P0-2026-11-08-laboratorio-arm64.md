# Evidência P0 — BG2:EE limpo no laboratório Windows 11 ARM64 (2026-11-08)

**Gate:** P0 (ADR-0108, `docs/architecture/testing.md`). **Resultado:** APROVADO **no laboratório ARM64/VM** do CR-2026-001 (ainda PROPOSED). **Não** vale como P0 em Windows x86-64 nativo (ADR-0005).
**Commit das ferramentas:** `565c2ae` (coletor `0.1.0`). **Executado por:** mantenedor (passos de jogo) e Claude Code via SSH (coleta e verificações).

## Ambiente

| Item | Valor |
|---|---|
| Host | Mac Apple Silicon (M1 Max), VMware Fusion |
| Convidado | Windows 11 Pro 10.0.26100 (build 26100), ARM64, 2 vCPU, 8 GB |
| Jogo | BG2:EE Steam, `Baldur.exe` 2.7.3.0, PE x64, rodando sob emulação x64 do Windows on ARM |
| Dependência de sistema | OpenAL 6.14.0357.24 (`oalinst.exe` do próprio jogo, assinatura Creative Labs válida), instalado em `System32`/`SysWOW64` |
| Mods / EEex | nenhum |

## Identidade da build

- `build_fingerprint`: `sha256:a9b1e706f8e74f2f14337cdf10e2222b42637f806a91506337904d9b555c8279`
- `modpack_hash`: `sha256:da3f9c8c2355e8708c9ee8c76e290df20cd5ca0de77c1b600fcfc34fe5af4c8c` (sem mods)
- `Baldur.exe` sha256: `b51093a49140b2b8a7c046b4652bb8e535be24ebbc12b1d735e0b94217a14d57`
- Avaliação: `MANIFEST_OK`, com `HOST_ARM64` e `VIRTUAL_MACHINE` como REVIEW.

## Passos e resultados

| # | Passo | Comando / ação | Resultado | Como foi verificado |
|---|---|---|---|---|
| 1 | Manifesto da instalação Steam, nunca executada | `p0-collect-manifest.ps1` + `scripts/p0_assess_manifest.py` | `MANIFEST_OK` | ferramenta |
| 2 | Cópia dedicada | robocopy para `C:\InfinityLab\BG2EE-P0` (3,62 GB) | mesmo fingerprint e modpack hash da origem | ferramenta |
| 3 | Primeira execução pela cópia | duplo clique no `Baldur.exe` da cópia | falhou: `OpenAL32.dll não foi encontrado` | relato + captura do erro |
| 4 | Instalar OpenAL do próprio jogo | `oalinst.exe /s` (exit 0) | `OpenAL32.dll` presente | ferramenta |
| 5 | Execução pela cópia | idem | uma instância, origem `C:\InfinityLab\BG2EE-P0`, respondendo; nenhuma instância da pasta Steam | ferramenta (processo) |
| 6 | Jogo novo e troca de área | personagem novo, sair da primeira área | save automático gravado às 16:19:21 | ferramenta (pasta de saves) + relato |
| 7 | Recarregar a frio | fechar e reabrir pela cópia, carregar | novo processo às 16:19:31 (da cópia); carregamento ok | ferramenta (horário do processo) + relato |
| 8 | Save descartável nomeado | slot `INFINITY-P0-DESCARTAVEL` | gravado às 16:23:00 | ferramenta (pasta de saves) |
| 9 | Recarregar o save nomeado | carregar o slot | ok, **na mesma sessão** (o processo é anterior ao save; não houve reinício depois do passo 8) | relato |
| 10 | Integridade da cópia após jogar | hash de todos os arquivos da cópia vs. instalação Steam | 2.324 arquivos; 0 novos, 0 removidos, 0 alterados | ferramenta |

## Conclusão

O jogo base roda pela cópia dedicada no laboratório, grava e recarrega saves, e não escreve na pasta da instalação. A dependência OpenAL precisa ser instalada quando a cópia é executada antes de o jogo ser aberto pelo Steam (documentado em `tools/windows-lab/README.md`).

## Riscos e pendências registrados

- **Saves fora da cópia:** o jogo grava em `Documentos\Baldur's Gate II - Enhanced Edition\save`, pasta compartilhada pela cópia e pela instalação Steam. Hoje a VM não tem saves reais; antes de qualquer save real nessa VM, definir isolamento (outra conta de usuário ou VM só de laboratório). Relevante para P1/P3.
- **Steam Cloud:** existe a pasta `cloudsave` (vazia na verificação). O mantenedor foi orientado a desativar a sincronização para o jogo; não verificado por ferramenta.
- **Emulação:** desempenho e temporização sob emulação x64 não foram medidos; o P1 (loader do EEex, que exige motor 2.7 → EEex ≥ v1.1.0) é o próximo teste de compatibilidade real.
- **P0 nativo:** repetir em Windows x86-64 nativo quando houver máquina disponível.

## O que não foi publicado

Manifestos brutos ficam fora do repositório (só hashes e versões acima). Nenhum save, arquivo do jogo, captura de tela do jogo, nome de usuário ou caminho pessoal foi publicado.
