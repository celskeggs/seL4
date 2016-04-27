
option (
        CONFIG_LIB_SEL4_INLINE_INVOCATIONS
        "Inline generated syscall invocations" on
)
option (
        CONFIG_LIB_SEL4_HAVE_REGISTER_STUBS
        "Support syscall stubs without IPC buffer" on
)
# TODO: make these automatically synchronize with the kernel
set(CONFIG_MAX_NUM_TRACE_POINTS 0)
set(CONFIG_IRQ_IOAPIC off)
set(CONFIG_MAX_NUM_IOAPIC 1)
set(CONFIG_MAX_MEM_REGIONS 10)
set(CONFIG_IOMMU on)
set(CONFIG_VTX on)
set(CONFIG_PAE_PAGING off)
set(CONFIG_NUM_PRIORITIES 256)
set(CONFIG_MAX_NUM_BOOTINFO_UNTYPED_CAPS 800)
set(SEL4_DEBUG_KERNEL on)

add_custom_command (
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/invocation.h
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/include/sel4
        COMMAND python2 ${CMAKE_CURRENT_SOURCE_DIR}/tools/invocation_header_gen.py
        --xml ${CMAKE_CURRENT_SOURCE_DIR}/include/interfaces/sel4.xml
        --libsel4 --dest ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/invocation.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/tools/invocation_header_gen.py ${CMAKE_CURRENT_SOURCE_DIR}/include/interfaces/sel4.xml
)
add_custom_command (
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/arch/invocation.h
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/arch
        COMMAND python2 ${CMAKE_CURRENT_SOURCE_DIR}/tools/invocation_header_gen.py
        --xml ${CMAKE_CURRENT_SOURCE_DIR}/arch_include/x86/interfaces/sel4arch.xml
        --libsel4 --arch --dest ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/arch/invocation.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/tools/invocation_header_gen.py ${CMAKE_CURRENT_SOURCE_DIR}/arch_include/x86/interfaces/sel4arch.xml
)
add_custom_command (
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/syscall.h
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/include/sel4
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/tools/xmllint.sh --noout --schema ${CMAKE_CURRENT_SOURCE_DIR}/include/api/syscall.xsd ${CMAKE_CURRENT_SOURCE_DIR}/include/api/syscall.xml
        COMMAND python2 ${CMAKE_CURRENT_SOURCE_DIR}/tools/syscall_header_gen.py --xml ${CMAKE_CURRENT_SOURCE_DIR}/include/api/syscall.xml
        --libsel4_header ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/syscall.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/tools/syscall_header_gen.py ${CMAKE_CURRENT_SOURCE_DIR}/include/api/syscall.xsd ${CMAKE_CURRENT_SOURCE_DIR}/include/api/syscall.xml
)
add_custom_command (
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/types_gen.h
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/include/sel4
        COMMAND python2 ${CMAKE_CURRENT_SOURCE_DIR}/tools/bitfield_gen.py --environment libsel4
        ${CMAKE_CURRENT_SOURCE_DIR}/include/sel4/types.bf ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/types_gen.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/tools/bitfield_gen.py ${CMAKE_CURRENT_SOURCE_DIR}/include/sel4/types.bf
)
add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/interfaces/sel4_client.h
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/include/interfaces
        COMMAND python2 ${CMAKE_CURRENT_SOURCE_DIR}/tools/syscall_stub_gen.py -a x86
        -o ${CMAKE_CURRENT_BINARY_DIR}/include/interfaces/sel4_client.h ${CMAKE_CURRENT_SOURCE_DIR}/include/interfaces/sel4.xml ${CMAKE_CURRENT_SOURCE_DIR}/arch_include/x86/interfaces/sel4arch.xml
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/tools/syscall_stub_gen.py ${CMAKE_CURRENT_SOURCE_DIR}/include/interfaces/sel4.xml ${CMAKE_CURRENT_SOURCE_DIR}/arch_include/x86/interfaces/sel4arch.xml
)

configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/include/sel4/config.h.in
        ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/config.h
)

# include_directories(${CMAKE_CURRENT_BINARY_DIR}/include)
# include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
# include_directories(${CMAKE_CURRENT_SOURCE_DIR}/arch_include/x86)

set(LIB_SEL4_SRC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/include ${CMAKE_CURRENT_SOURCE_DIR}/arch_include/x86 ${CMAKE_CURRENT_BINARY_DIR}/include)
set(LIB_SEL4_BIN_HEADERS ${CMAKE_CURRENT_BINARY_DIR}/include/interfaces/sel4_client.h ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/types_gen.h
        ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/syscall.h ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/arch/invocation.h
        ${CMAKE_CURRENT_BINARY_DIR}/include/sel4/invocation.h)

# "exported" - used by other CMake scripts
set(LIB_SEL4_HEADERS ${LIB_SEL4_SRC_HEADERS} ${LIB_SEL4_BIN_HEADERS})

add_library(sel4 STATIC ${CMAKE_CURRENT_SOURCE_DIR}/src/sel4_bootinfo.c
        ${LIB_SEL4_HEADERS})
target_include_directories(sel4 PUBLIC ${LIB_SEL4_SRC_HEADERS})
