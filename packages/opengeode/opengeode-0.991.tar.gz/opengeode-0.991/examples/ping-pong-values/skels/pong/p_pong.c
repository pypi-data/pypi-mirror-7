#include "p_pong.h"
void pongprocess (pong_data_t* input, pong_data_t*output)
{
   output->state = input->state;
   output->input.value = input->input.value;
   output->vars.myval = input->vars.myval;
   
   switch (input->state)
   {
      case PONG_START:
      {
         OPENGEODEDEBUGMSG ("Going to state  PONG_WAITING\n");
         output->state = PONG_WAITING;
         break;
      }
      case PONG_WAITING:
      {
         switch (input->input.value)
         {
            case (pong_recv_ping):
            {
               OPENGEODEDEBUGMSG ("Received signal pong_recv_ping\n");
               output->vars.myval = input->input.values.pong_recv_ping_myval;
               OPENGEODEDEBUGMSG ("Going to state  PONG_WAITING\n");
               output->state = PONG_WAITING;
               break;
            }
            default:
            {
               OPENGEODEDEBUGMSG ("[pong] did not receive any signal\n");
               break;
            }
         }
         break;
      }
   }
}
