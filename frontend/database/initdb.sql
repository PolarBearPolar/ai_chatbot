CREATE TABLE IF NOT EXISTS "user"(
	"user_id" VARCHAR(256) PRIMARY KEY,
	username VARCHAR(256) NOT NULL,
	user_password VARCHAR(256) NOT NULL,
	user_gender VARCHAR(256),
	user_age INT,
	CONSTRAINT username_password_uk UNIQUE (username, user_password)
);
CREATE TABLE IF NOT EXISTS chat_history(
	chat_id VARCHAR(256) NOT NULL,
	chat_role VARCHAR(256) NOT NULL,
	chat_message TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"user_id" VARCHAR(256),
	FOREIGN KEY ("user_id") REFERENCES "user" ("user_id")
);