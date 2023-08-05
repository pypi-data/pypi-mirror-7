from setuptools import setup, find_packages

setup(
    name='jac',
    author='Jayson Reis',
    author_email='santosdosreis@gmail.com',
    version='0.10',
    packages=find_packages(exclude=('tests*', )),
    install_requires=[
        'beautifulsoup4',
    ],
    description='A Jinja extension (compatible with Flask and other frameworks) to compile and/or compress your assets.',
    url='https://github.com/jaysonsantos/jinja-assets-compressor',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
