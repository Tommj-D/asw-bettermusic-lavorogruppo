#!/usr/bin/env python3
"""Optional offline binding/registration test; needs JDK 21+ and a built album.jar."""
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
from zipfile import ZipFile

h = runpy.run_path(str(Path(__file__).with_name('verify-compose.py')))
root, config = h['ROOT'], h['validate']()
java_home = os.environ.get('JAVA_HOME')
java = str(Path(java_home) / 'bin/java') if java_home else 'java'
javac = str(Path(java_home) / 'bin/javac') if java_home else 'javac'
with tempfile.TemporaryDirectory(prefix='bettermusic-binding-') as temp:
    with ZipFile(root / 'album/build/libs/album.jar') as jar:
        for name in jar.namelist():
            if name.startswith('BOOT-INF/lib/') and name.endswith('.jar'):
                (Path(temp) / Path(name).name).write_bytes(jar.read(name))
    classpath = temp + '/*' + os.pathsep + temp
    subprocess.run([javac, '-proc:none', '-cp', classpath, '-d', temp,
                    str(Path(__file__).with_name('CheckConsulBinding.java'))], check=True)
    for service, c in config['services'].items():
        if service in ('consul', 'postgres'):
            continue
        env = os.environ.copy()
        env.update(c['environment'])
        subprocess.run([java, '-cp', classpath, 'CheckConsulBinding', service], env=env, check=True)
