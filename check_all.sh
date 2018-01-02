#!/usr/bin/env bash
echo "Verification des versions disponibles des referentiels LPP, UCD, CCAM, NABM"

sh ./check_ref.sh lpp
sh ./check_ref.sh ucd
sh ./check_ref.sh ccam
sh ./check_ref.sh nabm