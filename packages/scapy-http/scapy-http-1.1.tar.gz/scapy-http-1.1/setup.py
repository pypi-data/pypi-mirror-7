from setuptools import setup
from distutils.command.install import install
import os.path
import shutil


def install_into_scapy(a):
    print 'Installing the HTTP layer extension into Scapy...',
    import scapy
    import scapy_http
    target_path = os.path.join(
        os.path.dirname(scapy.__file__),
        'layers'
    )
    source_path = os.path.join(
        os.path.dirname(scapy_http.__file__),
        'http.py'
    )
    shutil.copy2(source_path, target_path)
    print 'done!'


install.sub_commands.append(('install_into_scapy', install_into_scapy))

setup(
    name="scapy-http",
    packages=['scapy_http'],
    version="1.1",
    description="HTTP-layer support for Scapy",
    install_requires=['scapy'],
    author=['Luca Invernizzi, Steeve Barbeau'],
    author_email=['invernizzi.l@gmail.com'],
    url='https://github.com/invernizzi/scapy-http',
    download_url='https://github.com/invernizzi/scapy-http/tarball/1.1',
    keywords=['http', 'scapy', 'newtork', 'dissect', 'packets']
)
