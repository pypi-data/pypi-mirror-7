#include "stddef.h"
#include "sys/types.h"
#include "ppapi/c/ppb_messaging.h" 
#include "ppapi/c/pp_instance.h"
#include "ppapi_simple/ps.h"

void* PSUserCreateInstance(PP_Instance inst) __attribute__((weak));
void* PSUserCreateInstance(PP_Instance inst) {
  return NULL;
}

const PPB_Messaging *setup_ppapi_connection(PP_Instance *instance) __attribute__((weak));
const PPB_Messaging *setup_ppapi_connection(PP_Instance *instance)
{
  *instance = 0;
  return NULL;
}
