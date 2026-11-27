#!/usr/bin/env python3
"""Inspect live Docker isolation. Exit 2 reports demonstrated indirect paths.

Diagnostic containers are ephemeral and share only the source's network namespace.
No Docker socket or host mounts are passed to them. Requires a running stack.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess
import time
import uuid

HELPERS = runpy.run_path(str(Path(__file__).with_name('verify-compose.py')))
compose, validate, EXPECTED = (HELPERS[k] for k in ('compose', 'validate', 'EXPECTED'))
DIAGNOSTIC = os.environ.get('DIAGNOSTIC_IMAGE', 'python:3.13.9-alpine3.22')
PROBE = r'''
import errno, http.client, json, socket, sys
p = json.loads(sys.argv[1])
if p['op'] == 'deny':
    results = []
    for ip in p['ips']:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((ip, p.get('port', 8080)))
        except OSError as e:
            # This is a failed TCP handshake, not an HTTP/application timeout.
            results.append({'ip': ip, 'error': type(e).__name__, 'errno': e.errno})
        else:
            raise AssertionError('Forbidden TCP connection succeeded: ' + ip)
        finally:
            s.close()
    try:
        dns = sorted({x[4][0] for x in socket.getaddrinfo(p['host'], p.get('port', 8080), socket.AF_INET)})
    except socket.gaierror as e:
        dns = str(e)
    print(json.dumps({'dns': dns, 'tcp_denied': results}))
elif p['op'] == 'tcp':
    dns = sorted({x[4][0] for x in socket.getaddrinfo(p['host'], p['port'], socket.AF_INET)})
    with socket.create_connection((p['host'], p['port']), timeout=5):
        pass
    print(json.dumps({'dns': dns, 'tcp_connected': True}))
else:
    dns = sorted({x[4][0] for x in socket.getaddrinfo(p['host'], p['port'], socket.AF_INET)})
    conn = http.client.HTTPConnection(p['host'], p['port'], timeout=8)
    body = json.dumps(p['body']) if 'body' in p else None
    conn.request(p.get('method', 'GET'), p['path'], body, {'Content-Type': 'application/json'})
    r = conn.getresponse()
    data = r.read().decode()
    conn.close()
    print(json.dumps({'dns': dns, 'status': r.status, 'body': data}))
'''


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True)


def inspect(kind, names):
    return json.loads(docker(kind, 'inspect', *names)) if kind else json.loads(docker('inspect', *names))


def diag(source, payload):
    result = docker('run', '--rm', '--network', 'container:' + containers[source]['Id'],
                    '--user', '65534:65534', '--cap-drop=ALL', '--security-opt=no-new-privileges:true',
                    '--read-only', '--pids-limit=32', '--memory=64m', '--cpus=0.5',
                    '--entrypoint=python', DIAGNOSTIC, '-c', PROBE, json.dumps(payload))
    return json.loads(result)


def http(source, target, path='/actuator/health', method='GET', body=None):
    payload = dict(op='http', host=target, port=8500 if target == 'consul' else 8080,
                   path=path, method=method)
    if body is not None:
        payload['body'] = body
    return diag(source, payload)


def consul_json(path):
    return json.loads(compose('exec', '-T', 'consul', 'curl', '-fsS', 'http://127.0.0.1:8500' + path))


def shell(service, code):
    return compose('exec', '-T', service, 'sh', '-ec', code).strip()


if __name__ == '__main__':
    config = validate()
    docker('info')  # Stop immediately on missing daemon access; never report a skip as PASS.
    ids = compose('ps', '-q').split()
    containers = {c['Config']['Labels']['com.docker.compose.service']: c for c in inspect('', ids)}
    assert set(containers) == set(config['services']), 'All seven containers must be running'
    expected_names = {n['name'] for n in config['networks'].values()}
    project_networks = set(docker('network', 'ls', '--filter', 'label=com.docker.compose.project=' + config['name'],
                                  '--format', '{{.Name}}').split())
    assert project_networks == expected_names, (project_networks, expected_names)
    networks = {n['Name']: n for n in inspect('network', sorted(expected_names))}
    for logical, members in EXPECTED.items():
        actual = networks[config['networks'][logical]['name']]
        assert actual['Driver'] == 'bridge' and actual['Internal'] == (logical != 'public'), logical
        assert not actual.get('EnableIPv6'), logical
        assert set(actual.get('Containers', {})) == {containers[s]['Id'] for s in members}, logical
    for name, c in containers.items():
        expected = {config['networks'][n]['name'] for n in config['services'][name]['networks']}
        assert set(c['NetworkSettings']['Networks']) == expected, name
        assert c['State']['Health']['Status'] == 'healthy', (name, c['State'])
        h = c['HostConfig']
        assert h['ReadonlyRootfs'] and not h['Privileged'] and h['CapDrop'] == ['ALL'], name
        assert not h.get('CapAdd') and not h.get('Devices'), name
        assert 'no-new-privileges:true' in h['SecurityOpt'], name
        assert h['Memory'] > 0 and h['NanoCpus'] > 0 and h['PidsLimit'] > 0, name
        assert c['Config']['User'] == config['services'][name]['user'], name
        bindings = h.get('PortBindings') or {}
        if name == 'api-gateway':
            assert bindings == {'8080/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '8080'}]}, bindings
        else:
            assert not bindings, (name, bindings)
        for mount in c['Mounts']:
            assert mount['Type'] == 'tmpfs' or (
                name == 'consul' and mount['Destination'] == '/consul/config/bettermusic.json' and not mount['RW']
            ) or (
                name == 'postgres' and mount['Type'] == 'volume'
                and mount['Name'] == config['volumes']['postgres-data']['name']
                and mount['Destination'] == '/var/lib/postgresql' and mount['RW']
            ) or (
                name == 'postgres' and mount['Type'] == 'bind'
                and mount['Destination'] == '/docker-entrypoint-initdb.d/init-databases.sh' and not mount['RW']
            ), (name, mount)
        status = shell(name, 'cat /proc/1/status')
        fields = dict(line.split(':', 1) for line in status.splitlines() if ':' in line)
        assert set(fields['Uid'].split()) == {c['Config']['User'].split(':')[0]}, name
        for field in ('CapEff', 'CapPrm', 'CapBnd', 'CapAmb'):
            assert int(fields[field].strip(), 16) == 0, (name, field)
        assert fields['NoNewPrivs'].strip() == '1', name
        assert shell(name, 'cat /proc/sys/net/ipv4/ip_forward') == '0', name
        shell(name, 'if touch /bettermusic-readonly-probe 2>/dev/null; then rm /bettermusic-readonly-probe; exit 1; fi; '
                    'touch /tmp/bettermusic-write-probe; rm /tmp/bettermusic-write-probe')
        print('PASS: actual networks, UID, caps, mounts, read-only root, forwarding=0, limits, ports:', name, flush=True)

    # Pull before starting probes: no image pulls or tooling inside application containers.
    if subprocess.run(
        ['docker', 'image', 'inspect', DIAGNOSTIC], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode != 0:
        docker('pull', DIAGNOSTIC)
    allowed = [('api-gateway', s) for s in ('album', 'recensioni', 'connessioni', 'recensioni-seguite')]
    allowed += [('recensioni', 'album')]
    allowed += [('recensioni-seguite', s) for s in ('album', 'recensioni', 'connessioni')]
    applications = set(containers) - {'consul', 'postgres'}
    allowed += [(s, 'consul') for s in applications]
    allowed += [('consul', s) for s in applications]
    for source, target in allowed:
        result = http(source, target, '/v1/status/leader' if target == 'consul' else '/actuator/health')
        assert result['status'] == 200, (source, target, result)
        source_nets = containers[source]['NetworkSettings']['Networks']
        target_nets = containers[target]['NetworkSettings']['Networks']
        shared_ips = {target_nets[n]['IPAddress'] for n in set(source_nets) & set(target_nets)}
        assert result['dns'] and set(result['dns']) <= shared_ips, (source, target, result, shared_ips)
        if target != 'consul':
            assert json.loads(result['body'])['status'] == 'UP', result
        print('PASS: DNS + HTTP', source, '->', target, result['dns'], flush=True)

    for source in sorted(applications - {'api-gateway'}):
        result = diag(source, dict(op='tcp', host='postgres', port=5432))
        source_nets = containers[source]['NetworkSettings']['Networks']
        target_nets = containers['postgres']['NetworkSettings']['Networks']
        shared_ips = {target_nets[n]['IPAddress'] for n in set(source_nets) & set(target_nets)}
        assert result['tcp_connected'] and result['dns'] and set(result['dns']) <= shared_ips, result
        print('PASS: DNS + TCP', source, '-> postgres:5432', result['dns'], flush=True)
    for source in ('api-gateway', 'consul'):
        ips = [v['IPAddress'] for v in containers['postgres']['NetworkSettings']['Networks'].values()]
        result = diag(source, dict(op='deny', host='postgres', port=5432, ips=ips))
        assert len(result['tcp_denied']) == len(ips)
        print('PASS: forbidden PostgreSQL TCP handshakes denied', source, result, flush=True)

    deadline = time.monotonic() + 120
    while True:
        passing = True
        for service in applications:
            app = 'apigateway' if service == 'api-gateway' else service
            records = consul_json('/v1/health/service/' + app + '?passing=true')
            passing &= len(records) == 1
            if records:
                registered = records[0]['Service']
                assert registered['Address'] == service and registered['Port'] == 8080, registered
                assert registered['ID'] == app + '-docker', registered
                assert all(check['Status'] == 'passing' for check in records[0]['Checks'])
        if passing:
            break
        assert time.monotonic() < deadline, 'Consul health checks never all passed'
        time.sleep(2)
    checks = consul_json('/v1/agent/checks')
    for service in containers:
        if service in applications:
            app = 'apigateway' if service == 'api-gateway' else service
            check = checks['service:' + app + '-docker']
            expected_url = 'http://' + service + ':8080/actuator/health'
            assert check['Type'] == 'http' and check['Status'] == 'passing', check
            # Some Consul responses omit HTTP details from Definition; the
            # successful HTTP check's Output also identifies the actual URL.
            assert (check.get('Definition', {}).get('HTTP') == expected_url
                    or expected_url in check.get('Output', '')), check
    print('PASS: five hostname registrations and passing Consul HTTP health checks', flush=True)

    for source, target in [('album', 'connessioni'), ('recensioni', 'connessioni'),
                           ('connessioni', 'album'), ('connessioni', 'recensioni')]:
        ips = [v['IPAddress'] for v in containers[target]['NetworkSettings']['Networks'].values()]
        result = diag(source, dict(op='deny', host=target, ips=ips))
        assert len(result['tcp_denied']) == len(ips)
        print('PASS: forbidden direct TCP handshakes denied', source, '->', target, result, flush=True)

    # Verify that Consul has neither forwarding nor a CONNECT proxy endpoint.
    blocked = http('album', 'consul', '/v1/connect/ca/roots')
    assert blocked['status'] == 403, blocked
    risks = []
    gateway = http('album', 'api-gateway', '/connessioni/connessioni')
    if gateway['status'] == 200:
        risks.append('Album can call Connessioni indirectly through Gateway (bidirectional bridge + existing routes)')

    # Controlled GET-only check on our own stack demonstrates the API trust boundary.
    # Always deregister it, including when an assertion or probe fails.
    check_id = 'bettermusic-network-probe-' + uuid.uuid4().hex
    try:
        register = http('album', 'consul', '/v1/agent/check/register', 'PUT', {
            'ID': check_id, 'Name': 'Temporary GET-only network audit',
            'HTTP': 'http://connessioni:8080/actuator/health', 'Interval': '1s', 'Timeout': '2s',
        })
        if register['status'] == 200:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                check = consul_json('/v1/agent/checks').get(check_id, {})
                if check.get('Status') == 'passing':
                    risks.append('Album can induce Consul to GET Connessioni through HTTP check registration (no ACL)')
                    break
                time.sleep(1)
            else:
                raise AssertionError('Registered probe did not pass; investigate before assessing the alternate path')
        elif register['status'] not in (401, 403):
            raise AssertionError(register)
    finally:
        cleanup = http('album', 'consul', '/v1/agent/check/deregister/' + check_id, 'PUT')
        assert cleanup['status'] in (200, 401, 403), cleanup

    for risk in risks:
        print('LIMITATION:', risk, flush=True)
    print('Direct network checks passed. Full service authorization/isolation is NOT established.', flush=True)
    raise SystemExit(2 if risks else 0)
