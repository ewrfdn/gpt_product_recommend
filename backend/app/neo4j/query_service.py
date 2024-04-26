from app.neo4j.connection import connection_manager


class Neo4jDatabaseInspector:
    connection_manager = None

    @classmethod
    def get_all_nodes(cls, page_size=10, page_num=1):
        skip = (page_num - 1) * page_size
        with connection_manager.get_connection() as conn:
            query = """
                        MATCH (n)
                        RETURN n
                        ORDER BY ID(n)
                        SKIP {skip}
                        LIMIT {limit}
                        """.format(skip=skip, limit=page_size)
            return conn.execute_query(query)

    @classmethod
    def get_all_relationships(cls):
        # todo get all nro4j pagination relationship,  return json formate data
        query = "MATCH ()-[r]->() RETURN DISTINCT TYPE(r) as relationship"
        data = cls.execute(query)
        relation_list = [item.value() for item in data]
        return relation_list

    @classmethod
    def execute(cls, query_string: str):
        # todo use query_string query nro4j return json formate data
        with connection_manager.get_connection() as conn:
            data = conn.execute_query(query_string)
        return data

