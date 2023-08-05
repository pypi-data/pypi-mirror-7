#include "sys/types.h"
#include "ppapi/c/ppb_messaging.h" 
#include "ppapi/c/pp_instance.h"


const PPB_Messaging *setup_ppapi_connection(PP_Instance *instance) __attribute__((weak));
const PPB_Messaging *setup_ppapi_connection(PP_Instance *instance)
{
  *instance = 0;
  return NULL;
}
