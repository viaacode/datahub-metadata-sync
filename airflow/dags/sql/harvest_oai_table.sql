-- create harvest table to store task data
CREATE TABLE IF NOT EXISTS harvest_oai (
    id SERIAL PRIMARY KEY,
    data VARCHAR,
    mam_data VARCHAR,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now()
);
