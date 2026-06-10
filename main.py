import os
import sys

# Ensure the app directory is in the path so all imports work correctly
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Change working directory to the app folder so relative paths work
os.chdir(app_dir)

from extrac import EXTrac


def main():
    app = EXTrac()
    app.run()


if __name__ == '__main__':
    main()
