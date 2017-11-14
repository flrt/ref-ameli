#!/usr/bin/env bash
echo "Verification des versions disponibles des referentiels LPP, UCD, CCAM"

docker run -t -v "$PWD":/opt -w /opt py_ameli sh ./check_ref.sh lpp
docker run -t -v "$PWD":/opt -w /opt py_ameli sh ./check_ref.sh ucd
docker run -t -v "$PWD":/opt -w /opt py_ameli sh ./check_ref.sh ccam
