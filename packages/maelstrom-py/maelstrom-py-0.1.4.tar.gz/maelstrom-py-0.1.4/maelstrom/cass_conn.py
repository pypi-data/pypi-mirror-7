from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.decoder import dict_factory


class CassandraConnection(object):

    ip = None
    kp = None

    def __init__(self, cass_ip, cass_kp):
        self.ip = cass_ip
        self.kp = cass_kp
        try:
            self.cluster = Cluster(contact_points=self.ip,
                                   control_connection_timeout=10000.0)
            self.session = TransactionManager(self)
            self.session.row_factory = dict_factory
        except NoHostAvailable:
            print "TimeoutError: Possibly a connection issue."

    def destroy_cluster(self):
        ip = None
        kp = None
        self.cluster.shutdown()
        self.session.shutdown()


class TransactionManager:

    sessions = []

    def __init__(self, connector):
        self.connector = connector
        num_sessions = 1  # cpu_count() - 1 if cpu_count() > 1 else 1
        for i in range(num_sessions):
            session = self.connector.cluster.connect(self.connector.kp)
            session.row_factory = dict_factory
            self.sessions.append(session)
        print self.sessions

    def execute(self, *args, **kwargs):
        current_session = self.sessions.pop(0)
        result = current_session.execute_async(*args, **kwargs)
        self.sessions.append(current_session)
        return result

    def shutdown(self):
        for session in self.sessions:
            session.shutdown()
