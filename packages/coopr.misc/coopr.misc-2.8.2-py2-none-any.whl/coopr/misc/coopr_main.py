
import sys

try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.command'):
        plugin_class = entrypoint.load()
except Exception:
    err = sys.exc_info()[1]
    sys.stderr.write( "Error loading coopr.command entry points: %s  entrypoint='%s'\n" % (err, entrypoint) )


import coopr_parser


def main(args=None):
    parser = coopr_parser.get_parser()

    if args is None:
        ret = parser.parse_args()
    else:
        ret = parser.parse_args(args)
    ret.func(ret)

