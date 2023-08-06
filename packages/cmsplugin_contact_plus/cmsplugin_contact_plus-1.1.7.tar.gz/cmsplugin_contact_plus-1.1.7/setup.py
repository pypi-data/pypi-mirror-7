from setuptools import setup, find_packages


setup(
    name = 'cmsplugin_contact_plus',
    version = '1.1.7', 
    packages=find_packages(),
    license = 'BSD License',
    url = 'https://github.com/arteria/cmsplugin-contact-plus/',
    description = 'A django CMS plugin to dynamically create contact forms.',
    long_description = open('README.md').read()+"\n",
    author = 'arteria GmbH',
    author_email = 'admin@arteria.ch',
    install_requires = ['django-inline-ordering'], #TODO: add others
    include_package_data=True
)
# eof
