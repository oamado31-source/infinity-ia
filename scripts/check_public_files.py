"""Basic public repository hygiene (not a substitute for manual review).

Checks the files git tracks or would add (untracked, not ignored), so local virtualenvs and other
ignored folders do not cause false alarms. Falls back to walking the tree outside a git checkout.
"""
from pathlib import Path
import subprocess
import sys
banned={'.sav','.dmp','.key','.bif','.biff','.tlk','.cre','.are','.wed','.mos','.bam','.sqlite','.sqlite3','.db','.pem','.p12'}


def candidate_files():
    r=subprocess.run(['git','ls-files','-z','--cached','--others','--exclude-standard'],
                     capture_output=True)
    if r.returncode==0:
        return [Path(p) for p in r.stdout.decode('utf-8').split('\0') if p]
    return [p for p in Path('.').rglob('*') if p.is_file() and '.git' not in p.parts]


problems=[]
for p in candidate_files():
    if p.suffix.lower() in banned: problems.append(str(p))
    if p.name.lower() in {'weidu.log','.env'}: problems.append(str(p))
if problems:
    print('Protected/prohibited files:',*problems,sep='\n',file=sys.stderr);sys.exit(1)
print('No basic prohibited file types found.')
