import autotoggl

from setuptools import setup


setup(
    name='autotoggl',
    version=autotoggl.__version__,
    description='Toggl + EventGhost',
    install_requires=[
        'requests>=2.22.0',
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
