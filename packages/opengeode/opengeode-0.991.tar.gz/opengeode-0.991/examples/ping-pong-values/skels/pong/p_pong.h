#ifndef __OPENGEODE_PONG_H__
#define __OPENGEODE_PONG_H__
#include "C_ASN1_Types.h"
#ifndef OPENGEODE_TRUE
#define OPENGEODE_TRUE 1
#endif


#ifndef OPENGEODE_FALSE
#define OPENGEODE_FALSE 0
#endif

#ifdef OPENGEODEDEBUG
#include <stdio.h>
#define OPENGEODEDEBUGMSG(s, args...) fprintf(stderr, s, ##args); fflush (stderr);
#endif


typedef int opengeode_boolean_t;
typedef enum
{
   PONG_START = 0,
   PONG_WAITING = 1
} pong_state_t;


typedef enum
{
   pong_invalid_input = 0,
   pong_recv_ping =    1
} pong_input_t;


typedef struct
{
   pong_state_t state;
   struct
   {
      asn1SccT_INTEGER myval;
   }vars;
   struct
   {
      pong_input_t value;
      union
      {
         int ponginvalid_signal_value;
         asn1SccT_INTEGER pong_recv_ping_myval;
      }values;
   }input;

}pong_data_t;

void pongprocess (pong_data_t* input, pong_data_t*output);
#endif
