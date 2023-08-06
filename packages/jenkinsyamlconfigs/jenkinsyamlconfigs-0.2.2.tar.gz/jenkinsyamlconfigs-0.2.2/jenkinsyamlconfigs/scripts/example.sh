. ci_tools/build_ci_virtualenv.sh panama
pip install --extra-index-url http://pypi.mapmyfitness.com/mmf/stable/+simple/ --upgrade citools
pip install --extra-index-url http://pypi.mapmyfitness.com/mmf/stable/+simple/ --upgrade pyul
. ci_tools/unit_tests_build.sh
./tests/run_js_unit_tests.sh