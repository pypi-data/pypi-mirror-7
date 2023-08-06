echo ""
echo "*** REMEMBER to call script_test_cma.sh in ../../ first ***"
echo ""
cp cma.py _cma.py.backup
cp ../../cma.py .

# see http://www.diveinto.org/python3/packaging.html

echo "-- python setup.py check"
python setup.py check
echo "-- python setup.py --long-description | rst2html.py > output.html"
python setup.py --long-description | rst2html.py > output.html

echo ""
echo "NEXT STEPS:"
echo ""
echo "TESTING"
echo ""
echo "  python setup.py sdist bdist_wininst"
echo "      for (testing) building release"
echo ""
echo "INSTALLING"
echo ""
echo "  python setup.py register sdist bdist_wininst upload"
echo "      to upload a new release (new version number required)"
echo "  python setup.py register"
echo "      to upload only metadata"

##################################################
# for debugging purpose there are single commands:
#
# python setup.py sdist
# python setup.py bdist_wininst  # binary Windows installer
# python setup.py bdist_msi  # better choice(?) but does not exist here

# python setup.py register  # push up the meta data
# python setup.py sdist upload  # push up the source distribution
# python setup.py bdist_wininst upload  # push up Windows binary distribution

#_winreg, win32api or win32con

# to manage the package site and upload docs:
# https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=cma
