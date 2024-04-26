import os
from neo4j import GraphDatabase


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def execute_query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        with self.__driver.session(database=db) as session:
            return list(session.run(query, parameters))

    def execute(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        with self.__driver.session(database=db) as session:
            return list(session.run(query, parameters))


class Neo4jConnectionManager:
    def __init__(self, uri=None, user=None, pwd=None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.pwd = pwd or os.getenv('NEO4J_PASSWORD', '123456')

    def get_connection(self):
        return Neo4jConnection(self.uri, self.user, self.pwd)


connection_manager = Neo4jConnectionManager()
