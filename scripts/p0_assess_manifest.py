# SPDX-License-Identifier: Apache-2.0
"""Validate a P0 manifest from tools/windows-lab and print fingerprint, modpack hash and findings.

Usage: python scripts/p0_assess_manifest.py p0-manifest.json
Exit code 0 = MANIFEST_OK, 1 = MANIFEST_BLOCKED, 2 = schema/IO error.
A clean manifest is necessary but not sufficient for P0 (base run + throwaway save are manual).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.bridge.manifest import assess_manifest  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        manifest = json.loads(Path(argv[1]).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        print(f'cannot read manifest: {exc}', file=sys.stderr)
        return 2
    try:
        import jsonschema
    except ImportError:
        print('warning: jsonschema not installed, schema not checked', file=sys.stderr)
    else:
        schema_path = ROOT / 'src/infinity_ai/bridge/schemas/build_manifest_v1.schema.json'
        errors = list(jsonschema.Draft202012Validator(
            json.loads(schema_path.read_text())).iter_errors(manifest))
        for err in errors:
            print(f'schema: {"/".join(map(str, err.path)) or "<root>"}: {err.message}',
                  file=sys.stderr)
        if errors:
            return 2
    result = assess_manifest(manifest)
    print(json.dumps({
        'status': result.status,
        'build_fingerprint': result.build_fingerprint,
        'modpack_hash': result.modpack_hash,
        'findings': [{'code': f.code, 'severity': f.severity.value, 'detail': f.detail}
                     for f in result.findings],
    }, indent=2))
    return 0 if result.status == 'MANIFEST_OK' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
