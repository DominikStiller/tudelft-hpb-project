cmake_minimum_required(VERSION 3.15.0)

project(hpb_project)
set(CMAKE_CXX_STANDARD 14)


list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/")
include("AddLROExecutable")
include("AddLROLibrary")


find_package(Eigen3 3.4 REQUIRED)
find_package(Boost 1.81 COMPONENTS filesystem REQUIRED)
find_package(tudat 2.12 REQUIRED)


ADD_LRO_LIBRARY(
        lro
        "src/liblro.cpp"
        "src/liblro.h"
        PRIVATE_LINKS "${Tudat_PROPAGATION_LIBRARIES}" Boost::filesystem
        PRIVATE_INCLUDES "${EIGEN3_INCLUDE_DIRS}"
)

ADD_LRO_EXECUTABLE(
        application_lro_baseline
        "src/lro_baseline.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}" lro
)

ADD_LRO_EXECUTABLE(
        application_profile
        "src/lro_baseline.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}" lro
)

ADD_LRO_EXECUTABLE(
        application_lro_json
        "src/lro_json.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}" lro
)

ADD_LRO_EXECUTABLE(
        application_lro_analysis
        "src/lro_analysis.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}" Boost::filesystem
)

ADD_LRO_EXECUTABLE(
        application_bepicolombo
        "src/bepicolombo.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}" lro
)

ADD_LRO_EXECUTABLE(
        application_spice
        "src/spice_exe.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}"
)

ADD_LRO_EXECUTABLE(
        application_shadow_function_estimation
        "src/shadow_function_estimation.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}"
)

ADD_LRO_EXECUTABLE(
        application_lageos
        "src/lageos.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}"
)

ADD_LRO_EXECUTABLE(
        application_regression_test
        "src/regression_test.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}" lro
)

ADD_LRO_EXECUTABLE(
        application_scratch
        "src/scratch.cpp"
        "${Tudat_PROPAGATION_LIBRARIES}"
)
