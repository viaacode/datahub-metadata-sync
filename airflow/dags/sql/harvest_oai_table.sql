-- create harvest table to store task data
CREATE TABLE IF NOT EXISTS harvest_oai (
    id SERIAL PRIMARY KEY,
    vkc_xml VARCHAR,
    mam_xml VARCHAR,
    published_id VARCHAR,
    datestamp timestamp with time zone,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now()
);

