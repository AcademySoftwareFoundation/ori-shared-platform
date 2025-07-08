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

On Windows, use a Unix-like terminal such as mingw64.exe (available through MSYS2) to run the Bash script. Standard Windows Command Prompt (cmd.exe) or PowerShell are not compatible with Bash scripts.

**Step 1:**  
Run the following script to build the RPA Wheel and RPA Open RV Packages.  
`>> build_scripts/build.sh`  

Following is an example of how the output in `build_scripts/output` directory will look like,
1. rpa-0.2.4-py3-none-any.whl
2. rpa_core-1.0.rvpkg
2. rpa_widgets-1.0.rvpkg

**Step 2:**  
Add the following values from your setup into the `build_scripts/install.sh`,

1. **RV_HOME:** Your Open RV's installation path
2. **RPA_WHL:** Name of the RPA wheel file built in your `build_scripts/output` directory
3. **RPA_CORE_PKG:** Name of the RPA core Open RV package.
4. **RPA_WIDGETS_PKG:** Name of the RPA widgets Open RV package.

Once the above values are added, then run the script to install,  
`>> build_scripts/install.sh`  

**Step 3:**
Launch Open RV

**Step 4:**
You can find all the RPA widgets under the RPA menu in OpenRV's main menu bar.

## Docs Publish Workflow:

1. If you want to update the static documentation you can update the RST files here,  
`>> docs/source`

2. If you want to update the dynamic documenation that is pulled from source-code, run the following command,
`>> cd docs; make clean; make html`  

3. From the rpa root dir, move the contents of the html folder to the docs folder in the root level of rpa,  
`>> rm -rf ./docs; mkdir ./docs`  
`>> mv -rf ./rpa/docs/build/html/* ./docs/`  

4. To not use any formating from Github's .nojekyll, add an empty file called,  
`>> touch ./docs/.nojekyll`

5. Clear the contents of the rpa docs build folder,  
`>> rm -rf ./rpa/docs/build`

5. Now when you push to main, the html docs under ./docs will be hosted as github pages.
