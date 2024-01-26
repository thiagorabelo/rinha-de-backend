import errno
import os
import sys

from django.core.management.commands.runserver import Command as RunserverCommand
from uvicorn import run


def get_internal_asgi_application():
    # TODO: Melhore-me
    return "rinha_de_backend.asgi:application"


# Adicionar mais opções do Uvicorn
class Command(RunserverCommand):
    help = "Starts a uvicorn web server for development."

    # TODO: Só funciona para as opções definidas em BaseCommand
    suppressed_base_arguments = {"--verbosity",
                                 "--traceback",
                                 "--nothreading"}

    def run(self, **options):
        self.reload = options["use_reloader"]
        self.nocolor = options["no_color"]
        self.inner_run(None, **options)

    def get_handler(self, *args, **kwargs):
        return get_internal_asgi_application()

    def inner_run(self, *args, **options):
        # 'shutdown_message' is a stealth option.
        shutdown_message = options.get("shutdown_message", "")

        if not options["skip_checks"]:
            self.stdout.write("Performing system checks...\n\n")
            self.check(display_num_errors=True)
        # Need to check migrations here, so can't use the
        # requires_migrations_check attribute.
        self.check_migrations()

        try:
            handler = self.get_handler(*args, **options)
            # uvicorn --port 8000 --workers 1 --loop uvloop --backlog 2048 --no-access-log "rinha_de_backend.asgi:application"
            run(
                app=handler,
                host=self.addr,
                port=int(self.port),
                loop="uvloop",
                reload=self.reload,
                use_colors=not self.nocolor,
                workers=1,  # https://www.uvicorn.org/settings/#production

                # Limits - https://www.uvicorn.org/server-behavior/#resource-limits
                limit_concurrency=None,  # defaults to None
                limit_max_requests=None,  # defaults to None'

                # Resource Limits - https://www.uvicorn.org/settings/#resource-limits
                backlog=2048,
                #access_log=False,
            )
        except OSError as e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            try:
                error_text = ERRORS[e.errno]
            except KeyError:
                error_text = e
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
