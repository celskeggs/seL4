/*
 * Copyright 2014, NICTA
 *
 * This software may be distributed and modified according to the terms of
 * the BSD 2-Clause license. Note that NO WARRANTY is provided.
 * See "LICENSE_BSD2.txt" for details.
 *
 * @TAG(NICTA_BSD)
 */

#ifndef __LIBSEL4_SEL4_ARCH_FUNCTIONS_H
#define __LIBSEL4_SEL4_ARCH_FUNCTIONS_H

#include <sel4/config.h>
#include <sel4/constants.h>

LIBSEL4_INLINE_FUNC seL4_IPCBuffer*
seL4_GetIPCBuffer(void)
{
#if defined(CONFIG_IPC_BUF_GLOBALS_FRAME)
    return *(seL4_IPCBuffer**)seL4_GlobalsFrame;
#elif defined(CONFIG_IPC_BUF_TPIDRURW)
    seL4_Word reg;
    asm ("mrc p15, 0, %0, c13, c0, 2" : "=r"(reg));
    return (seL4_IPCBuffer*)reg;
#else
#error "Unknown IPC buffer strateg"
#endif
}

#endif
