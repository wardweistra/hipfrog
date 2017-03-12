from setuptools import setup, find_packages

NAME = 'Glassfrog Hipchat Bot'
VERSION = '0.1'
mainscript = 'runserver.py'

setup(
    name=NAME,
    version=VERSION,
    description='Hipchat extension to talk to Glassfrog',
    url='https://github.com/wardweistra/glassfrog-hipchat-bot',
    author='Ward Weistra',
    author_email='ward@thehyve.nl',
    license='GNU General Public License V3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['requests', 'Flask-Migrate', 'psycopg2', 'Flask-SQLAlchemy', 'PyJWT',
                      'Flask', 'python-Levenshtein'],
    scripts=[mainscript],
)
