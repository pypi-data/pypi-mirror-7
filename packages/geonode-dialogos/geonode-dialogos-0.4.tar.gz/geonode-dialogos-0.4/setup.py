from distutils.core import setup


setup(
    name = "geonode-dialogos",
    version = "0.4",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "a flaggable comments app",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/GeoNode/geonode-dialogos",
    packages = [
        "dialogos",
        "dialogos.templatetags",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
