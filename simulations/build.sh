#!/usr/bin/env bash

if [ "$HOSTNAME" = eudoxos.lr.tudelft.nl ]; then
  n_jobs=14
  conda_path="/home2/dominik/miniconda3/envs/tudat-bundle;/home2/dominik/.local/usr/local"
elif [ "$HOSTNAME" = Dominik-Laptop ]; then
  n_jobs=4
  conda_path="/home/dominik/miniconda3/envs/tudat-bundle;/home/dominik/.local/usr/local"
else
  n_jobs=4
  conda_path=${CONDA_PREFIX}
fi

# configuration step
cmake \
  -DCMAKE_PREFIX_PATH="${conda_path}" \
  -DBoost_NO_BOOST_CMAKE=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -GNinja \
  -S . -B build

# build step
if [[ $? -eq 0 ]]; then
  cmake --build build -j${n_jobs} "$@"
fi
