from setuptools import setup

setup(name='ape',
    packages=['ape', ],
    zip_safe=False,
    entry_points={
       'paste.filter_factory': ['middleware = ape.middleware:filter_factory'],
    },
)
