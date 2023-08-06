# Publishing Pip Packages

---

# about me

.notes: over 60 node modules

- long time node.js developer
- python noob
- loves open source
- wants to write python packages

---

# getting started
- pypi
- information overload
- where is the 'hello world?'

---

# simple is better?
- npm: 77,899
- pypi: 44,823

---

# minimum viable package

- setup.py
- some_folder/\__init__.py
- README

e.g. https://github.com/brianc/mvp.py

---

# setup.py

.notes: full python program, pretty helpful CLI. ridic argument list

    !python
    from setuptools import setup
    setup(
        name='package_name',
        author='Brian',
        author_email='brian.m.carlson@gmail.com',
        version='0.0.1',
        url='https://github.com/brianc/publishing_pip_packages.git',
        packages='package_name',
        description='this package is completely awesome',
        # 500,000 other optional parameters
    )

---

# publishing
- create an account
- register your package
- build your package
- upload your package
- celebrate!!!

---

# tips
- small, self-contained, focused
- documentation
- tests
- marketing

---

# cookiecutter

- radical
- https://github.com/audreyr/cookiecutter-pypackage.git

---

# Links
- one
- two
- three

---

# Questions?

---

# Thank you
- @briancarlson
- https://github.com/brianc

