INSERT INTO teams (team_name, logo_image, league_name) VALUES
    ('Team A', 'team_a_logo.png', 'Premier League'),
    ('Team B', 'team_b_logo.png', 'La Liga');

-- Sample data for 'player' table
INSERT INTO players (player_name, current_team_id, player_image) VALUES
    ('Player 1', 1, 'player1_image.png'),
    ('Player 2', 2, 'player2_image.png');

INSERT INTO transfers (player_id, rumoured_team_id, percentage, stage) VALUES
    (1, 2, 50, 'Rumour'),
    (2, 1, 100, 'Confirmed');

INSERT INTO sources (source_link, text, author_name, timestamp, source_type) VALUES
    ('https://www.google.com', 'Some text', 'Author 1', 1234567890, 'News'),
    ('https://www.google.com', 'Some text', 'Author 2', 1234567890, 'News'),
    ('https://www.google.com', 'Some text', 'Author 3', 1234567890, 'News'),
    ('https://www.google.com', 'Some text', 'Author 4', 1234567890, 'News');

INSERT INTO source_transfer (source_id, transfer_id) VALUES
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 2);