#!/usr/bin/env bash
echo "Verification des versions disponibles des referentiels LPP, UCD, CCAM"

docker exec ameli_checker sh ./check_ref.sh lpp
docker exec ameli_checker sh ./check_ref.sh ucd
docker exec ameli_checker sh ./check_ref.sh ccam
