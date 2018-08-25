from argparse import ArgumentParser

from . import app, routes

parser = ArgumentParser()
parser.add_argument('-s', '--host', type=str, required=False, default='0.0.0.0',
                    help='Server host (see Flask docs)')
parser.add_argument('-p', '--port', type=int, required=False, default=5000,
                    help='Server port (see Flask docs)')
args = parser.parse_args().__dict__

app.run(host=args['host'], port=args['port'])
