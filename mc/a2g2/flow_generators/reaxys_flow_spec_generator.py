import time


class ReaxysFlowSpecGenerator(object):
    def __init__(self, *args, flow_params=None, **kwargs):
        self.flow_params = flow_params

    def generate_flow_spec(self):
        node_specs = []
        #node_specs.append(self.generate_confgen_node_spec())
        node_specs.append(self.generate_conformer_query_node_spec())
        node_specs.append(self.generate_conformer_demux_node_spec())
        flow_spec = {'label': 'reaxys_flow', 'node_specs': node_specs}
        return flow_spec

    def generate_confgen_node_spec(self):
       return { 
            'node': {
                'node_key': 'confgen',
                'node_tasks': [
                    self.generate_compute_parse_load_task(
                        flow_params={
                            'compute_job_spec': {
                                'job_type': 'a2g2.jobs.confgen.confgen',
                            },
                            'parse_job_spec': {
                                'job_type': 'a2g2.jobs.confgen.parse',
                            },
                            'load_job_spec': {
                                'job_type': 'a2g2.jobs.confgen.load',
                            },
                        }),
                ],
                'data': { 
                    # @TODO! REPLACE!
                    #'conformer_chemthings': ['FAKE_%s' % i for i in range(3)]
                    'conformer_chemthings': [1],
                }
            },
            'precursor_keys': ['ROOT'],
        }

    def generate_compute_parse_load_task(self, task_key=None, flow_params=None):
        return {
            'task_key': task_key or 'compute_parse_load_task',
            'task_type': ('a2g2.tasks.nodes'
                          '.run_compute_parse_load_flow_task'),
            'task_params': {
                'flow_params': {
                    'delete_flow_spec_after_creation': True,
                    **flow_params,
                }
            }
        }

    def generate_conformer_query_node_spec(self):
        return {
            'node': {
                'node_key': 'conformer_query',
                'node_tasks': [
                    {
                        'task_key': 'run_conformer_query_job',
                        'task_params': {
                            'job_spec': {
                                'job_type': 'a2g2.jobs.a2g2_db.query',
                                'job_params': {},
                            }
                        },
                        'task_type': 'a2g2.tasks.nodes.run_job_task'
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'from_json': True,
                            'source': ('ctx.tasks'
                                       '.run_conformer_query_job.data'
                                       '.stdout'),
                            'dest': 'ctx.node.scratch.query_results',
                        }
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': 'ctx.node.scratch.query_results.hits',
                            'dest': 'ctx.node.data.conformer_chemthings'
                        },
                    },
                ]
            },
            'precursor_keys': ['ROOT']
        }
    
    def generate_conformer_demux_node_spec(self):
        return {
            'node': {'node_key': 'confgen_demux',
                     'node_tasks': self.generate_confgen_demux_tasks()},
            'precursor_keys': ['conformer_query']
        }

    def generate_confgen_demux_tasks(self):
        demux_tasks = [{
            'task_key': 'confgen_demux',
            'task_type': 'a2g2.tasks.nodes.demux_task',
            'task_params': {
                'items': ('_ctx:flow.nodes.conformer_query.data'
                          '.conformer_chemthings'),
                'demux_flow_params': {
                    'cfg': {
                        'fail_fast': False,
                    },
                    'data': {
                        'run_dft_flow_params': {
                            'flow_spec': self.generate_dft_flow_spec(),
                        }
                    }
                },
                'node_spec_template': self.generate_demux_node_spec_template(),
                'substitutions': [
                    {
                        'source': 'ctx.demux_item',
                        'dest': 'ctx.node_spec.node.data.conformer_chemthing',
                    }
                ]
            }
        }]
        return demux_tasks

    def generate_demux_node_spec_template(self):
        node_spec_template = {
            'node': {
                'node_tasks': [
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'from_value': True,
                            'value': {'multiplicity': 0, 'charge': 0},
                            'dest': 'ctx.node.data.molecule'
                        },
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': ('ctx.node.data.conformer_chemthing'
                                       '.props.a2g2:prop:atoms'),
                            'dest': 'ctx.node.data.molecule.atoms'
                        },
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': 'ctx.flow.data.run_dft_flow_params',
                            'dest': 'ctx.tasks.run_dft_flow.task_params'
                        },
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': 'ctx.node.data.molecule',
                            'dest': ('ctx.tasks.run_dft_flow.task_params'
                                     '.flow_spec.data.molecule')
                        },
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'value': [None],
                            'dest': ('ctx.tasks.run_dft_flow.task_params'
                                     '.flow_spec.data.precursors')
                        },
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': 'ctx.node.data.conformer_chemthing',
                            'dest': ('ctx.tasks.run_dft_flow.task_params'
                                     '.flow_spec.data.precursors.0')
                        },
                    },
                    {
                        'task_key': 'run_dft_flow',
                        'task_type': 'a2g2.tasks.nodes.run_flow_task',
                        'task_params': 'TO BE WIRED',
                    },
                ]
            }
        }
        return node_spec_template

    def generate_dft_flow_spec(self):
        dft_flow_spec = {
            'label': 'dft_flow',
            'node_specs': [
                self.generate_b3lyp_opt_node_spec(),
                self.generate_b3lyp_tddft_node_spec(),
                #self.generate_b3lyp_opt_t1_node_spec(),
            ]
        }
        return dft_flow_spec

    def generate_b3lyp_opt_node_spec(self):
        node_key = 'b3lyp_6_31gs_opt'
        cpl_key = node_key + '_cpl'
        return {
            'node': {
                'node_key': node_key,
                'node_tasks': [
                    self.generate_wire_precursors_into_cpl_task(
                        precursors_source='ctx.flow.data.precursors',
                        cpl_key=cpl_key),
                    self.generate_wire_molecule_into_cpl_task(cpl_key=cpl_key),
                    self.generate_compute_parse_load_task(
                        task_key=cpl_key,
                        flow_params={
                            'label': 'b3lyp_6_31gs_opt_flow',
                            'compute_job_spec': {
                                'job_type': 'a2g2.jobs.qchem.qchem',
                                'job_params': {
                                    'qchem_params': {
                                        'method': 'b3lyp',
                                        'basis': '6_31gs',
                                        'molecule': 'TO BE WIRED',
                                    }
                                },
                            },
                            'parse_load_params': {
                                'job_type': 'a2g2.jobs.flow.task_list',
                                'job_params': {
                                    'tasks': self.generate_opt_parse_tasks()
                                },
                            },
                        }
                    ),
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': ('ctx.tasks.{cpl_key}.data.flow_data'
                                       '.opt_geom_tag'),
                            'dest': 'ctx.node.data.outputs.opt_geom_tag'
                        }
                    },
                ]
            },
            'precursor_keys': ['ROOT'],
        }

    def generate_wire_precursors_into_cpl_task(self, precursors_source=None,
                                               cpl_key=None):
        return {
            'task_key': 'wire_precursors_into_cpl',
            'task_type': 'set_value',
            'task_params': {
                'source': precursors_source,
                'dest': ('ctx.tasks.{cpl_key}.task_params.flow_params'
                         '.parse_load_params.job_params.flow_data.precursors'
                        ).format(cpl_key=cpl_key)
            }
        }

    def generate_wire_molecule_into_cpl_task(self, cpl_key=None):
        return {
            'task_key': 'wire_molecule_into_cpl',
            'task_type': 'set_value',
            'task_params': {
                'source': 'ctx.flow.data.molecule',
                'dest': ('ctx.tasks.{cpl_key}.task_params.flow_params'
                         '.compute_job_spec.job_params.qchem_params'
                         '.molecule').format(cpl_key=cpl_key)
            }
        }

    def generate_opt_parse_tasks(self):
        return [
            {
                'task_key': 'parse_computation',
                'task_type': ('mc.a2g2.job_modules.qchem.tasks'
                              '.parse_computation_meta_task'),
                'task_params': {
                    'precursors': '_ctx:flow.data.precursors'
                }
            },
            {
                'task_key': 'opt_geom_key',
                'task_type': 'set_value',
                'task_params': {
                    'template': ('{{ctx.tasks.parse_computation.data'
                                 '.computation_meta.uuid}}:opt_geom'),
                    'dest': 'ctx.task.data.key'
                }
            },
            {
                'task_key': 'parse_opt_coords',
                'task_type': ('mc.a2g2.job_modules.qchem.tasks'
                              '.parse_opt_coords_task'),
                'task_params': {
                    'key': '_ctx:tasks.opt_geom_key.data.key',
                }
            },
            {
                'task_key': 'set_extra_geom_props',
                'task_type': ('mc.a2g2.job_modules.qchem.tasks'
                              '.set_geom_props_task'),
                'task_params': {
                    'key': '_ctx:tasks.opt_geom_key.data.key',
                    'props': {
                        'fungly': 'yes',
                        'blammo': 'cowjuice',
                    }
                }
            },
            {
                'task_key': 'collect_chemthing_actions',
                'task_type': ('mc.a2g2.job_modules.a2g2_db.tasks'
                              '.collect_chemthing_actions_task')
            },
            {
                'task_key': 'post_chemthing_actions',
                'task_type': ('mc.a2g2.job_modules.a2g2_db.tasks'
                              '.post_chemthing_actions_task'),
                'task_params': {
                    'chemthing_actions': ('_ctx:tasks.collect_chemthing_actions'
                                          '.data.chemthing_actions'),
                }
            },
            {
                'task_type': 'print',
                'task_params': {
                    'message': '_ctx:tasks.opt_geom_key.data.opt_geom_key',
                }
            }
        ]

    def generate_b3lyp_tddft_node_spec(self):
        node_key = 'b3lyp_opt_tddft'
        cpl_key = node_key + '_cpl'
        return {
            'node': {
                'node_key': node_key,
                'node_tasks': [
                    {
                        'task_key': 'set_query_params',
                        'task_type': 'set_value',
                        'task_params': {
                            'source': ('ctx.flow.nodes.b3lyp_6_31gs_opt.data'
                                       '.outputs.opt_geom_tag'),
                            'dest': 'ctx.task.data.query_params.filters.tag'
                        },
                        'data': {
                            'query_params': {
                                'collection': 'chemthings'
                            }
                        }
                    },
                    *(self.generate_chemthing_query_tasks(
                        query_params_src='set_query_params.data.query_params',
                        dest='ctx.node.data.precursors')
                    ),
                    self.generate_wire_precursors_into_cpl_task(
                        precursors_source='ctx.node.data.precursors',
                        cpl_key=cpl_key
                    ),
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'from_value': True,
                            'value': {'multiplicity': 0, 'charge': 0},
                            'dest': 'ctx.node.data.molecule'
                        },
                    },
                    {
                        'task_type': 'set_value',
                        'task_params': {
                            'source': ('ctx.node.data.opt_geom_chemthing'
                                       '.props.a2g2:prop:atoms'),
                            'dest': 'ctx.node.data.molecule.atoms'
                        },
                    },
                    self.generate_wire_molecule_into_cpl_task(cpl_key=cpl_key),
                    self.generate_compute_parse_load_task(
                        task_key=cpl_key,
                        flow_params={
                            'label': 'b3lyp_6_31gs_opt_flow',
                            'compute_job_spec': {
                                'job_type': 'a2g2.jobs.qchem.qchem',
                                'job_params': {
                                    'qchem_params': {
                                        'method': 'b3lyp',
                                        'basis': '6_31gs',
                                        'molecule': 'TO BE WIRED',
                                    }
                                },
                            },
                            'parse_load_params': {
                                'job_type': 'a2g2.jobs.flow.task_list',
                                'job_params': {
                                    'tasks': self.generate_opt_parse_tasks()
                                },
                            }
                        }
                    )
                ]
            },
            'precursor_keys': ['b3lyp_6_31gs_opt'],
        }

    def generate_chemthing_query_tasks(self, query_params_src=None, dest=None):
        query_task_key = 'query_%s' % int(time.time())
        scratch_path = 'ctx.node.data.%s_scratch.query_results' % query_task_key
        tasks = [
            self.generate_query_task(task_key=query_task_key,
                                     query_params_src=None),
            {
                'task_key': 'parse_query_job_stdout',
                'task_type': 'set_value',
                'task_params': {
                    'from_json': True,
                    'source': 'ctx.tasks.%s.data.stdout' % query_task_key,
                    'dest': scratch_path,
                }
            },
            {
                'task_key': 'pipe_query_hits_to_dest',
                'task_type': 'set_value',
                'task_params': {
                    'source': '%s.hits' % scratch_path,
                    'dest': dest
                },
            },
            {
                'task_key': 'clear_scratch',
                'task_type': 'set_value',
                'task_params': {
                    'value': None,
                    'dest': scratch_path,
                },
            },
        ]
        return tasks

    def generate_query_task(self, task_key=None, query_params_src=None):
        query_task = {
            'task_key': task_key,
            'task_params': {
                'job_spec': {
                    'job_type': 'a2g2.jobs.a2g2_db.query',
                    'job_params': {
                        'query_params': '_ctx:%s' % query_params_src
                    }
                }
            },
            'task_type': 'a2g2.tasks.nodes.run_job_task'
        }
        return query_task

    def generate_b3lyp_opt_t1_node_spec(self):
        node_key = 'b3lyp_6_31gs_opt_t1'
        cpl_key = node_key + '_cpl'
        return {
            'node': {
                'node_key': 'b3lyp_6_31gs_opt_t1',
                'node_tasks': [
                    self.generate_wire_molecule_into_cpl_task(cpl_key=cpl_key),
                    self.generate_compute_parse_load_task(
                        task_key=cpl_key,
                        flow_params={
                            'label': 'b3lyp_6_31gs_opt_t1_flow',
                            'compute_job_spec': {
                                'job_type': 'a2g2.jobs.qchem.qchem',
                                'job_params': {
                                    'qchem_params': {
                                        'method': 'b3lyp',
                                        'basis': '6_31gs',
                                    }
                                },
                            },
                            'parse_job_spec': {
                                'job_type': 'a2g2.jobs.qchem.parse'
                            },
                            'load_job_spec': {
                                'job_type': 'a2g2.jobs.qchem.load'
                            }
                        }
                    ),
                ]
            },
            'precursor_keys': ['ROOT'],
        }

def generate_flow_spec(*args, flow_params=None, **kwargs):
    generator = ReaxysFlowSpecGenerator(*args, flow_params=flow_params,
                                        **kwargs)
    return generator.generate_flow_spec()
