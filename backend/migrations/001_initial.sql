-- Initial metadata is bootstrapped by SQLAlchemy. Apply reviewed migrations for upgrades.
CREATE INDEX IF NOT EXISTS measurement_stream_sequence_idx ON measurements (stream_id,sequence);
CREATE INDEX IF NOT EXISTS investigation_run_status_idx ON investigations (run_id,status);
