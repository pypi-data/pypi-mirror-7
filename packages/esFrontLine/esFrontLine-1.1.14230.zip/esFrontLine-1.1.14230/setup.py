import os

from setuptools import setup


root = os.path.abspath(os.path.dirname(__file__))
path = lambda *p: os.path.join(root, *p)
try:
    long_desc = open(path('README.txt')).read()
except Exception:
    long_desc = "<Missing README.txt>"
    print "Missing README.txt"

setup(
    name='esFrontLine',
    version="1.1.14230",
    description='Limit restful requests to backend ElasticSearch cluster:  Queries only.',
    long_description=long_desc,
    author='Kyle Lahnakoski',
    author_email='kyle@lahnakoski.com',
    url='https://github.com/klahnakoski/esFrontLine',
    license='MPL 2.0',
    packages=['esFrontLine'],
    install_requires=['Flask==0.9', 'requests==1.2.3'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts":[
            "esFrontLine = esFrontLine.app:main"
        ]
    },
    classifiers=[  #https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Internet :: Proxy Servers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ]
)
