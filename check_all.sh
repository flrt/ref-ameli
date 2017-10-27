#!/usr/bin/env bash
echo "Verification des versions disponibles des referentiels LPP, UCD, CCAM"

sh ./check_ref.sh lpp
sh ./check_ref.sh ucd
sh ./check_ref.sh ccam