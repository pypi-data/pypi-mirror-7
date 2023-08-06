# publishing pip packages

---

# pip install this talk

    !bash
    $: pip install publishing_pip_packages
    $: publishing_pip_packages


---

# about me

.notes: over 60 published node modules & 1 million module installs

- long time node.js developer
- python noob
- loves open source
- wants to write python packages
- wants you to write python packages

---

# how do I start?

---

# me: "pypi looks hard"
- I am very lazy
- requires web sign-up
- lots of (sometimes dense) documentation
- where is the 'hello world?'

---

- pypi: 44,823 in 5 years
- npm: 77,899 in 3 years

![modules](https://s3.amazonaws.com/reonomy-public/modules.png)

---

# minimum viable package

---

# ./setup.py

.notes: full python program, pretty helpful CLI. ridic argument list

    !python
    from setuptools import setup
    setup(
        name='mvp',
        author='Brian',
        author_email='brian.m.carlson@gmail.com',
        version='0.0.1',
        url='https://github.com/brianc/pub...',
        packages='mvp',
        description='this package is completely awesome',
        # 500,000 other optional parameters
    )

---

# ./README

---

# ./mvp/\__init__.py

---

# publishing
- create an account
- register your package
- build your package
- upload your package
- celebrate!!!

---

# publishing...

    !bash
    $: cd ~/src/your_package
    $: python setup.py register sdist upload
    $: echo 'I just did open source! yay!!'

---

# mvp.py

- setup.py
- mvp/\__init__.py
- README

[https://github.com/brianc/mvp.py](https://github.com/brianc/mvp.py)

    !bash
    pip install minimum_viable_package
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
- [pypi](https://pypi.python.org/pypi)
- [dive into python](http://www.diveinto.org/python3/packaging.html)
- [packaging user guide](https://python-packaging-user-guide.readthedocs.org/en/latest/)
- [fantastic packaging reference](http://pythonhosted.org/setuptools/setuptools.html)

---

# Questions?

---

# Thank you
- @briancarlson
- https://github.com/brianc

