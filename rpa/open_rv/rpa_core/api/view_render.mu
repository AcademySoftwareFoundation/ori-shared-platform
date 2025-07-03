module: view_render

{

use commands;
use extra_commands;
use rvtypes;
use rvui;

\: display_feedback(void; string msg, float duration) {
    extra_commands.displayFeedback("%s" % msg, duration);
}

}
