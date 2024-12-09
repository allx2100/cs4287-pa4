db = new Mongo().getDB("kafka_db");

if (!db.getCollectionNames().includes("images")) {
    db.createCollection("images");
    print("Collection 'images' created in 'kafka_db' database.");
} else {
    print("Collection 'images' already exists.");
}
