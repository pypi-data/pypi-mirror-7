from distutils.core import setup

setup(
    name='F5NoMore',
    version='0.0.3',
    author='Alex Rodrigues',
    author_email='alex@rodrigues.com',
    packages=['f5nomore'],
    license='LICENSE.txt',
    description='Autoreload webpage on file system changes',
    long_description=open('README.txt').read(),
    install_requires="watchdog >= 0.7.0 < 0.8.0"
)