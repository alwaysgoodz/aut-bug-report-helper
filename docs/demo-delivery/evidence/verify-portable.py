import hashlib
from contextlib import closing
import http.client
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time
from urllib.parse import urlencode, urlsplit

package = Path(sys.argv[1]).resolve()
runtime = package / 'runtime/python.exe'
directory = package / ('smoke data 演示-' + os.urandom(2).hex())
manifest = json.loads((package / 'BUILD-INFO.json').read_text(encoding='utf-8'))
for name, digest in manifest['app_sha256'].items():
    assert hashlib.sha256((package/'app'/name).read_bytes()).hexdigest() == digest, name
environment = dict(os.environ)
environment['PATH'] = str(Path(os.environ['SystemRoot'])/'System32')
environment.pop('PYTHONPATH', None)
environment.pop('PYTHONHOME', None)
command = [str(runtime), '-m', 'tools.demo_launcher', '--data-dir', str(directory)]
creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
checks = []

def execute(arguments):
    return subprocess.run(command+arguments, cwd=package.parent, env=environment, capture_output=True,
                          text=True, encoding='utf-8', errors='replace', timeout=10, creationflags=creationflags)

def start():
    previous = (directory/'workspace.json').read_bytes() if (directory/'workspace.json').exists() else None
    process = subprocess.Popen(command+['--port','0','--no-browser'], cwd=package.parent, env=environment,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
    for _ in range(100):
        if process.poll() is not None:
            raise AssertionError(process.communicate())
        path = directory/'workspace.json'
        if path.exists():
            raw=path.read_bytes()
            if raw != previous:
                info=json.loads(raw)
                if info['pid']==process.pid:
                    return process, info
        time.sleep(.05)
    process.terminate()
    raise AssertionError('No ready file')

def stop(process):
    process.terminate()
    process.communicate(timeout=5)

def request(info, method, path, data=None):
    url=urlsplit(info['url'])
    connection=http.client.HTTPConnection(url.hostname,url.port,timeout=5)
    body=urlencode(data).encode('utf-8') if data is not None else None
    headers={'Content-Type':'application/x-www-form-urlencoded'} if data is not None else {}
    try:
        connection.request(method,path,body,headers)
        response=connection.getresponse()
        return response.status,dict(response.getheaders()),response.read().decode('utf-8')
    finally:
        connection.close()

result=execute(['--check'])
assert result.returncode==0, result.stderr
checks.append({'check':'isolated embedded runtime self-check without installed Python in PATH','result':json.loads(result.stdout)})
process,info=start()
try:
    assert request(info,'GET','/health')[0]==200
    with closing(sqlite3.connect(directory/'demo-reports.db')) as db:
        assert db.execute('SELECT count(*) FROM reports').fetchone()[0]==4
    for asset in ('app.css','app.js','mark.svg'):
        assert request(info,'GET','/static/'+asset)[0]==200
    _,_,form=request(info,'GET','/reports/new')
    token=re.search(r'name="_csrf" value="([^"]+)"',form).group(1)
    status,headers,_=request(info,'POST','/reports',dict(_csrf=token,title='离线 portable proof',severity='high',
        description='Fictional smoke check',steps='1. Open\n2. Select',expected='Expected',actual='Actual',environment='Offline packaged CPython'))
    assert status==303
    detail=headers['Location'].split('?')[0]
    status,_,_=request(info,'POST',detail+'/status',dict(_csrf=token,expected_status='Open',status='In progress'))
    assert status==303
    status,headers,body=request(info,'GET',detail+'/export')
    assert status==200 and 'attachment;' in headers['Content-Disposition']
    assert '离线 portable proof' in body and 'Status: In progress' in body and '100%' in body
    duplicate=execute(['--no-browser'])
    assert duplicate.returncode==0 and info['url'] in duplicate.stdout
    reset=execute(['--reset-demo','--yes'])
    assert reset.returncode==2
    assert not (directory/'backups').exists()
    checks.append({'check':'first seed, all assets, real HTTP create/status/UTF-8 export, duplicate startup and refused live reset','pass':True})
finally:
    stop(process)
process,info=start()
try:
    assert request(info,'GET',detail)[0]==200
    assert 'Status: In progress' in request(info,'GET',detail+'/export')[2]
    checks.append({'check':'restart preserves report and saved status','pass':True})
finally:
    stop(process)
reset=execute(['--reset-demo','--yes'])
assert reset.returncode==0,reset.stderr
backups=list((directory/'backups').glob('*.db'))
assert len(backups)==1
with closing(sqlite3.connect(backups[0])) as db:
    assert db.execute('SELECT count(*) FROM reports').fetchone()[0]==5
    assert db.execute('SELECT status FROM reports WHERE title=?',('离线 portable proof',)).fetchone()[0]=='In progress'
with closing(sqlite3.connect(directory/'demo-reports.db')) as db:
    assert db.execute('SELECT count(*) FROM reports').fetchone()[0]==4
checks.append({'check':'offline reset creates a readable five-report backup before restoring four fictional examples','pass':True})
output=dict(package=str(package),source_commit=manifest['source_commit'],runtime_version=manifest['runtime_version'],
            reduced_path=environment['PATH'],checks=checks,
            limits='Local Windows 11 x64. External requests blocked separately in browser rehearsal; not a physical second PC test.')
Path('tmp/demo-portable-smoke.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(output,ensure_ascii=True,indent=2))
