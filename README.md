# E-ARK Python Information Package Validator

Core package and command line utility for E-ARK Information Package validation.

The validation core component implements validation rules defined by E-ARK specifications which can be found on the
website of the Digital Information LifeCycle Interoperability Standards Board (DILCIS Board):

<https://dilcis.eu/specifications/>

## Quick Start

### Pre-requisites

Python 3.10 or later is required to run the E-ARK Python Information Package Validator.

You must be running either a Debian/Ubuntu Linux distribution or Windows Subsystem for Linux on Windows to follow these commands.
If you are running a different Linux distribution you must change the apt commands to your package manager.
For getting Windows Subsystem for Linux up and running, please follow the guide further down and then come back to this step.

### Getting up and running with the E-ARK Python Information Package Validator

#### Setting up the environment

It is recommended that you create a directory for your EARK work. Write the following:

```shell
mkdir EARK
```

To enter the directory use the following command

```shell
cd EARK/
```

To retrieve the source code from Github use the following command:

```shell
git clone https://github.com/E-ARK-Software/eark-validator.git
```

To enter the new directory containing the source code do:

```shell
cd eark-validator/
```

It is recommended that you create a virtual environment for Python. By doing that you avoid "polluting" the host operating system with dynamically fetched dependencies and at the same time it creates a reproducible environment for your validator.

To create a virtual environment we need to install virtualenv (not to be confused with the venv package). But we also need python3-pip to handle our Python packages. Install this by issuing the following command:

```shell
sudo apt install python3-pip
```

It will list a number of dependencies. Confirm that you wish to install python3-pip by pressing Y followed by ENTER

Now we can install the virtual environment with the following command:

```shell
sudo apt install python3-virtualenv
```

It will list a number of dependencies. Confirm that you wish to install python3-pip by pressing Y followed by ENTER

Finally we will need unzip. Install that by doing:

```shell
sudo apt install unzip
```

It will list a number of dependencies. Confirm that you wish to install python3-pip by pressing Y followed by ENTER


#### Installing the application

Set up a local virtual environment by issuing the following commands (one line at the time):

```shell
virtualenv -p python3 venv
source venv/bin/activate
```

Update pip to ensure you have the latest and install all the packages required:

```shell
pip install -U pip
pip install .
```

You are now able to run the application "eark-validator". It will validate an Information Package for you.


#### Testing a valid package.

You can test a valid package by first retrieving it from the test corpus:

```shell
wget https://github.com/DILCISBoard/eark-ip-test-corpus/raw/integration/corpora/csip/metadata/metshdr/CSIP12/valid/mets-xml_metsHdr_agent_TYPE_exist.zip
```

Unzip the package:

```shell
unzip mets-xml_metsHdr_agent_TYPE_exist.zip
```

Delete the .zip-file you just downloaded:

```shell
rm mets-xml_metsHdr_agent_TYPE_exist.zip
```

Run the eark-validator:

```shell
eark-validator mets-xml_metsHdr_agent_TYPE_exist/
```

Result:

```shell
('Path mets-xml_metsHdr_agent_TYPE_exist/ is dir, struct result is: '
 'StructureStatus.WellFormed')
```

#### A note on testing a directory

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

### Installing Windows Subsystem for Linux (WSL)

If you do not have Linux and have not previously used WSL please perform the following steps. You must either be logged in as Administrator on the machine or as a user with Administrator rights on the machine.

Start a command prompt (cmd.exe) and then enter the following command:

```shell
wsl --install
```

Confirm that the app is allowed to make changes to your device. Installation begins.

Confirm once more that an app is allowed to make changes to your device.

Retrieving and installing the necessary components take a while. Please do not reboot or shutdown your computer during this process. Even if it seems stalled, it is working.

Installation concludes with the message: "The requested operation is successful. Changes will not be effective until the system is rebooted."

Please reboot your computer.

#### After reboot

You will be prompted to create a new "UNIX username". By convention this is often a less than nine character long all-lowercase username. It does not need to match your Windows username.

You will be prompted to set a password.

You are now logged into Ubuntu (the default Linux distribution used by Windows Subsystem for Linux).

##### Update the system

No matter how fresh the install, there will almost always be updates available. To fetch them write the following:

```shell
sudo apt update
```

And to install them:

```shell
sudo apt upgrade
```

Confirm that you wish to upgrade your packages by pressing Y followed by ENTER

Please resume the guide above.

## For Developers

Developers should install the testing dependencies as well, e.g. [`pytest`](https://docs.pytest.org/en/7.2.x/) and using the [`--editable`](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e) flag:

```shell
pip install -U pip
pip install --editable ".[testing]"
```

### Running tests

You can run unit tests from the project root: `pytest ./tests/`, or generate test coverage figures by: `pytest --cov=ip_validation ./tests/`. If you want to see which parts of your code aren't tested then: `pytest --cov=ip_validation --cov-report=html ./tests/`. After this you can open the file [`<projectRoot>/htmlcov/index.html`](./htmlcov/index.html) in your browser and survey the gory details.
