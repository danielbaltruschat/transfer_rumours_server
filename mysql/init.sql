-- Create the 'transfer_data' database
CREATE DATABASE IF NOT EXISTS transfer_data;
USE transfer_data;

-- Table: team
CREATE TABLE IF NOT EXISTS teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(50),
    logo_image VARCHAR(255),
    league_name VARCHAR(50)
);

-- Table: player
CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(50),
    current_team_id INT,
    player_image VARCHAR(255),
    FOREIGN KEY (current_team_id) REFERENCES teams(team_id)
);

-- Table: transfers
CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    rumoured_team_id INT,
    percentage INT(1),
    stage VARCHAR(20), -- Stage as a string field
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (rumoured_team_id) REFERENCES teams(team_id)
);

-- Table: sources
CREATE TABLE IF NOT EXISTS sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_link VARCHAR(255),
    text TEXT,
    author_name VARCHAR(100),
    timestamp INT, -- Unix timestamp as an integer field
    source_type VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS source_transfer (
    source_id INT,
    transfer_id INT,
    PRIMARY KEY (source_id, transfer_id),
    FOREIGN KEY (source_id) REFERENCES sources(source_id),
    FOREIGN KEY (transfer_id) REFERENCES transfers(transfer_id)
);




