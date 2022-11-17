CREATE TABLE user (
    user_id int NOT NULL,
    name varchar(100),
    temp_threshold decimal,
    humidity_threshold decimal,
    light_intensity decimal,
    PRIMARY KEY (user_id)
);
