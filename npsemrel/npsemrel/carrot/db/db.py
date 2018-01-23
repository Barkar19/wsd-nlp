import MySQLdb, codecs, os, pickle
from npsemrel.carrot.db import mer_graph


class DB:
    '''
    Wykorzystuje plik polaczenia bazy danych w formacie WordnetLooma.
    Na podstawie tego pliku tworzy polaczenie do MySQLa
    '''

    def __init__(self):
        self.DIST_NOT_FOUND = 99999999

    def connect(self, db_config_file):
        user, password, dbhost, dbname, dbport = self.__read_db_config_file(
            db_config_file)
        return self.__make_db_connection_utf8(user, password, dbhost, dbname,
                                              dbport)

    def read_write_wn_graph(self, db_cfg_file, wn_graph_file):
        graph = None
        if not os.path.exists(wn_graph_file):
            wn_conn = self.__mer_connect_to_db(db_cfg_file)
            with open(wn_graph_file, "w") as f:
                graph = mer_graph.create_graph(wn_conn)
                pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(wn_graph_file, "r") as f:
                graph = pickle.load(f)
        return graph

    def __make_db_connection_utf8(self, db_user, db_passwd, db_host, db_name,
                                  db_port):
        if db_port:
            return MySQLdb.connect(
                host=db_host, user=db_user,
                passwd=db_passwd, db=db_name,
                port=db_port,
                charset='utf8')
        else:
            return MySQLdb.connect(
                host=db_host, user=db_user,
                passwd=db_passwd, db=db_name,
                charset='utf8')

    def __mer_connect_to_db(self, db_cfg_file):
        from django.conf import settings

        user, password, dbhost, dbname, dbport = self.__read_db_config_file(
            db_cfg_file)
        settings.configure(
            DATABASES={
            'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': dbname,
            'USER': user,
            'PASSWORD': password,
            'HOST': dbhost,
            'PORT': str(dbport)
            }
            },
            DEBUG=False)

        import django_model as wn_db

        return wn_db

        # def read_write_wn_graph(self, wn_conn, wn_graph_file):

    def __read_db_config_file(self, config_file):
        '''
        Returns: user, password, dbhost, dbname, dbport
        '''
        user = None
        password = None
        dbhost = None
        dbname = None
        dbport = None
        with codecs.open(config_file, 'r', 'utf8') as fp_db_file:
            for line in fp_db_file:
                if line.startswith('User'):
                    user = line.split('=')[1].strip()
                elif line.startswith('Password'):
                    password = line.split('=')[1].strip()
                elif line.startswith('Url'):
                    host_db_port = line.split('=')[1].replace("jdbc:mysql://",
                                                              '').split(':')
                    dbhost = host_db_port[0].strip()
                    db_port = host_db_port[1].split('/')
                    if len(db_port) > 1:
                        dbport = int(db_port[0])
                        dbname = db_port[1].strip()
                    else:
                        dbname = db_port[1].strip()
        return user, password, dbhost, dbname, dbport