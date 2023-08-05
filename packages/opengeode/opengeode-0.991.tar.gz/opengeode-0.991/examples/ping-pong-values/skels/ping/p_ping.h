#ifndef __OPENGEODE_PING_H__
#define __OPENGEODE_PING_H__
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
   PING_START = 0,
   PING_WAITING = 1
} ping_state_t;


typedef enum
{
   ping_invalid_input = 0,
   ping_activation =    1
} ping_input_t;


typedef struct
{
   ping_state_t state;
   struct
   {
      asn1SccT_INTEGER myval;
   }vars;
   struct
   {
      ping_input_t value;
      union
      {
         int pinginvalid_signal_value;
      }values;
   }input;

   struct
   {
      opengeode_boolean_t ping_snd_ping;
      struct
      {
         int ping_invalid_signal_value;
         asn1SccT_INTEGER ping_snd_ping;
      }values;
   }outputs;

}ping_data_t;

void pingprocess (ping_data_t* input, ping_data_t*output);
#endif
