# Windows lab — roteiro do gate P0

Ferramentas para coletar evidência no Windows sem escrever na instalação do jogo. Contexto: ADR-0005, ADR-0108, SPEC-001 e, para Windows on ARM em VM, CR-2026-001.

## 1. Preparar a cópia dedicada

1. Instale o BG2:EE da sua conta legítima (Steam, GOG ou Beamdog) **sem mods**.
2. Faça uma cópia dedicada da pasta do jogo para os testes (ADR-0005 item 5); nunca use a instalação ou os saves do dia a dia.
3. Não instale EEex ainda: o P0 é o jogo limpo.

## 2. Coletar o manifesto (somente leitura)

No PowerShell do Windows, na pasta deste arquivo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File p0-collect-manifest.ps1 -GameRoot 'C:\InfinityLab\BG2EE' -OutFile p0-manifest.json
```

Sem `-GameRoot`, o coletor procura instalações Steam/GOG/Beamdog e usa a primeira encontrada. Ele grava só o JSON, com caminhos relativos à raiz do jogo e sem usuário ou nome da máquina.

## 3. Avaliar

```bash
python scripts/p0_assess_manifest.py p0-manifest.json
```

`MANIFEST_OK` é condição necessária, não o P0. Achados `REVIEW` (VM, ARM64, override) devem constar no relatório; `BLOCK` impede seguir.

## 4. Teste base manual (completa o P0)

1. Abra o jogo pela cópia dedicada, inicie um jogo novo, ande até sair da primeira área.
2. Salve num slot com nome `INFINITY-P0-DESCARTAVEL`, feche e recarregue o save.
3. Registre: data, SHA do commit, `build_fingerprint`, `modpack_hash`, ambiente e resultado.

## 5. Onde guardar a evidência

O manifesto bruto fica fora do repositório (contém hashes da sua instalação, nada sensível, mas também nada que precise ser público). No relatório da PR, cite apenas fingerprint, modpack hash, versões, ambiente e resultado. **Nunca** suba saves, `chitin.key`, `.tlk`, `.bif` ou capturas com conteúdo do jogo.
