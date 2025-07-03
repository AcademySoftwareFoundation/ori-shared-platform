module: wipe_api
{

use commands;
use extra_commands;
use rvtypes;
require wipes;
use rvui;

global wipes.Wipe g_wipe_mode;
global bool g_wipe_mode_initialized = false;

\: is_wipe_mode(bool; ){
    State state = data();
    if (state.wipe neq nil && state.wipe.isActive()) {
        return true;
    }
    else {
        return false;
    }
}

\: toggleWipeMode(void; ){
    rvui.toggleWipe();

    State state = data();

    if (state.wipe neq nil && state.wipe.isActive()) {
        // Wipe events may accidentally trigger scrubbing and play
        // Deactivate them to make sure only wipe actions work
        state.scrubDisabled = true;
        state.clickToPlayDisabled = true;
    }
    else {
        state.scrubDisabled = false;
        state.clickToPlayDisabled = false;
    }
}
}