# set cmake version
cmake_minimum_required(VERSION 3.18.0)

project(CLEO_1dkid
  LANGUAGES CXX C
  DESCRIPTION "CLEO_1dkid by Clara Bayley and other developers"
  VERSION 0.52.0
)

find_package(MPI REQUIRED COMPONENTS C)

message(STATUS "CLEO_1dkid source from CLEO_1dkid_SOURCE_DIR: ${CLEO_1dkid_SOURCE_DIR}")
message(STATUS "CLEO_1dkid build in CLEO_1dkid_BINARY_DIR: ${CLEO_1dkid_BINARY_DIR}")

# ensure C++ compiler uses certain settings
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_CXX_STANDARD "20")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CXX_EXTENSIONS ON)

# install Kokkos for project
set(kokkospath ${CLEO_1dkid_SOURCE_DIR}/extern/kokkos)
message(STATUS "Using Kokkos installation from: ${kokkospath}")
add_subdirectory(${kokkospath} ${CLEO_1dkid_BINARY_DIR}/kokkos)

# install yaml-cpp for project
set(yamlcpppath ${CLEO_1dkid_SOURCE_DIR}/extern/yaml-cpp)
message(STATUS "Using yaml-cpp installation from: ${yamlcpppath}")
add_subdirectory(${yamlcpppath} ${CLEO_1dkid_BINARY_DIR}/yaml-cpp)

# print default compiler flags
message(STATUS "CLEO primary CMAKE_CXX_FLAGS: ${CMAKE_CXX_FLAGS}")

# add directories of CLEO libray and main program
add_subdirectory(libs)
