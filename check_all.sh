#!/usr/bin/env bash
echo "Verification des versions disponibles des referentiels LPP, UCD, CCAM, NABM"

RUNDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $RUNDIR

sh ./check_ref.sh lpp
sh ./check_ref.sh ucd
sh ./check_ref.sh ccam
sh ./check_ref.sh nabm