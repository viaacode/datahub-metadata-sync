-- create harvest table to store vlaamse kunst xml data
CREATE TABLE IF NOT EXISTS harvest_vkc(
    id SERIAL PRIMARY KEY,
    vkc_xml VARCHAR,
    mam_xml VARCHAR,
    work_id VARCHAR,
    datestamp timestamp with time zone,
    synchronized BOOL DEFAULT 'false',
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now()
);

