from setuptools import setup
import sys


def version(filename='package.version', increment_minor=True,
            increment_major=False):
    """
    Get the package version, optionally incrementing the minor/major
    of the version number.
    """
    try:
        old_version = open(filename).readlines()[0].strip()
    except IOError:
        old_version = "0.0.0"
    split_old_version = old_version.split('.')
    if len(split_old_version) and increment_minor:
        split_old_version[-1] = "%d" % (int(split_old_version[-1]) + 1)
    if len(split_old_version) > 1 and increment_major:
        split_old_version[-2] = "%d" % (int(split_old_version[-2]) + 1)
    new_version = '.'.join(split_old_version)
    if increment_minor or increment_major:
        open(filename, 'w').write(new_version + '\n')
    return new_version


requires = ['six']
if sys.version > '3.0.0':
    print('Python3')
    requires.append('BeautifulSoup4')
else:
    print('Python2')
    requires.append('BeautifulSoup')


print('Setting up under python version %s' % sys.version)
print('Requirements: %s' % ','.join(requires))

setup(
    name="dlipower",
    version=version(increment_minor=True),
    author="Dwight Hubbard",
    author_email="dwight@dwighthubbard.com",
    url="http://pypi.python.org/pypi/dlipower/",
    license="LICENSE.txt",
    packages=["dlipower", ],
    scripts=["dlipower/dlipower", "dlipower/fence_dli"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Power (UPS)',
         'License :: OSI Approved :: BSD License'
    ],
    long_description=open('README.md').read(),
    description="Control digital loggers web power switch",
    requires=requires,
    install_requires=requires
)
