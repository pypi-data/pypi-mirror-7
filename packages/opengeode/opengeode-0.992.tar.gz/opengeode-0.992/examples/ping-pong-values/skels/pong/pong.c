/* Functions to be filled by the user (never overwritten by buildsupport tool) */

#include "pong.h"
#include "p_pong.h"

pong_data_t pong_input;
pong_data_t pong_output;

void pong_startup()
{
    pong_input.state = PONG_START;
    pongprocess(&pong_input, &pong_output);
    pong_input = pong_output;
}

void pong_PI_RECV_PING(const asn1SccT_INTEGER *IN_param)
{
    pong_input.input.value = pong_recv_ping;
    pong_input.input.values.pong_recv_ping_myval = *IN_param;
    pongprocess(&pong_input, &pong_output);
    pong_input = pong_output;
}

