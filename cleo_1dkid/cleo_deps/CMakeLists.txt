# set cmake version
cmake_minimum_required(VERSION 3.18.0)

project(CLEO_1DKiD
  LANGUAGES CXX C
  DESCRIPTION "CLEO_1DKiD by Clara Bayley and other developers"
  VERSION 0.0.0
)

find_package(MPI REQUIRED COMPONENTS C)

message(STATUS "CLEO_1DKiD source from CLEO_1DKiD_SOURCE_DIR: ${CLEO_1DKiD_SOURCE_DIR}")
message(STATUS "CLEO_1DKiD build in CLEO_1DKiD_BINARY_DIR: ${CLEO_1DKiD_BINARY_DIR}")

# ensure C++ compiler uses certain settings
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_CXX_STANDARD "20")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CXX_EXTENSIONS ON)

# fetch and make cleo library available
include(FetchContent)
FetchContent_Declare(
  cleo
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  URL https://github.com/yoctoyotta1024/CLEO/archive/refs/tags/v0.64.0.zip
  GIT_TAG 4cf4985b741c098c12baa0c0261ae602a221c31a
)
FetchContent_MakeAvailable(cleo)

message(STATUS "CLEO version v0.64.0, installation in: ${CLEO_BINARY_DIR}")

# print default compiler flags
message(STATUS "CLEO primary CMAKE_CXX_FLAGS: ${CMAKE_CXX_FLAGS}")
