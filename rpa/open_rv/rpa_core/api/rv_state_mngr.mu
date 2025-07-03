module: rv_state_mngr
{
use commands;
use extra_commands;
use rvtypes;
use rvui;

\: disable_frame_change_mouse_events(void; ){
    State state = data();
    state.clickToPlayDisabled = true;
    state.scrubDisabled = true;
}

\: enable_frame_change_mouse_events(void; ){
    State state = data();
    state.clickToPlayDisabled = false;
    state.scrubDisabled = false;
}

}
