from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

with driver.session() as session:
    result = session.run("RETURN 'Conexión correcta' AS mensaje")
    print(result.single()["mensaje"])