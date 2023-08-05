from setuptools import setup

version = '2.3.3'

setup(
    name='cbagent',
    version=version,
    author='Couchbase',
    license='Apache Software License',
    packages=[
        'cbagent',
        'cbagent.collectors',
        'cbagent.collectors.libstats'
    ],
    entry_points={
        'console_scripts': [
            'cbagent = cbagent.__main__:main',
        ]
    },
    include_package_data=True,
    install_requires=[
        'couchbase==1.2.0',
        'decorator',
        'fabric==1.8.0',
        'logger',
        'requests==2.1.0',
        'seriesly',
        'spring'
    ],
    dependency_links=[
        'git+https://github.com/couchbaselabs/spring.git',
    ]
)
