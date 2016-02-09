#!/usr/bin/env python2
#
# Copyright 2014, NICTA
#
# This software may be distributed and modified according to the terms of
# the BSD 2-Clause license. Note that NO WARRANTY is provided.
# See "LICENSE_BSD2.txt" for details.
#
# @TAG(NICTA_BSD)
#

# seL4 System Call ID Generator
# ==============================

from __future__ import print_function
import argparse
import re
import sys
# install tempita using sudo apt-get install python-tempita or similar for your distro
import tempita
import xml.dom.minidom

common_header = """

/* This header was generated by kernel/tools/syscall_header_gen.py.
 *
 * To add a system call number, edit kernel/include/api/syscall.xml
 *
 */"""

kernel_header_template = \
"""/* @LICENSE(OKL_CORE) */""" + common_header + """
#ifndef __ARCH_API_SYSCALL_H
#define __ARCH_API_SYSCALL_H

#ifdef __ASSEMBLER__

/* System Calls */
{{py:syscall_number = -1}}
{{for condition, list in assembler}}
    {{for syscall in list}}
#define SYSCALL_{{upper(syscall)}} ({{syscall_number}})
    {{py:syscall_number -= 1}}
    {{endfor}}
{{endfor}}

#endif

#define SYSCALL_MAX (-1)
#define SYSCALL_MIN ({{syscall_number + 1}})

#ifndef __ASSEMBLER__

enum syscall {
{{py:syscall_number = -1}}
{{for condition, list in enum}}
    {{if len(condition) > 0}}
#if {{condition}}
    {{endif}}
    {{for syscall in list}}
    Sys{{syscall}} = {{syscall_number}},
    {{py:syscall_number -= 1}}
    {{endfor}}
    {{if len(condition) > 0}}
#endif /* {{condition}} */
    {{endif}}
{{endfor}}
};
typedef word_t syscall_t;

/* System call names */
#ifdef CONFIG_DEBUG_BUILD
static char *syscall_names[] UNUSED = {
{{py:syscall_number = 1}}
{{for condition, list in assembler}}
    {{for syscall in list}}
         [{{syscall_number}}] = "{{syscall}}",
        {{py:syscall_number += 1}}
    {{endfor}}
{{endfor}}
};
#endif /* CONFIG_DEBUG_BUILD */
#endif

#endif /* __ARCH_API_SYSCALL_H */
"""

libsel4_header_template = \
"""/* @LICENSE(NICTA) */""" + common_header + """
#ifndef __LIBSEL4_SYSCALL_H
#define __LIBSEL4_SYSCALL_H

#include <autoconf.h>

typedef enum {
{{py:syscall_number = -1}}
{{for condition, list in enum}}
    {{if len(condition) > 0}}
#if {{condition}}
    {{endif}}
    {{for syscall in list}}
    seL4_Sys{{syscall}} = {{syscall_number}},
    {{py:syscall_number -= 1}}
    {{endfor}}
    {{if len(condition) > 0}}
#endif /* {{condition}} */
    {{endif}}
{{endfor}}
    SEL4_FORCE_LONG_ENUM(seL4_Syscall_ID)
} seL4_Syscall_ID;

#endif /* __ARCH_API_SYSCALL_H */
"""

def parse_args():
    parser = argparse.ArgumentParser(description="""Generate seL4 syscall API constants
                                                    and associated header files""")
    parser.add_argument('--xml', type=argparse.FileType('r'),
            help='Name of xml file with syscall name definitions', required=True)
    parser.add_argument('--kernel_header', type=argparse.FileType('w'),
            help='Name of file to generate for kernel')
    parser.add_argument('--libsel4_header', type=argparse.FileType('w'),
            help='Name of file to generate for libsel4')

    result = parser.parse_args()

    if result.kernel_header is None and result.libsel4_header is None:
        print("Error: must provide either kernel_header or libsel4_header",
                file=sys.stderr)
        parser.print_help()
        exit(-1)

    return result

def parse_syscall_list(element):
    syscalls = []
    for config in element.getElementsByTagName("config"):
        config_condition = config.getAttribute("condition")
        config_syscalls = []
        for syscall in config.getElementsByTagName("syscall"):
            name = str(syscall.getAttribute("name"))
            config_syscalls.append(name)
        syscalls.append((config_condition, config_syscalls))

    # sanity check
    assert len(syscalls) != 0

    return syscalls


def parse_xml(xml_file):
    # first check if the file is valid xml
    try:
        doc = xml.dom.minidom.parse(xml_file)
    except:
        print("Error: invalid xml file.", file=sys.stderr)
        sys.exit(-1)

    api = doc.getElementsByTagName("api")
    if len(api) != 1:
        print("Error: malformed xml. Only one api element allowed",
                file=sys.stderr)
        sys.exit(-1)

    configs = api[0].getElementsByTagName("config")
    if len(configs) != 1:
        print("Error: api element only supports 1 config element",
                file=sys.stderr)
        sys.exit(-1)

    if len(configs[0].getAttribute("name")) != 0:
        print("Error: api element config only supports an empty name",
                file=sys.stderr)
        sys.exit(-1)

    # debug elements are optional
    debug = doc.getElementsByTagName("debug")
    if len(debug) != 1:
        debug_element = None
    else:
        debug_element = debug[0]

    api_elements = parse_syscall_list(api[0])
    debug = parse_syscall_list(debug_element)

    return (api_elements, debug)

def convert_to_assembler_format(s):
    words = re.findall('[A-Z][A-Z]?[^A-Z]*', s)
    return '_'.join(words).upper()

def generate_kernel_file(kernel_header, api, debug):
    tmpl = tempita.Template(kernel_header_template)
    kernel_header.write(tmpl.substitute(assembler=api,
        enum=api + debug, upper=convert_to_assembler_format))

def generate_libsel4_file(libsel4_header, syscalls):

    tmpl = tempita.Template(libsel4_header_template)
    libsel4_header.write(tmpl.substitute(enum=syscalls))

if __name__ == "__main__":
    args = parse_args()

    (api, debug) = parse_xml(args.xml)
    args.xml.close()

    if (args.kernel_header is not None):
        generate_kernel_file(args.kernel_header, api, debug)
        args.kernel_header.close()

    if (args.libsel4_header is not None):
        generate_libsel4_file(args.libsel4_header, api + debug)
        args.libsel4_header.close()

