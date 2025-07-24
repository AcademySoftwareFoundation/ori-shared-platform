## Objective:

To empower VFX and Animation studios to use their custom built review workflows and tools across any review-playback system (such as OpenRV or xStudio),
RPA provides a unified collection of **API modules** and **widgets**.

RPA is designed for pipeline developers to build their review workflows and tools once and deploy them seamlessly across any review-playback system that supports the RPA implementation.

RPA is an abstraction layer between the review widgets you create and the review-playback systems you use.

## Documentation:

[RPA Documentation](https://mariapanneerrajan-spi.github.io/ori-shared-platform/index.html)

## Contents:

- **RPA API Modules:**
Collection of RPA api modules that help manipulate an RPA review session.
- **RPA Widgets:**
Collection of rpa widgets that facilalte a complete review workflow.
- **Open RV Pkgs:**
Prebuilt packages for adding rpa(Review Plugin API) and rpa widgets into Open RV.

## Build and Install

Use the following shell scripts to build and install RPA Wheel and Open-RV Packages.

On Windows, you can use the provided Power-Shell-1 scripts. If you want to use the Bash scripts, use a Unix-like terminal such as mingw64.exe (available through MSYS2).

### Step 1:
Run the following script to build the RPA Wheel and RPA Open RV Packages.

#### Linux/Mac:
`>> ./rpa/build_scripts/build.sh`

#### Windows:
`>> ./rpa/build_scripts/build.ps1`

Following is an example of how the output in `./rpa/build_scripts/output` directory will look like,
1. rpa-0.2.4-py3-none-any.whl
2. rpa_core-1.0.rvpkg
2. rpa_widgets-1.0.rvpkg

### Step 2:
Update the install script found in the path below with the values based on your setup,

#### Linux/Mac:
`./rpa/build_scripts/install.sh`,

#### Windows:
`./rpa/build_scripts/install.ps1`,

1. **RV_HOME:** Your Open RV's installation path
2. **RPA_WHL:** Name of the RPA wheel file built in your `./rpa/build_scripts/output` directory
3. **RPA_CORE_PKG:** Name of the RPA core Open RV package built in your `./rpa/build_scripts/output` directory.
4. **RPA_WIDGETS_PKG:** Name of the RPA widgets Open RV package built in your `./rpa/build_scripts/output` directory.

Once the above values are added, then run the script to install,

#### Linux/Mac:
`>> ./rpa/build_scripts/install.sh`

#### Windows:
`>> ./rpa/build_scripts/install.ps1`

**Step 3:**
Launch Open RV

**Step 4:**
Now in the main Menu Bar, you will find the menu to enter RPA Session mode here,

`Open RV -> Switch to RPA`.

While in RPA Session mode, in the main Menu Bar, you can find all the RPA widgets under,

`Tools -> RPA Widgets`.

## Docs Publish Workflow:

1. If you want to update the static documentation you can update the RST files here,
`>> ./rpa/docs/source`

2. If you want to update the dynamic documenation that is pulled from source-code, run the following command,
`>> cd ./rpa/docs; make clean; make html`

3. For github pages to host the documentaiton move the contents of the ./rpa/docs/build/html folder to the ./docs folder in the root level of rpa.

4. To not use any formating from Github's .nojekyll, add an empty file called,
`>> touch ./docs/.nojekyll`

5. Now when you push to main, the html docs under ./docs will be hosted as github pages.
