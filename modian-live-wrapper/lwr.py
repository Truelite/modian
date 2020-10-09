#!/usr/bin/python3

if __name__ == '__main__':
    from lwr.run import LiveWrapper, __version__
    LiveWrapper(version=__version__).run()
