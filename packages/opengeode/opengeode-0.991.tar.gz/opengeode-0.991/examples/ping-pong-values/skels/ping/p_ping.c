#include "p_ping.h"
void pingprocess (ping_data_t* input, ping_data_t*output)
{
   output->state = input->state;
   output->input.value = input->input.value;
   output->vars.myval = input->vars.myval;
   output->outputs.ping_snd_ping = input->outputs.ping_snd_ping;
   
   switch (input->state)
   {
      case PING_START:
      {
         OPENGEODEDEBUGMSG ("Going to state  PING_WAITING\n");
         output->state = PING_WAITING;
         break;
      }
      case PING_WAITING:
      {
         switch (input->input.value)
         {
            case (ping_activation):
            {
               OPENGEODEDEBUGMSG ("Received signal ping_activation\n");
               output->vars.myval = output->vars.myval + 1;
               output->outputs.ping_snd_ping = OPENGEODE_TRUE;
               output->outputs.values.ping_snd_ping = output->vars.myval;
               OPENGEODEDEBUGMSG ("Going to state  PING_WAITING\n");
               output->state = PING_WAITING;
               break;
            }
            default:
            {
               OPENGEODEDEBUGMSG ("[ping] did not receive any signal\n");
               break;
            }
         }
         break;
      }
   }
}
