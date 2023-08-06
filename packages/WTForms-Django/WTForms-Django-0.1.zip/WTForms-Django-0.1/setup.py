from setuptools import setup

setup(
    name='WTForms-Django',
    version='0.1',
    url='http://github.com/wtforms/wtforms-appengine/',
    license='BSD',
    author='Thomas Johansson, James Crasta',
    author_email='wtforms@simplecodes.com',
    description='Django tools for WTForms',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'wtforms_django',
    ],
    package_data={
    },
    test_suite='tests.runtests',
    install_requires=['WTForms>=1.0.5', 'Django>=1.3'],
)
