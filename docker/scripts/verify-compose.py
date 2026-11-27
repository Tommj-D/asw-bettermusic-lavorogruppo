#!/usr/bin/env python3
"""Validate the required topology independently of Docker daemon availability."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    'public': {'api-gateway'},
    'gateway-album': {'api-gateway', 'album'},
    'gateway-recensioni': {'api-gateway', 'recensioni'},
    'gateway-connessioni': {'api-gateway', 'connessioni'},
    'gateway-seguite': {'api-gateway', 'recensioni-seguite'},
    'recensioni-album': {'recensioni', 'album'},
    'seguite-album': {'recensioni-seguite', 'album'},
    'seguite-recensioni': {'recensioni-seguite', 'recensioni'},
    'seguite-connessioni': {'recensioni-seguite', 'connessioni'},
    'consul-gateway': {'consul', 'api-gateway'},
    'consul-album': {'consul', 'album'},
    'consul-recensioni': {'consul', 'recensioni'},
    'consul-connessioni': {'consul', 'connessioni'},
    'consul-seguite': {'consul', 'recensioni-seguite'},
    'postgres-album': {'postgres', 'album'},
    'postgres-recensioni': {'postgres', 'recensioni'},
    'postgres-connessioni': {'postgres', 'connessioni'},
    'postgres-seguite': {'postgres', 'recensioni-seguite'},
}


def compose(*args):
    return subprocess.check_output(
        ['docker', 'compose', '-f', str(ROOT / 'docker-compose.yml'), *args],
        cwd=ROOT, text=True,
    )


def validate():
    config = json.loads(compose('config', '--format', 'json'))
    assert set(config['networks']) == set(EXPECTED), 'Unexpected network set'
    assert set(config['services']) == set().union(*EXPECTED.values()), 'Expected exactly seven services'
    assert set(config.get('volumes', {})) == {'postgres-data'}, 'Expected PostgreSQL data volume'
    for name, members in EXPECTED.items():
        network = config['networks'][name]
        assert network['driver'] == 'bridge', name
        assert network.get('internal', False) == (name != 'public'), name
        actual = {s for s, c in config['services'].items() if name in c['networks']}
        assert actual == members, (name, actual, members)
    for name, service in config['services'].items():
        assert set(service['networks']) <= set(EXPECTED), name
        assert service['cap_drop'] == ['ALL'], name
        assert 'no-new-privileges:true' in service['security_opt'], name
        assert service['read_only'] and not service.get('privileged'), name
        assert service.get('sysctls', {}).get('net.ipv4.ip_forward') == '0', name
        assert service['user'].split(':')[0] not in ('0', 'root'), name
        assert int(service['mem_limit']) > 0 and float(service['cpus']) > 0, name
        assert service['pids_limit'] > 0 and service['healthcheck'], name
        assert service['restart'] == 'unless-stopped', name
        assert service['logging']['options']['max-size'] == '10m', name
        assert not service.get('network_mode'), name
        assert not service.get('cap_add'), name
        for mount in service.get('volumes', []):
            if name == 'postgres':
                assert mount['type'] == 'volume' and mount['source'] == 'postgres-data', mount
                assert mount['target'] == '/var/lib/postgresql' and not mount.get('read_only'), mount
            else:
                assert mount['read_only'] and mount['target'] == '/consul/config/bettermusic.json', name
        if name == 'api-gateway':
            ports = service['ports']
            assert len(ports) == 1 and ports[0]['host_ip'] == '127.0.0.1', ports
            assert str(ports[0]['published']) == '8080' and ports[0]['target'] == 8080, ports
        else:
            assert not service.get('ports'), name
        if name == 'postgres':
            assert service['image'] == 'postgres:18-alpine', name
            assert service['user'] == '70:70', name
            assert len(service['volumes']) == 1, name
            assert service['environment']['POSTGRES_USER'] == 'postgres', name
            assert service['environment']['POSTGRES_DB'] == 'postgres', name
            assert service['environment']['POSTGRES_PASSWORD'], name
            assert any(m.startswith('/var/run/postgresql:') for m in service['tmpfs']), name
            assert service['healthcheck']['test'] == [
                'CMD', 'pg_isready', '-h', '127.0.0.1', '-U', 'postgres', '-d', 'postgres'
            ], name
        elif name != 'consul':
            env = service['environment']
            assert env['PORT'] == env['SERVER_PORT'] == '8080', name
            assert env['SPRING_CLOUD_CONSUL_HOST'] == 'consul', name
            assert env['SPRING_CLOUD_CONSUL_PORT'] == '8500', name
            assert env['SPRING_CLOUD_CONSUL_DISCOVERY_PREFERIPADDRESS'] == 'false', name
            assert env['SPRING_CLOUD_CONSUL_DISCOVERY_HOSTNAME'] == name, name
            assert service['depends_on']['consul']['condition'] == 'service_healthy', name
    return config


if __name__ == '__main__':
    validate()
    print('PASS: 7 services; 18 bridge networks (17 internal); exact matrix; PostgreSQL volume; ports and hardening')
