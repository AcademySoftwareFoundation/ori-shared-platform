## Objective:

Proof of concept API and widget collection for building cross-platform plugins for review/playback systems (like Itview, OpenRV, xStudio etc).

In this prototype, we have a sample plugin (color corrector) which uses the ReviewPluginAPI and the color corrector widget which works
in both OpenRV and Itview 5.

## Contents:

- review_plugin_api: abstraction layer and widget collection for the common plugin API
- openrv: implementation for the sample plugin functionality (color corrector)
- pkgs: prebuilt packages for the ReviewPluginApi and the color corrector RV packages

## Installing:

In the `pkgs` directory, you will find a python wheel file for the review_plugin_api.
To install it, just do

```
pip install review_plugin_api-0.1-py3-none-any.whl
```

If you are using OpenRV, you will also need to install the two RV packages,
`review_plugin_api-0.1.rvpkg` and `color_corrector-1.0.rvpkg` using OpenRV's package manager.

## Customizing code

If you are making code changes to either review_plugin_api python module or the RV packages, you can
make the install packages again using `pkgs/reinstall_pkgs.sh`. Remember to re-install these
packages again to see the effect in OpenRV.
