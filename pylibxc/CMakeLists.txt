cmake_minimum_required(VERSION 3.21)
cmake_policy(SET CMP0079 NEW)

project(pylibxc LANGUAGES NONE)
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake)

################################### Options ####################################
include(psi4OptionsTools)
option_with_default(PYLIBXC_INSTALL_PYMODDIR "Location within CMAKE_INSTALL_PREFIX to which the Python module is installed. Empty string queries Python interpreter. Don't start with '/'" prefix)

################################# Main Project #################################

#  <<<  Build  >>>

if (PYLIBXC_INSTALL_PYMODDIR STREQUAL "prefix")

    if (NOT TARGET Python3::Interpreter)
        find_package(Python3 COMPONENTS Interpreter REQUIRED)
    endif()

    # Note that this block is *Linux-style* install to `CMAKE_INSTALL_PREFIX` not *Python-style* install to `Python3_EXECUTABLE`'s site-packages.

    execute_process(
      COMMAND ${Python3_EXECUTABLE} -c
        "import os, sys, sysconfig as s; spdir = s.get_path('platlib'); print(spdir.replace(os.path.commonpath([sys.prefix, spdir]), '').lstrip(os.path.sep));"
      OUTPUT_VARIABLE PYLIBXC_INSTALL_PYMODDIR
      OUTPUT_STRIP_TRAILING_WHITESPACE
      )
endif()
message(STATUS "Showing option PYLIBXC_INSTALL_PYMODDIR: ${PYLIBXC_INSTALL_PYMODDIR}")

if(TARGET xc)
    set(_xc_target xc)
else()
    find_package(Libxc REQUIRED COMPONENTS C shared)
    set(_xc_target Libxc::xc)
endif()

#  <<<  Install  >>>

install(
  FILES
    __init__.py
    array_backend.py
    core.py
    dlpack.py
    flags.py
    functional.py
    structs.py
    testing.py
    util.py
    version.py
    example_densities.py
  COMPONENT Libxc_Python
  DESTINATION ${PYLIBXC_INSTALL_PYMODDIR}/pylibxc
  )

if (UNIX)
  install(CODE "
    file(MAKE_DIRECTORY
      \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/${PYLIBXC_INSTALL_PYMODDIR}/pylibxc\"
    )
    execute_process(
      COMMAND \"${CMAKE_COMMAND}\" -E create_symlink
              \"$<TARGET_FILE:${_xc_target}>\"
              \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/${PYLIBXC_INSTALL_PYMODDIR}/pylibxc/libxc.so\"
      COMMAND_ERROR_IS_FATAL ANY
    )
  ")
endif()
