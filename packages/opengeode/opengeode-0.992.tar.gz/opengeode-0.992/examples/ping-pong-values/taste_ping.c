/* Functions to be filled by the user (never overwritten by buildsupport tool) */

#include "ping.h"

ping_data_t ping_input;
ping_data_t ping_output;

void ping_startup()
{
    ping_input.state = PING_START;
    pingprocess(&ping_input, &ping_output);
    ping_input = ping_output;
}

void ping_PI_ACTIVATION()
{
    ping_input.input.value = ping_activation;
    pingprocess(&ping_input, &ping_output);
    if (ping_output.outputs.ping_snd_ping == OPENGEODE_TRUE) {
        ping_RI_SND_PING(&ping_output.outputs.values.ping_snd_ping);
    }
    ping_input = ping_output;
}

