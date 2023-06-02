from subprocess import check_output
from sys import executable, argv
from Front.Desktop.main import GUI

IN_DEV = True if len(argv) == 2 else False

def warn():
    print('If you are running from source code, be sure to call the program like so \n\n\tpython runDesktop True\n')
    print('This will insure you have the appropriate dependencies at the cost of time')
    print('This obviously is unnecessary when ruinning a binary since the dependencies\nare compiled in it.')


if __name__=='__main__':
    if len(argv) == 1:
        warn()
    if IN_DEV:
        packages = check_output([executable, '-m', 'pip', 'list'])
        name = 'spotdl'
        if name not in str(packages):
            raise Exception('spotdl could not be found, install it whith\npip install spotdl')
    GUI()
