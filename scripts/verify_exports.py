"""Check source/export consistency, node references, and public artifact hygiene."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable,str(ROOT/'scripts/build_workflows.py'),'--output',tmp],check=True,stdout=subprocess.DEVNULL)
    for path in sorted((ROOT/'workflows').glob('*.json')):
        assert path.read_bytes()==(Path(tmp)/path.name).read_bytes(),f'Generated export differs: {path.name}'
        workflow=json.loads(path.read_text())
        nodes={n['name']:n for n in workflow['nodes']}
        assert len(nodes)==len(workflow['nodes']),'Duplicate node name'
        assert not workflow['pinData'],'Pinned execution data present'
        for name,connections in workflow['connections'].items():
            assert name in nodes,name
            for branch in connections['main']:
                for conn in branch:assert conn['node'] in nodes,conn['node']
        for node in nodes.values():
            for ref in re.findall(r"\$\(['\"]([^'\"]+)['\"]\)",json.dumps(node['parameters']).replace('\\"','"')):
                assert ref in nodes,(node['name'],ref)
        print('PASS',path.name,'source consistency and graph references')
for path in ROOT.rglob('*'):
    if not path.is_file() or any(part in ('.git','.local','__pycache__','node_modules') for part in path.relative_to(ROOT).parts):continue
    if path.name=='.env' or path.suffix.lower() not in ('.md','.json','.py','.js','.cjs','.yaml','.sh','.txt'):continue
    text=path.read_text()
    assert not re.search(r'(?:sk-ant-api\d*-|ghp_)[A-Za-z0-9_-]{15,}',text),'Secret-like token in '+str(path)
print('PASS public text files contain no recognized API-token patterns')
