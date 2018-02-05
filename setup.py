import autotoggl

from setuptools import setup


setup(
    name='autotoggl',
    version=autotoggl.__version__,
    description='Toggl + EventGhost',
    instal_requires=[
        'requests==2.18.4',
    ],
    url='https://beatonma.org/autotoggl',
    packages=[
        'autotoggl',
    ],
    entry_points={
        'console_scripts': [
            'autotoggl = autotoggl.autotoggl:main',
        ],
    },
    zip_safe=False,
    )
