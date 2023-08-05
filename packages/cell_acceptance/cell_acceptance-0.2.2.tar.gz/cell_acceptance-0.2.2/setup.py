import setuptools

setuptools.setup(
    name='cell_acceptance',
    version="0.2.2",
    description='LibreOffice Calc Calculation Engine',
    long_description=open('README.md').read().strip(),
    author='James Rakich',
    author_email='james@fullandbydesign.com.au',
    url='https://bitbucket.org/MalucoMarinero/cellacceptance',
    py_modules=['cell_acceptance'],
    install_requires=['flask', 'requests'],
    scripts=['bin/cell-acceptance-load-calc'],
    entry_points = {
        'console_scripts': ['cell-acceptance=cell_acceptance.server:server']
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    license='MIT License',
    zip_safe=False,
    keywords='testing'
)
