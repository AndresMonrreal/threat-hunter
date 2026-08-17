CREATE TABLE IF NOT EXISTS detections (
    id          SERIAL PRIMARY KEY,
    tipo        TEXT NOT NULL,
    ip_origen   TEXT NOT NULL,
    intentos    INTEGER NOT NULL,
    inicio      TIMESTAMPTZ NOT NULL,
    fin         TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (ip_origen, inicio, fin)
);

CREATE INDEX IF NOT EXISTS idx_detections_ip ON detections (ip_origen);
CREATE INDEX IF NOT EXISTS idx_detections_inicio ON detections (inicio);