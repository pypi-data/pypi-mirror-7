Quick start
===========
For a proper installation of *Kiwi*, follow the instructions in the Documentation.

For a quick flavor of *Kiwi*, you can download the package from the Python Package Index (PyPI), extract it, open the command-prompt, navigate to the root directory, and run:

	> python -c "import kiwi; -gsn kiwi/demo/GSN.txt -gss kiwi/demo/GSS_LUAD.txt -gls kiwi/demo/GLS_LUAD.txt -gsc kiwi/demo/GSC_LUAD.txt"

This command fails if the dependencies (chiefly numpy, matplotlib, networkx) are not properly installed for the Python interpreter called by the command prompt.