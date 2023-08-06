from setuptools import setup, find_packages
import cquery


f = open('README.rst')
readme = f.read().strip()

f = open('LICENSE.md')
license = f.read().strip()

setup(
    name='cQuery',
    version=cquery.version,
    description='Decentralised content queries',
    long_description=readme,
    author='Marcus Ottosson',
    author_email='marcus@abstractfactory.com',
    url='https://github.com/abstractfactory/cquery',
    license=license,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['cquery = cquery.cli:main']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
)
