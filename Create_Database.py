import mysql.connector

# Establish connection to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword"
)

# Create a cursor object
cursor = conn.cursor()

# Drop the database if it exists
cursor.execute("drop database if exists ai_repo")

# Create the database
cursor.execute("create database ai_repo")

# Switch to the new database
cursor.execute("use ai_repo")

# Drop tables if they exist
cursor.execute("drop table if exists ai_llm_model_chat")
cursor.execute("drop table if exists ai_rag_scene")
cursor.execute("drop table if exists ai_rag_kb_doc")
cursor.execute("drop table if exists ai_rag_kb")
cursor.execute("drop table if exists system_users")

# Create the system_users table
cursor.execute("""
    create table system_users (
        id int auto_increment primary key,
        username varchar(255) not null,
        nickname varchar(255),
        create_time datetime,
        deleted tinyint(1) default 0
    )
""")

# Create the ai_rag_kb table (Knowledge Base)
cursor.execute("""
    create table ai_rag_kb (
        id int auto_increment primary key,
        user_id int,
        create_time datetime,
        deleted tinyint(1) default 0,
        foreign key (user_id) references system_users(id)
    )
""")

# Create the ai_rag_kb_doc table (Knowledge Base Documents)
cursor.execute("""
    create table ai_rag_kb_doc (
        id int auto_increment primary key,
        kb_id int,
        create_time datetime,
        deleted tinyint(1) default 0,
        foreign key (kb_id) references ai_rag_kb(id)
    )
""")

# Create the ai_rag_scene table (Chat Scenes)
cursor.execute("""
    create table ai_rag_scene (
        id int auto_increment primary key,
        name varchar(255),
        create_time datetime,
        deleted tinyint(1) default 0
    )
""")

# Create the ai_llm_model_chat table
cursor.execute("""
    create table ai_llm_model_chat (
        id int auto_increment primary key,
        user_id int,
        scene_id int,
        create_time datetime,
        platform varchar(255),
        foreign key (user_id) references system_users(id),
        foreign key (scene_id) references ai_rag_scene(id)
    )
""")

# Insert random initial data for system_users
cursor.execute("""
    insert into system_users (username, nickname, create_time) values 
    ('user1', 'User One', now() - interval 5 day), 
    ('user2', 'User Two', now() - interval 4 day), 
    ('user3', 'User Three', now() - interval 3 day), 
    ('user4', 'User Four', now() - interval 2 day), 
    ('user5', 'User Five', now() - interval 1 day)
""")

# Insert random initial data for ai_rag_kb (Knowledge Base)
cursor.execute("""
    insert into ai_rag_kb (user_id, create_time) values 
    (1, now() - interval 5 day), 
    (2, now() - interval 4 day), 
    (3, now() - interval 3 day), 
    (4, now() - interval 2 day), 
    (5, now() - interval 1 day)
""")

# Insert random initial data for ai_rag_kb_doc (Knowledge Base Documents)
cursor.execute("""
    insert into ai_rag_kb_doc (kb_id, create_time) values 
    (1, now() - interval 5 day), 
    (2, now() - interval 4 day), 
    (3, now() - interval 3 day), 
    (4, now() - interval 2 day), 
    (5, now() - interval 1 day)
""")

# Insert random initial data for ai_rag_scene (Chat Scenes)
cursor.execute("""
    insert into ai_rag_scene (name, create_time) values 
    ('Scene One', now() - interval 5 day), 
    ('Scene Two', now() - interval 4 day), 
    ('Scene Three', now() - interval 3 day), 
    ('Scene Four', now() - interval 2 day), 
    ('Scene Five', now() - interval 1 day)
""")

# Insert random initial data for ai_llm_model_chat (Chat Logs)
cursor.execute("""
    insert into ai_llm_model_chat (user_id, scene_id, create_time, platform) values 
    (1, 1, now() - interval 5 day, 'huayuan_rag'), 
    (2, 2, now() - interval 4 day, 'huayuan_rag'), 
    (3, 3, now() - interval 3 day, 'huayuan_rag'), 
    (4, 4, now() - interval 2 day, 'huayuan_rag'), 
    (5, 5, now() - interval 1 day, 'huayuan_rag'),
    (1, 2, now() - interval 4 day, 'huayuan_rag'),
    (2, 3, now() - interval 3 day, 'huayuan_rag'),
    (3, 4, now() - interval 2 day, 'huayuan_rag'),
    (4, 5, now() - interval 1 day, 'huayuan_rag'),
    (5, 1, now(), 'huayuan_rag')
""")

# Commit changes
conn.commit()

# Close cursor and connection
cursor.close()
conn.close()
