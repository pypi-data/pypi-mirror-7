from setuptools import setup
import os


data = list()
for d in os.walk('appkit/'):
    if len(d[2]) > 0:
        path_list = [str.join('/', os.path.join(d[0], x).split('/')[1:]) for x in d[2]]
        data.extend(path_list)

requires = ['flask', 'pygobject',]
requires.append('beautifulsoup4')  # v0_2_4 backward compatibility

setup(
    name='AppKit',
    version='0.2.8',
    description='Desktop application framework based on Webkit' +
    ' HTML5, CSS3, Javascript and Python',
    author='Nitipit Nontasuwan',
    author_email='nitipit@gmail.com',
    url='http://nitipit.github.com/appkit/',
    license='MIT',
    platforms=['Linux', ],
    keywords=['framework, html5, gnome, ui'],
    package_dir={'appkit': 'appkit'},
    packages=['appkit'],
    package_data={'appkit': data},
    install_requires=requires,
)
