#!/usr/bin/env python3
"""Run Django shell with imported modules"""

if __name__ == "__main__":
    import os

    if not os.environ.get("PYTHONSTARTUP"):
        import sys
        from subprocess import check_call

        base_dir = os.path.dirname(os.path.abspath(__file__))

        sys.exit(
            check_call(
                [os.path.join(base_dir, "manage.py"), "shell", *sys.argv[1:]],
                env={**os.environ, "PYTHONSTARTUP": os.path.join(base_dir, "repl.py")},
            )
        )

    # put imports here used by PYTHONSTARTUP
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            exec(  # pylint: disable=exec-used
                "from {app}.models import *".format(app=app)
            )
        except ModuleNotFoundError:
            pass
