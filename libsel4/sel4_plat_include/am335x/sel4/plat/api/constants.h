/*
 * Copyright 2016, Data61
 * Commonwealth Scientific and Industrial Research Organisation (CSIRO)
 * ABN 41 687 119 230.
 *
 * This software may be distributed and modified according to the terms of
 * the BSD 2-Clause license. Note that NO WARRANTY is provided.
 * See "LICENSE_BSD2.txt" for details.
 *
 * @TAG(DATA61_BSD)
 */

#ifndef __LIBSEL4_SEL4_PLAT_API_CONSTANTS_H_
#define __LIBSEL4_SEL4_PLAT_API_CONSTANTS_H_

#ifdef HAVE_AUTOCONF
#include <autoconf.h>
#else
#ifdef HAVE_SEL4_CONFIG
#include <sel4/config.h>
#endif
#endif

#if defined(CONFIG_HARDWARE_DEBUG_API) || defined(CONFIG_ARM_HYPERVISOR_SUPPORT)
/* Cortex a8 manual, table 12-11 */
#define seL4_NumHWBreakpoints (8)
#define seL4_NumExclusiveBreakpoints (6)
#define seL4_NumExclusiveWatchpoints (2)
#endif

#ifdef CONFIG_HARDWARE_DEBUG_API
#define seL4_FirstWatchpoint (6)
#define seL4_NumDualFunctionMonitors (0)
#endif

#endif /* __LIBSEL4_SEL4_PLAT_API_CONSTANTS_H_ */
