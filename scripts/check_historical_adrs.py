"""Reject modifications to already merged ADRs in a PR; additions allowed."""
import os, subprocess, sys
base=os.getenv('GITHUB_BASE_REF','main')
cmd=['git','diff','--name-status',f'origin/{base}...HEAD','--','docs/decisions/']
r=subprocess.run(cmd,capture_output=True,text=True)
if r.returncode:
    print(r.stderr,file=sys.stderr);sys.exit(2)
errors=[]
for line in r.stdout.splitlines():
    cols=line.split('\t'); status=cols[0] if cols else ''
    if any(p.endswith('.md') and '/ADR-' in p for p in cols[1:]) and status[0] != 'A':
        errors.append(line)
if errors:
    print('Approved ADRs are append-only; create a new ADR instead:',*errors,sep='\n',file=sys.stderr);sys.exit(1)
print('No historical ADR modified or deleted.')
