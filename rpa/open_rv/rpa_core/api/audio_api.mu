module: audio_api

{

use commands;
use extra_commands;
use rvtypes;
use rvui;


\: is_scrubbing_mode(bool; ){
    State state = data();
    if (state.scrubAudio) {
        return true;
    }
    else {
        return false;
    }
}

\: toggle_scrubbing_mode(void; bool mode){
    State state = data();
    state.scrubAudio = mode;
    commands.setAudioCacheMode(if state.scrubAudio then CacheGreedy else CacheBuffer);
}

\: check_for_scrubbing(void; ){
    State state = data();
    if (state.scrubAudio) {
        commands.scrubAudio(true, 1.0 / commands.fps(), 1);
    }
    else {
        commands.scrubAudio(false, 0.0, 0);
    }
}

}