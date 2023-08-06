from setuptools import setup
import os


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


version = "1.0b3"


install_requires = [
    'setuptools',
    'mr.awsome >= 1.0rc2']


try:
    import fabric
except ImportError:
    install_requires.append('Fabric>=1.3.0,!=1.8.3')


setup(
    version=version,
    description="A plugin for mr.awsome providing integration with Fabric.",
    long_description=README + "\n\n",
    name="mr.awsome.fabric",
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='http://github.com/fschulze/mr.awsome.fabric',
    include_package_data=True,
    zip_safe=False,
    packages=['mr'],
    namespace_packages=['mr'],
    install_requires=install_requires,
    entry_points="""
        [mr.awsome.plugins]
        fabric = mr.awsome_fabric:plugin
    """)
