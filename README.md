# Python-application-Builder
A handy python application builder that can build for both linux and windows.

## Flags
Source (Your projects directory and mandatory)

--linux --windows --both --arch x86 x64 arm64 --version --name --clean --extrahelp


#### typical command:

Python3 BuilderV1 ./JumpingFrogs --linux --arch x64 arm64 --version 1.6 --name JumpoFrog

#### Normal output:

[*] Building for Linux(x64)...

[*] Build root: Builds/code/BuilderV1/executables

[*] Build path: Builds/code/BuilderV1/executables/x64

[*] Running command: ['fpm', '-s', 'dir', '-t', 'deb', '-n', 'test', '-v', '1.6', '-a', 'x64', 'package/=/']

Created package {:path=>"test_1.6_x64.deb"}

[*] Build completed. Output at /Builds/code/BuilderV1/executables

## Untested features

Automatic icon finding and attaching

Building for windows
