from setuptools import setup

setup(
    name='Api',
    description='My personal API to manage Everything',
    version='1.0.0',
    url='https://github.com/netboot-fr/Api',
    license='MIT',
    author='Thomas ILLIET',
    author_email='contact@netboot.fr',
    platforms='any',
    zip_safe=False,
    install_requires=[
        'flask',
        'connexion',
        'Flask-Script'
    ],
    tests_require=['tox'],
    package_dir={'api': 'api'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Flask',
        'Framework :: Pytest',
        'Operating System :: Unix',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='tests',
)
