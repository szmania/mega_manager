from setuptools import setup

with open('megamanager/__version__.py') as f: exec(f.read())

setup(
    name='megamanager',
    version=__version__,
    description='Multiple MEGA.co.nz account manager that has synchronization and compression capabilities. ',
    url='https://github.com/szmania/mega_manager',
    author='Curtis Szmania',
    author_email='szmania@yahoo.com',
    license='GNU General Public License v3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
    ],
    keywords=['megamanager', 'mega', 'mega.co.nz', 'mega.nz', 'cloud', 'compression'],
    python_requires='>=2.7,<3.0',
    packages=["megamanager"],
    install_requires=['numpy', 'psutil'],
    entry_points={
        'console_scripts': [
            'megamanager = megamanager.__main__:main',
        ],
    },
)
