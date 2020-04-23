#create temporary table: robot sessions
CREATE TEMPORARY TABLE IF NOT EXISTS robot_sessions (
	session_id INT,
    PRIMARY KEY(session_id)
);
INSERT INTO robot_sessions(session_id) SELECT session_id FROM session_attributes WHERE attribute_id = 12;

SET @robot_events_dump= CONCAT(@@GLOBAL.secure_file_priv,'robot_events_dump.txt');
SET @robot_events_query= CONCAT('SELECT e.* FROM events e JOIN robot_sessions rs ON e.session_id = rs.session_id INTO OUTFILE "',@robot_events_dump,"\" FIELDS TERMINATED BY \'|\' ENCLOSED BY \'\"\' LINES TERMINATED BY \'\\n\'");
PREPARE s1 FROM @robot_events_query;
execute s1;deallocate prepare s1;

SET @robot_forms_dump= CONCAT(@@GLOBAL.secure_file_priv,'robot_forms_dump.txt');
SET @robot_forms_query= CONCAT('SELECT f.* FROM forms f JOIN robot_sessions rs ON f.session_id = rs.session_id INTO OUTFILE "',@robot_forms_dump,"\" FIELDS TERMINATED BY \'|\' ENCLOSED BY \'\"\' LINES TERMINATED BY \'\\n\'");
PREPARE s1 FROM @robot_forms_query;
execute s1;deallocate prepare s1;

SET @robot_session_attributes_dump= CONCAT(@@GLOBAL.secure_file_priv,'robot_session_attributes_dump.txt');
SET @robot_session_attributes_query= CONCAT('SELECT sa.* FROM session_attributes sa JOIN robot_sessions rs ON sa.session_id = rs.session_id INTO OUTFILE "',@robot_session_attributes_dump,"\" FIELDS TERMINATED BY \'|\' ENCLOSED BY \'\"\' LINES TERMINATED BY \'\\n\'");
PREPARE s1 FROM @robot_session_attributes_query;
execute s1;deallocate prepare s1;

SET @robot_sessions_dump= CONCAT(@@GLOBAL.secure_file_priv,'robot_sessions_dump.txt');
SET @robot_sessions_query= CONCAT('SELECT s.* FROM sessions s JOIN robot_sessions rs ON s.id = rs.session_id INTO OUTFILE "',@robot_sessions_dump,"\" FIELDS TERMINATED BY \'|\' ENCLOSED BY \'\"\' LINES TERMINATED BY \'\\n\'");
PREPARE s1 FROM @robot_sessions_query;
execute s1;deallocate prepare s1;

DROP TEMPORARY TABLE IF EXISTS robot_sessions;