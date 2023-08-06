from setuptools import setup

setup(
    name='model_cache',
    version='0.0.1',
    url='http://github.com/mvj3/model_cache/',
    license='MIT',
    author='David Chen',
    author_email=''.join(reversed("moc.liamg@emojvm")),
    description='model_cache',
    long_description='model_cache',
    packages=['model_cache', 'model_cache/store'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'redis_collections',
        'sqlitedict',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
