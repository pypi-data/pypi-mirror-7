import setuptools

setuptools.setup(name='simpleargs',
    version='0.1.6',
    package_dir={'': 'src'},
    packages=['simpleargs'],
    install_requires=open('requirements.txt').readlines(),
)
