"""
Flask-MetaRoute
-------------

Flask-MetaRoute adds some useful decorators for routing
"""
from setuptools import setup

setup(
    name='Flask-MetaRoute',
    version='1.3.0',
    url='https://github.com/deep-orca/Flask-MetaRoute',
    license='BSD',
    author='Orca',
    author_email='deep.orca@gmail.com',
    description='Extra routing capabilities for Flask',
    long_description=__doc__,
    packages=['flask_metaroute'],
    zip_safe=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points = """
    [paste.filter_app_factory]
    main = flask_metaroute.middleware:MetaRouteMiddlewareAppFactory
    """
)