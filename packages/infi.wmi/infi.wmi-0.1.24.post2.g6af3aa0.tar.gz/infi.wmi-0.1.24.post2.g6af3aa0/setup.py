
SETUP_INFO = dict(
    name = 'infi.wmi',
    version = '0.1.24.post2.g6af3aa0',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """monkeypatched fork of comptypes to support faster WMI access""",
    long_description = """monkeypatched fork of comptypes to support faster WMI access""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['comtypes',
'setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = []),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

