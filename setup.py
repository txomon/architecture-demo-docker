from setuptools import setup

with open('requirements.txt') as f:
    reqs = f.readlines()

setup(
    name='worker',
    description='Simple API runner and worker',
    author='Javier Domingo Cansino',
    author_email='javierdo1@gmail.com',
    packages=['worker'],
    install_requires=reqs,
    entry_points={
        'console_scripts': ['apid=api:main', 'workerd=worker:main']
    },
    zip_safe=False,
)
