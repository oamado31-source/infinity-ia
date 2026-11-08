"""Basic public repository hygiene (not a substitute for manual review)."""
from pathlib import Path
import sys
banned={'.sav','.dmp','.key','.bif','.biff','.tlk','.cre','.are','.wed','.mos','.bam','.sqlite','.sqlite3','.db','.pem','.p12'}
problems=[]
for p in Path('.').rglob('*'):
    if not p.is_file() or '.git' in p.parts: continue
    if p.suffix.lower() in banned: problems.append(str(p))
    if p.name.lower() in {'weidu.log','.env'}: problems.append(str(p))
if problems:
    print('Protected/prohibited files:',*problems,sep='\n',file=sys.stderr);sys.exit(1)
print('No basic prohibited file types found.')
