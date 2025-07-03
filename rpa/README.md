## Objective:

To empower VFX and Animation studios to use their custom built review workflows and tools across any review-playback system (such as OpenRV or xStudio),
RPA provides a unified collection of **API modules** and **widgets**.

RPA is designed for pipeline developers to build their review workflows and tools once and deploy them seamlessly across any review-playback system that supports the RPA implementation.

RPA is an abstraction layer between the review widgets you create and the review-playback systems you use.

## Documentation:

TO BE UPDATED!

## Contents:

- **RPA API Modules:**  
Collection of RPA api modules that help manipulate an RPA review session.
- **RPA Widgets:**  
Collection of rpa widgets that facilalte a complete review workflow.
- **Open RV Pkgs:**  
Prebuilt packages for adding rpa(Review Plugin API) and rpa widgets into Open RV.

## Installing:

**Step 1:**  
`>> cd build_scripts\pkgs\`

**Step 2:**  
`>> \path\to\openrv\bin\python3 -m pip install --user rpa-*-py3-none-any.whl --force-reinstall`

**Step 3:**  
`>> \path\to\openrv\bin\python3 -m pip install scipy==1.13.1 OpenImageIO==3.0.4 imageio==2.37.0`

**Step 4:**  
Use openrv package manager to install:  
rpa_core-1.0.rvpkg and  
rpa_widgets-1.0.rvpkg

**Step 5:**  
Restart openrv

## Docs Publish Workflow:

1. Update your documentation by updating the Sphinx RST files here,  
`>> cd ./rpa/docs/source`

2. Go back to the docs director and generate the HTML files,  
`>> cd ..; make clean; make html`  

3. From the root level, copy the contents of the html folder to the docs,  
`>> cd ../..; rm -rf ./docs; mkdir ./docs`  
`>> cp -rf ./rpa/docs/build/html/* ./docs/`  

4. To not use any formating from Github's .nojekyll, add an empty file called,  
`>> touch ./docs/.nojekyll`

5. Clear the contents of the rpa docs build folder,  
`>> rm -rf ./rpa/docs/build/*`

5. Now when you push to main, the html docs under ./docs will be hosted as github pages.
