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