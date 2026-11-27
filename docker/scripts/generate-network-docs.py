#!/usr/bin/env python3
"""Generate diagrams from normalized Compose; optional SVGs use local Graphviz."""
import argparse
from pathlib import Path
import runpy
import shutil
import subprocess

h = runpy.run_path(str(Path(__file__).with_name('verify-compose.py')))
root, config = h['ROOT'], h['validate']()
out = root / 'docs/network'


def ident(prefix, name):
    return prefix + name.replace('-', '_')


def generate():
    files = {}
    definitions = ['  ' + ident('c_', name) + '["' + name + '<br/>' + str({'consul': 8500, 'postgres': 5432}.get(name, 8080)) + '"]'
                   for name in config['services']]
    memberships = {net: [s for s, c in config['services'].items() if net in c['networks']]
                   for net in config['networks']}
    detail = ['%% Generated from docker-compose.yml. Run docker/scripts/generate-network-docs.py.',
              'flowchart LR', '  host(["Host: 127.0.0.1:8080"])', *definitions]
    dot = ['graph networks {', 'rankdir=LR;', 'graph [fontname="sans-serif", overlap=false, splines=true];',
           'node [fontname="sans-serif", fontsize=11];', 'edge [color="#64748b"];',
           'host [label="Host: 127.0.0.1:8080", shape=box, style=rounded];']
    for name in config['services']:
        dot.append(f'{ident("c_", name)} [label="{name}", shape=box, style="rounded,filled", fillcolor="#dbeafe"];')
    matrix = ['<!-- Generated from docker-compose.yml -->', '# Matrice rete-container', '',
              '| Rete logica | Nome Docker predefinito | Internal | Container |', '|---|---|---|---|']
    for net, n in config['networks'].items():
        nid = ident('n_', net)
        internal = n.get('internal', False)
        label = net + ('<br/>bridge internal' if internal else '<br/>bridge public')
        detail.append(f'  {nid}(("{label}"))')
        color = '#dcfce7' if net == 'public' else '#fef3c7'
        dot.append(f'{nid} [label="{net}\\ninternal={str(internal).lower()}", shape=ellipse, style=filled, fillcolor="{color}"];')
        for service in memberships[net]:
            detail.append(f'  {ident("c_", service)} --- {nid}')
            dot.append(f'{ident("c_", service)} -- {nid};')
        matrix.append(f'| `{net}` | `{n["name"]}` | `{str(internal).lower()}` | ' + ', '.join(memberships[net]) + ' |')
    detail.append('  host -->|"port publishing TCP 8080"| n_public')
    dot += ['host -- n_public [label="published 8080"];', '}']
    files['docker-networks.mmd'] = '\n'.join(detail) + '\n'
    files['network-matrix.md'] = '\n'.join(matrix) + '\n'
    overview = ['%% Generated from docker-compose.yml.', 'flowchart LR',
                '  host(["127.0.0.1:8080"])', *definitions, '  host --> c_api_gateway']
    overview_dot = ['digraph overview {', 'rankdir=LR;', 'node [shape=box, style="rounded,filled", fillcolor="#dbeafe", fontname="sans-serif"];',
                    'edge [fontname="sans-serif", fontsize=10];', 'host [label="127.0.0.1:8080"];', 'host -> c_api_gateway;']
    for name in config['services']:
        overview_dot.append(f'{ident("c_", name)} [label="{name}"];')
    for net, members in memberships.items():
        if net == 'public':
            continue
        if net.startswith('consul-'):
            source, target = next(s for s in members if s != 'consul'), 'consul'
            overview.append(f'  {ident("c_", source)} -.->|"discovery / health inverso"| c_consul')
            overview_dot.append(f'{ident("c_", source)} -> c_consul [style=dashed, label="discovery / health inverso"];')
        elif net.startswith('postgres-'):
            source = next(s for s in members if s != 'postgres')
            overview.append(f'  {ident("c_", source)} -.->|"TCP 5432 predisposto / {net}"| c_postgres')
            overview_dot.append(f'{ident("c_", source)} -> c_postgres [style=dashed, label="TCP 5432 predisposto / {net}"];')
        else:
            source = 'api-gateway' if net.startswith('gateway-') else 'recensioni-seguite' if net.startswith('seguite-') else 'recensioni'
            target = next(s for s in members if s != source)
            overview.append(f'  {ident("c_", source)} -->|"REST / {net}"| {ident("c_", target)}')
            overview_dot.append(f'{ident("c_", source)} -> {ident("c_", target)} [label="{net}"];')
    overview_dot.append('}')
    files['overview.mmd'] = '\n'.join(overview) + '\n'
    return files, {'docker-networks.svg': '\n'.join(dot), 'overview.svg': '\n'.join(overview_dot)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Fail if generated Mermaid or matrix differs')
    args = parser.parse_args()
    files, svgs = generate()
    out.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        if args.check:
            assert (out / name).read_text() == content, 'Regenerate ' + name
        else:
            (out / name).write_text(content)
    if not args.check and shutil.which('dot'):
        for name, content in svgs.items():
            subprocess.run(['dot', '-Tsvg', '-o', str(out / name)], input=content, text=True, check=True)
    print('PASS: diagrams and matrix match Compose' if args.check else 'Generated network diagrams and matrix')
