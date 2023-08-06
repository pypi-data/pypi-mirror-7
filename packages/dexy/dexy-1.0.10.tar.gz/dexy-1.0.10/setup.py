from setuptools import setup, find_packages
from dexy.version import DEXY_VERSION

setup(
        author='Ana Nelson',
        author_email='ana@ananelson.com',
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Financial and Insurance Industry",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Topic :: Documentation",
            "Topic :: Software Development :: Build Tools",
            "Topic :: Software Development :: Code Generators",
            "Topic :: Software Development :: Documentation",
            "Topic :: Text Processing",
            "Topic :: Text Processing :: Markup :: HTML",
            "Topic :: Text Processing :: Markup :: LaTeX"
            ],
        description='Document Automation',
        ### "entry-points"
        entry_points = {
            'console_scripts' : [
                'dexy = dexy.commands:run'
                ],
            'pygments.lexers' : [
                'rst+django = dexy.filters.utils:RstDjangoLexer'
                ]
            },
        ### @end
        include_package_data = True,
        install_requires = [
            # for internal dexy use or used in many common plugins
            'BeautifulSoup4',
            'PyYAML',
            'cashew>=0.2.7',
            'chardet',
            'inflection>=0.2.0',
            'jinja2',
            'pexpect',
            'ply>=3.4',
            'pygments',
            'python-modargs>=1.7',
            'requests>=0.10.6',
            # dexy utilities
            'dexy_viewer', ## TODO version
            # for convenience of running additional filters
            'Markdown',
            'docutils'
            ],
        name='dexy',
        packages=find_packages(),
        url='http://dexy.it',
        version=DEXY_VERSION
    )
