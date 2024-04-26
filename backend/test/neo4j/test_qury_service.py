from app.neo4j.query_service import Neo4jDatabaseInspector


def test_get_all_nodes():
    page_size = 10
    page_num = 2
    paged_nodes = Neo4jDatabaseInspector.get_all_nodes(page_size, page_num)
    print("Page {} of Nodes:".format(page_num))
    for node in paged_nodes:
        print(node)


def test_get_all_relationships():
    paged_relationships = Neo4jDatabaseInspector.get_all_relationships()
    print(','.join(paged_relationships))


