#include <stdio.h>

#include "ping_process.h"
#include "pong_process.h"

pong_data_t pong_input;
pong_data_t pong_output;
ping_data_t ping_input;
ping_data_t ping_output;

void mycallback (void* ptr)
{
   pong_data_t* dptr;
   dptr = (pong_data_t*) ptr;
   fprintf (stderr, "MY CALLBACK\n");
   fprintf (stderr, "var value=%lld\n", dptr->vars.myval);
}

int main (int argc, char* argv[])
{
   int iter;
   pingprocess_init (&ping_input);
   pingprocess_init (&ping_output);

   pongprocess_init (&pong_input);
   pongprocess_init (&pong_output);

   ping_input.state = PING_START;
   pong_input.state = PONG_START;
   ping_input.input.value = ping_activation;
   ping_input.vars.myval = 0;
   pingprocess (&ping_input, &ping_output);
   pongprocess (&pong_input, &pong_output);

   ping_input = ping_output;
   pong_input = pong_output;

   iter = 0;

   while (1)
   {
      ping_input.input.value = ping_activation;
      OPENGEODE_OUTPUT_USER_CALLBACK(ping_output,ping_snd_ping,mycallback);

      pingprocess (&ping_input, &ping_output);

      pong_input.input.value = pong_recv_ping;
      pong_input.input.values.pong_recv_ping = ping_output.outputs.values.ping_snd_ping;

      pongprocess (&pong_input, &pong_output);

      printf ("[%d] Pong vars val=%lld\n", iter, pong_output.vars.myval);

      ping_input = ping_output;
      pong_input = pong_output;
      sleep (3);
      iter = iter + 1;
   }

   return 0;
}
