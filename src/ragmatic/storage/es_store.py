import json
from .bases import MetadataStore
from ..code_analysis.metadata_units.bases import ModuleData
from elasticsearch import Elasticsearch


class ElasticsearchMetadataStore(MetadataStore):

    name = 'elasticsearch'

    def __init__(self, config):
        self.index_name = config.pop('index_name')
        self._module_name_field = config.pop('module_name_field', "name")
        self._index_mapping_loc = config.pop('index_mapping_loc')
        self.config = config
        self.es = Elasticsearch([self.config])
    
    def store_all_module_data(self, modules: dict[str, ModuleData]):
        for _, module_data in modules.items():
            self.store_module_data(module_data)

    def store_module_data(self, module_data: ModuleData):
        doc = module_data.model_dump()

    def _create_index(self):
        with open(self._index_mapping_loc) as f:
            index_mapping = json.load(f)
        self.es.indices.create(index=self.index_name, body=index_mapping)

    def query_modules(self, query):
        return self.es.search(index=self.index_name, body=query)

    def get_module(self, module_name):
        query = {
            'query': {
                'term': {
                    self._module_name_field: module_name
                }
            }
        }
        response = self.es.search(index=self.index_name, body=query)
        return response['hits']['hits'][0]['_source']
    