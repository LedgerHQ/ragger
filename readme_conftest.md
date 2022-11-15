# How to use the Ragger test framework

This framework allows testing the application on the Speculos emulator or on a real device using LedgerComm or LedgerWallet


## Quickly get started with Ragger and Speculos

### Install ragger and dependencies

```
pip install --extra-index-url https://test.pypi.org/simple/ -r requirements.txt
```

### Compile the application

For all required devices, compile the application by running the following command in the container `ghcr.io/ledgerhq/ledger-app-builder/ledger-app-builder-lite:latest`
```
make BOLOS_SDK=$<device>_SDK
```

Copy the compiled binaries to the elfs directory
```
cp bin/app.elf tests/elfs/<appname>_<device>.elf
```

### Run a simple test

You can use the following command to get your first experience with Ragger and Speculos
```
pytest -v --tb=short --nanox --display
```
Or you can refer to the following section to configure the options you want to use


## Available pytest options

Standard recommended pytest options
```
    -v              formats the test summary in a readable way
    -s              enable logs for successful tests, on Speculos it will enable app logs if compiled with DEBUG=1
    -k <testname>   only run the tests that contain <testname> in their names
    --tb=short      in case of errors, formats the testtraceback in a readable way
``` 

Custom pytest options
```
    --backend <backend>  run the tests against the backend [speculos, ledgercomm, ledgerwallet]. Speculos is the default
    --display            on Speculos, enables the display of the app screen using QT
    --golden_run         on Speculos, screen comparison functions will save the current screen instead of comparing
    --nanos              run only the test for the nanos device
    --nanox              run only the test for the nanox device
    --nanosp             run only the test for the nanosp device
``` 

