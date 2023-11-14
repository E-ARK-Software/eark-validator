# E-ARK Python Information Package Validator

Core package and command line utility for E-ARK Information Package validation.

The validation core component implements validation rules defined by E-ARK specifications which can be found on the
website of the Digital Information LifeCycle Interoperability Standards Board (DILCIS Board):

<https://dilcis.eu/specifications/>

## Quick Start

### Pre-requisites

Python 3.7+ is required.

### Getting the code

Clone the project move into the directory:

```shell
git clone https://github.com/E-ARK-Software/py-e-ark-ip-validator.git
cd py-e-ark-ip-validator
```

### Installating the application

Set up a local virtual environment:

```shell
virtualenv -p python3 venv
source venv/bin/activate
```

Update pip and install the application:

```shell
pip install -U pip
pip install .
```

### Running the validator

From the command line and using the virtual environment, you can run the validator on an information package:

```shell
ip-check <path_to_directory_or_package>
```

If the path passed is a directory, it must contain a single folder which contains the information package (and no other files or folders):

```shell
user@machine:~$ tree input
<path to directory>
  ├── documentation
  ├── metadata
  ├── METS.ipxml
  ├── representations
  │   └── rep1
  │       ├── data
  │       ├── metadata
  │       └── METS.ipxml
  └── schemas
```

If the output paramter (`-o`) is specified, the validation result report (JSON format) is written to a file.

## For Developers

Developers should install the testing dependencies as well, e.g. [`pytest`](https://docs.pytest.org/en/7.2.x/) and using the [`--editable`](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e) flag:

```shell
pip install -U pip
pip install --editable ".[testing]"
```

### Running tests

You can run unit tests from the project root: `pytest ./tests/`, or generate test coverage figures by: `pytest --cov=ip_validation ./tests/`. If you want to see which parts of your code aren't tested then: `pytest --cov=ip_validation --cov-report=html ./tests/`. After this you can open the file [`<projectRoot>/htmlcov/index.html`](./htmlcov/index.html) in your browser and survey the gory details.
