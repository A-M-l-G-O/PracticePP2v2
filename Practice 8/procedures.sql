-- Upsert single contact
CREATE OR REPLACE PROCEDURE upsert_contact(fn VARCHAR, ln VARCHAR, ph VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name=fn AND last_name=ln) THEN
        UPDATE phonebook SET phone=ph WHERE first_name=fn AND last_name=ln;
    ELSE
        INSERT INTO phonebook(first_name, last_name, phone) VALUES (fn, ln, ph);
    END IF;
END;
$$;

-- Bulk insert with phone validation
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(data TEXT[][])
LANGUAGE plpgsql AS $$
DECLARE
    i INT; fn VARCHAR; ln VARCHAR; ph VARCHAR;
BEGIN
    DROP TABLE IF EXISTS invalid_contacts;
    CREATE TEMP TABLE invalid_contacts(first_name VARCHAR, last_name VARCHAR, phone VARCHAR, reason TEXT);

    FOR i IN 1..array_length(data, 1) LOOP
        fn := data[i][1]; ln := data[i][2]; ph := data[i][3];
        IF ph !~ '^\+?[0-9]{10,15}$' THEN
            INSERT INTO invalid_contacts VALUES (fn, ln, ph, 'Invalid phone');
            CONTINUE;
        END IF;
        CALL upsert_contact(fn, ln, ph);
    END LOOP;
END;
$$;

-- Delete by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(fn VARCHAR DEFAULT NULL, ln VARCHAR DEFAULT NULL, ph VARCHAR DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF ph IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone=ph;
    ELSIF fn IS NOT NULL AND ln IS NOT NULL THEN
        DELETE FROM phonebook WHERE first_name=fn AND last_name=ln;
    ELSE
        RAISE EXCEPTION 'Provide a phone or full name.';
    END IF;
END;
$$;