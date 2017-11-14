#!/usr/bin/env bash
echo "Demarrage du container ameli_checker"

docker run -it --name ameli_checker -d -v "$PWD":/opt -w /opt py_ameli /bin/bash
