from .maps import Map
from .matching import matchmaker
from .export import json_exporter, csv_exporter, pickle_exporter

export_functions = {
    "json": json_exporter,
    "csv": csv_exporter,
    "pickle": pickle_exporter
}


class Pandarus(object):
    """Controller for all actions."""
    def __init__(self, from_filepath=None, to_filepath=None,
            from_metadata={}, to_metadata={}, with_global=False):
        self.from_map = Map(from_filepath, **from_metadata)
        self.to_map = Map(to_filepath, **to_metadata)
        self.with_global = with_global

    def match(self, cpus=None, progressbar=True):
        self.data = matchmaker(
            self.from_map.filepath,
            self.to_map.filepath,
            use_progressbar=progressbar,
            with_global=self.with_global,
            cpus=cpus,
        )
        return self.data

    def add_from_map_fieldname(self, fieldname=None):
        if not self.data:
            raise ValueError("Must match maps first")
        mapping_dict = self.from_map.get_fieldnames_dictionary(fieldname)
        self.data = {
            ('GLO' if k[0] == 'GLO' else mapping_dict[k[0]], k[1]): v
            for k, v in self.data.iteritems()
        }

    def add_to_map_fieldname(self, fieldname=None):
        if not self.data:
            raise ValueError("Must match maps first")
        mapping_dict = self.to_map.get_fieldnames_dictionary(fieldname)
        self.data = {
            (k[0], 'GLO' if k[1] == 'GLO' else mapping_dict[k[1]]): v
            for k, v in self.data.iteritems()
        }

    def export(self, filepath, kind="json", compress=True):
        exporter = export_functions[kind]
        return exporter(self.data, filepath, compressed=compress)
