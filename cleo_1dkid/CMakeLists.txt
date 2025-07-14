cmake_minimum_required(VERSION 3.18.0)
project(project
  LANGUAGES CXX C
  DESCRIPTION "CLEO_1dkid test case by Clara Bayley and other developers"
)

find_package(MPI REQUIRED COMPONENTS C)

## Use the pybind11 package from .gitmodules
add_subdirectory(extern/pybind11)

## Create the Python extension module from C++ source files
set(SOURCES libs/mock_bindcxx/mock.cpp)
pybind11_add_module(mock_cxx MODULE ${SOURCES})

# ## Link any necessary libraries (if needed)
target_link_libraries(mock_cxx PUBLIC MPI::MPI_C)

# ## Set additional compile options if needed
# target_compile_options(mock_cxx PRIVATE -Wall -Wextra)

set_target_properties(mock_cxx PROPERTIES
  CXX_STANDARD 20
  CMAKE_CXX_STANDARD_REQUIRED ON
  CMAKE_CXX_EXTENSIONS ON)

## Include CLEO libraries
add_subdirectory(extern/cleo EXCLUDE_FROM_ALL)
