#!/usr/bin/env python

from mc.utils import import_utils
from mc.utils.commands.subcommand_command import SubcommandCommand

from .houston import Houston


class HoustonCommand(SubcommandCommand):
    def __init__(self, *args, default_cfg_path=None, subcommands=None,
                 **kwargs):
        self.houston = Houston(ensure_db=False)
        self.default_cfg_path = default_cfg_path
        if subcommands:
            self.subcommands = subcommands
        super().__init__(*args, **kwargs)

    @property
    def subcommands(self):
        return self.houston.subcommands

    @subcommands.setter
    def subcommands(self, value):
        self.houston.subcommands = value

    def add_arguments(self, parser=None):
        parser.add_argument('-c', '--cfg_path', dest='cfg_path',
                            help="path to houston cfg file",
                            default=self.default_cfg_path)
        super().add_arguments(parser=parser)

    def handle(self, parsed_args=None, unparsed_args=None):
        raw_cfg = self._load_cfg_from_path(parsed_args['cfg_path'])
        self.houston.set_cfg(cfg=raw_cfg)
        super().handle(parsed_args=parsed_args, unparsed_args=unparsed_args)

    def _load_cfg_from_path(self, cfg_path=None):
        cfg_module = import_utils.load_module_from_path(path=cfg_path)
        return cfg_module.__dict__

    def _get_subcommand_fn(self, subcommand=None):
        subcommand = self.houston._get_subcommand(subcommand)

        def subcommand_fn(parsed_args=None, unparsed_args=None):
            return self.houston._call_subcommand(
                subcommand, parsed_args, unparsed_args)
        return subcommand_fn


if __name__ == '__main__':
    HoustonCommand.run()
