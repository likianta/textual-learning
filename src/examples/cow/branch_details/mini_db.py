class Database:
    
    def __init__(self):
        self._db = {
            'master'     : {
                'name'        : 'master',
                'description' : 'This is default branch.',
                'created'     : '2022-01-21',
                'is packed'   : 'no',
                'is pushed'   : 'no',
                'is committed': 'no',
                'oss link'    : '',
                'ecs ip addr' : '',
            },
            'dev'        : {
                'name'        : 'dev',
                'description' : 'Developing',
                'created'     : '2022-01-21',
                'is packed'   : 'yes',
                'is pushed'   : 'no',
                'is committed': 'no',
                'oss link'    : '',
                'ecs ip addr' : '',
            },
            'feature/foo': {
                'name'        : 'feature/foo',
                'description' : '',
                'created'     : '2022-01-21',
                'is packed'   : 'yes',
                'is pushed'   : 'yes',
                'is committed': 'no',
                'oss link'    : '',
                'ecs ip addr' : '',
            },
            'feature/bar': {
                'name'        : 'feature/bar',
                'description' : '',
                'created'     : '2022-01-21',
                'is packed'   : 'yes',
                'is pushed'   : 'yes',
                'is committed': 'yes',
                'oss link'    : '',
                'ecs ip addr' : '10.10.0.85',
            },
        }
    
    def add_branch(self, branch_name):
        from lk_utils.time_utils import timestamp
        data = {
            'name'        : branch_name,
            'created'     : timestamp('y-m-d h:n:s'),
            'is packed'   : 'no',
            'is pushed'   : 'no',
            'is committed': 'no',
            'oss link'    : '',
            'ecs ip addr' : '',
        }
        self._db[branch_name] = data
    
    def get_branch(self, branch_name):
        return self._db[branch_name]


db = Database()
