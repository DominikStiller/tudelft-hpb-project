# Adapted from https://github.com/tudat-team/tudat/blob/master/cmake_modules/yolo/YOLOProjectAddExecutable.cmake

function(ADD_LRO_EXECUTABLE arg1 arg2)
    # arg1: executable name
    # arg2: sources

    # Create target name.
    set(target_name "${arg1}")

    # Add executable.
    add_executable(${target_name} ${arg2})

    #==========================================================================
    # TARGET-CONFIGURATION.
    #==========================================================================
    target_include_directories("${target_name}" PUBLIC
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
            $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>
            $<INSTALL_INTERFACE:include>)

    target_include_directories("${target_name}"
            SYSTEM PRIVATE "${EIGEN3_INCLUDE_DIRS}" "${Boost_INCLUDE_DIRS}" "${CSpice_INCLUDE_DIRS}" "${Sofa_INCLUDE_DIRS}" "${TudatResources_INCLUDE_DIRS}"
            )

    target_link_libraries("${target_name}"
            PUBLIC    ${ARGN}
            PRIVATE   "${Boost_LIBRARIES}"
            )

    #==========================================================================
    # BUILD-TREE.
    #==========================================================================
    set_target_properties(${target_name}
            PROPERTIES
            LINKER_LANGUAGE CXX
            ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/lib"
            LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/lib"
            RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/bin"
            )

    set_property(TARGET ${target_name} PROPERTY CXX_STANDARD_REQUIRED YES)
    set_property(TARGET ${target_name} PROPERTY CXX_EXTENSIONS NO)

    # Clean up set variables.
    unset(target_name)

endfunction()