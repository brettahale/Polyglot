#! /bin/bash +x

# check_style [NODE_SERVER_NAME]

if [ ${PWD##*/} == "scripts" ]; then                                            
    cd ..                                                                       
fi  

if [ $# -gt 0 ]; then
    PYTHONPATH=`pwd`
    cd polyglot/node_servers/$1
    exe="*.py"
else
    exe="polyglot"
fi

echo -e 'Running Style Checks...'

echo -e '\n========== FLAKE8 CHECKS =========='
flake8 $exe --exclude CVS,polyglot/__init__.py

echo -e '\n========== PYLINT CHECKS =========='
pylint $exe

echo -e '\n=========== TODO CHECKS ==========='
grep todo * -nr --exclude *pyc --exclude-dir CVS --exclude-dir scripts --exclude-dir build

echo -e '\n=========== FUTURE CHECKS ==========='
grep future * -nr --exclude *pyc --exclude-dir CVS --exclude-dir scripts --exclude-dir build

echo -e '\n=========== PDB CHECKS ============'
grep "import pdb" * -nr --exclude *pyc --exclude-dir CVS --exclude-dir scripts --exclude-dir build

echo -e '\nDone'
