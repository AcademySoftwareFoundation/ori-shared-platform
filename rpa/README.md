## Objective:

To empower VFX and Animation studios to use their custom built review workflows and tools across any review-playback system (such as OpenRV or xStudio),
RPA provides a unified collection of **API modules** and **widgets**.

RPA is designed for pipeline developers to build their review workflows and tools once and deploy them seamlessly across any review-playback system that supports the RPA implementation.

RPA is an abstraction layer between the review widgets you create and the review-playback systems you use.

## Documentation:

[RPA Documentation](https://ori-shared-platform.readthedocs.io/en/latest/)

## Contents:

- **RPA API Modules:**
Collection of RPA api modules that help manipulate an RPA review session.
- **RPA Widgets:**
Collection of rpa widgets that facilalte a complete review workflow.
- **Open RV Pkgs:**
Prebuilt packages for adding rpa(Review Plugin API) and rpa widgets into Open RV.

## Build and Install

Use the following shell scripts to build and install RPA Wheel and Open-RV Packages.

On Windows, you can use the provided Power-Shell-1 scripts. To run Power-Shell-1 scripts in your terminal you might have to set the following execution policy,

`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

If you want to use the Bash scripts on Windows, use a Unix-like terminal such as mingw64.exe (available through MSYS2).

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

## Read the Docs Publish Workflow:

1. If you want to update the documentation you can update the sphinx source here,
`>> ./rpa/docs/source`

2. If you want to build and locally test your documentation you can run the following commands,
`>> cd ./rpa/docs; make clean; make html`

3. Kindly make sure to remove your `>> ./rpa/docs/build` directory before pushing.

3. Update the following read the docs config file if needed,
`./.readthedocs.yaml`

5. Now when you push to main, your sphinx html documention will be generated and publised to,
**[https://ori-shared-platform.readthedocs.io/en/latest/](https://ori-shared-platform.readthedocs.io/en/latest/)**
