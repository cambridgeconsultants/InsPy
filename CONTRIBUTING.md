## InsPy Contributing Guide

To contribute something to InsPy, please first create an issue or find an existing issue that isn't already being
worked on, and then feel free to create a Pull Request.

When you submit your Pull Request (PR), please make sure you link it to an issue by putting e.g. 'Fixes #IssueID'.
Some other ways you can link your PR to an issue are listed [here](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

Overall, please try to stick to the recommended contribution process outlined [here](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-open-source) by GitHub.

### How to add a new device
To add a new device you can create a new class under the `inspy.instrument.X.Y` package, where X is the type of your device (e.g. a
new Power Supply or an Oscilloscope, etc.) and Y is the brand name as a Python module. Within that module you can define the
device class itself. It can inherit an existing base class if one exists, if not (in this case this is a new type of device), you
need to make a base class and inherit `inspy.instrument._base.InstrumentBase`. Common functionality across all devices of this type
are put in that base class.

### How to add tests for your new device
To add tests for this new device, we have tried to make the test package structure resemble that of the core Inspy package.
There is a base class in `tests.X` where X is `test_'device type'`, e.g. `test_powersupply`, and the class is called e.g. `OscilloscopeTest`,
i.e. not prefixed with the word test, so that pytest doesn't run the base class. Also, this class is abstract and has an abstract fixture
to actually make a device class. It will return the base class for that device, and subclasses will instantiate specific device types
in these fixtures to actually test them.

Tests are written in the test base class as private methods with default arguments that represent common options to run the test with. Then a public method takes the device class from the fixture and calls the private method with it.
This is so that to run the test with different parameters, the test device subclass can override the public method and then call the private method with different parameters, without having to include all the other parameters too.

For very different tests or unique tests you can include the implementation in the test subclass.