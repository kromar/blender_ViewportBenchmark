


benchmark_config = {
        'shading_type': {
            'WIREFRAME': {
                'Enabled': True, 
                'object_mode': { 
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
            'SOLID': {
                'Enabled': True, 
                'object_mode': {
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
            'MATERIAL': {
                'Enabled': True, 
                'object_mode': {
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
            'RENDERED': {
                'Enabled': True, 
                'object_mode': {
                    'EDIT': {'Enabled': False, 'score':[]},
                    'OBJECT': {'Enabled': True, 'score':[]},
                    'SCULPT': {'Enabled': False, 'score':[]},
                    },
            },
        },

        'modifiers': [
            'ARRAY', 
            'BEVEL', 
            'BOOLEAN', 
            'MULTIRES', 
            'SUBSURF', 
        ],
              
        'show_wireframe': False,
    }