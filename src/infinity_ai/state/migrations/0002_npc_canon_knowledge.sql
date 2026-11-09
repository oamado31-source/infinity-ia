-- SPDX-License-Identifier: Apache-2.0
-- ADR-0114: common regional knowledge acquired by an NPC from the pinned canon pack.
-- Separate from campaign events (ADR-0059 item 1: a CANON_CLAIM never becomes a CAMPAIGN_FACT).
-- The summary is snapshotted at acquisition: later pack corrections do not change what the NPC
-- learned (ADR-0059 item 3). Append-only like every other table.

CREATE TABLE npc_canon_knowledge (
    knowledge_id     TEXT PRIMARY KEY,
    idempotency_key  TEXT NOT NULL UNIQUE,
    campaign_id      TEXT NOT NULL REFERENCES campaigns(campaign_id),
    branch_id        TEXT NOT NULL REFERENCES branches(branch_id),
    npc_id           TEXT NOT NULL CHECK (length(npc_id) > 0),
    game_time        INTEGER NOT NULL CHECK (game_time >= 0),
    basis            TEXT NOT NULL CHECK (basis IN ('ORIGIN', 'RESIDENCE', 'INQUIRY')),
    region_id        TEXT NOT NULL CHECK (length(region_id) > 0),
    entry_id         TEXT NOT NULL CHECK (length(entry_id) > 0),
    pack_year_dr     INTEGER NOT NULL,
    pack_revision    TEXT NOT NULL CHECK (length(pack_revision) > 0),
    pin_event_id     TEXT NOT NULL REFERENCES events(event_id),
    trigger_event_id TEXT NOT NULL REFERENCES events(event_id),
    snapshot_json    TEXT NOT NULL,
    recorded_at      TEXT NOT NULL
);
CREATE INDEX npc_canon_knowledge_by_npc ON npc_canon_knowledge (campaign_id, npc_id, game_time);

CREATE TRIGGER npc_canon_knowledge_no_update BEFORE UPDATE ON npc_canon_knowledge BEGIN SELECT RAISE(ABORT, 'append-only: npc_canon_knowledge'); END;
CREATE TRIGGER npc_canon_knowledge_no_delete BEFORE DELETE ON npc_canon_knowledge BEGIN SELECT RAISE(ABORT, 'append-only: npc_canon_knowledge'); END;
