# # # # # # # # # # # # # #
# CAPTAINHOOK IDENTIFIER  #
# # # # # # # # # # # # # #
from .utils import bash, filter_python_files

DEFAULT = 'on'


def run(files):
    "Check to see if python files are py3 compatible"
    errors = []
    for py_file in filter_python_files(files):
        # We only want to show errors if we CAN'T compile to py3.
        # but we want to show all the errors at once.
        b = bash('python3 -m py_compile {0}'.format(py_file))
        if b.err:
            b = bash('2to3-2.7 {file}'.format(file=py_file))
            errors.append(b.output.decode(encoding='UTF-8'))
    return "\n".join(errors)
