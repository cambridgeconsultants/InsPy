# InsPy

## Introduction

InsPy is a Python library and command-line tool for controlling test and
measurement instruments (oscilloscopes, power supplies, digital
multimeters etc) over USB, Serial, or LAN connections.

It provides a consistent, vendor-agnostic API across supported instrument
brands, so the same code works with a variety of instrument manufacturers.
InsPy makes it easier to write repeatable, automated test scripts without
hand-coding raw SCPI commands for each device. Its OOP-based framework allows
new instruments to be easily added, producing a scalable tool tailored to your
test automation needs.

## Links

- [Documentation](https://cambridgeconsultants.github.io/InsPy/)
- [Quick Start Guide](https://cambridgeconsultants.github.io/InsPy/cookbook/getting_started.html)
- [GitHub Repo](https://github.com/cambridgeconsultants/InsPy)
- [Changelog](https://github.com/cambridgeconsultants/InsPy/blob/main/CHANGELOG.md)

## Table of Contents
- [Installation](#installation)
  - [Command line](#command-line)
  - [wheel](#wheel)
  - [pyproject.toml](#pyproject-toml)
  - [requirements.txt](#requirements-txt)
  - [Uv Package Manager](#uv-package-manager)
- [Development](#development)
  - [Setup](#setup)
  - [Contributing](#contributing)
  - [Testing and test development](#testing-and-test-development)
  - [Releases](#releases)
  - [Building the docs](#building-the-docs)
- [Getting Started](#getting-started)


## Installation
### Command line
```powershell
pip install cc-inspy
```


To check your install in command line run:
```powershell
inspy --version
```

And as always you can get help:
```powershell
inspy --help
```
> To interface an instrument using USB on Windows, install
[Keysight IO Libraries Suite](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html).


If you are running InsPy on Linux and want to connect your device via USB, then you also have to do the following:
```bash
sudo tee /etc/udev/rules.d/99-inspy.rules > /dev/null <<'EOF'
SUBSYSTEM=="usb", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="xxxx", MODE="0660", GROUP="plugdev"
EOF
sudo usermod -aG plugdev "$USER"
sudo udevadm control --reload-rules && sudo udevadm trigger
```

This is to make it so that inspy (and pyVISA) can see your USB device.


### Wheel 

1. Download the wheel from the [InsPy Releases page](https://pypi.org/project/cc-inspy).
2. `pip install cc-inspy-*-py3-none-any.whl`


<a id="pyproject-toml"></a>

### pyproject.toml
Add 'inspy' to the list of dependencies, for example:
```
[project]
dependencies = [
    "cc-inspy"
]
```

<a id="requirements-txt"></a>

### requirements.txt
Add the following to your `requirements.txt`:
```
cc-inspy==1.0.0
```
(replace the version number with the desired version - versions can be identified via the tags)

### Uv package manager

1. Add InsPy as a project dependency `uv add cc-inspy`.
2. Run `uv sync` to install all dependencies.

## Development

See below for information on how to setup a local development environment,
contribute to the project, run tests, and build documentation.

### Setup


> Ensure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) and [Git](https://git-scm.com/install/) installed.

To get setup using InsPy:
1. Clone this repository: `git clone https://github.com/cambridgeconsultants/inspy.git`
2. Navigate back to the inspy repo and install:
```powershell
cd inspy
uv sync
```

3. Reload your IDE (VSCode: `Ctrl+Shift+P` and enter `Developer: Reload Window`) (this may be required when you make changes to your editable)

4. Check editable installed by entering the following terminal command - the inspy version should be returned:
```powershell
uv run inspy --version
```
And you should see it auto complete will the modules in the package. If not, check the correct venv is selected (`Ctrl+Shift+P` `Python: Select Interpreter`)

### Contributing

To add instruments and develop on this project, please follow the instructions in CONTRIBUTING.md in the repository root.

### Testing and test development
We use pytest for writing and running tests. Tests should live in a 
separate file for each instrument, and separately from the development code.

Test files and test functions must start with the prefix `test_`, for 
example `test_oscilloscope_<model_no>.py`, containing `test_get_voltage`.

Example:

    # test_oscilloscope_<model_no>.py
    def test_get_voltage():
        """Dummy test."""
        assert True

You can run these tests using the commands:
- `uv run pytest` to run all test files in the project (bear in mind many tests 
  need real instruments to be connected so they may fail) - not recommended.
- `uv run pytest test_file_name.py` to run all tests in a specific file. This can 
  be run on multiple files in one line too.
- `uv run pytest test_file_name.py::test_func` for a specific test in that file.

### Releases

When there's a commit to main signifying a release, a versioned tag will be added e.g., v2.0. 
The built package is then stored in the GitHub releases using the versioned release tag.

### Building the docs

```
sphinx-build -b html ./docs ./docs/_build/html -W
```

You can then open `_build/html/index.html` in your browser. In windows you can run:
```
start docs/_build/html/index.html
```


## Getting Started

Now you have installed InsPy, check out the [quick start guide](https://cambridgeconsultants.github.io/InsPy/cookbook/getting_started.html)

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

[🔝 Back to top](#links)
