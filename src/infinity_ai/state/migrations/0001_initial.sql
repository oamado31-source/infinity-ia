-- SPDX-License-Identifier: Apache-2.0
-- SPEC-003 / ADR-0110: campaign state, append-only event log and NPC memory (single player stage).
-- Every table except schema_migrations is append-only: triggers abort UPDATE and DELETE.

CREATE TABLE campaigns (
    campaign_id    TEXT PRIMARY KEY CHECK (length(campaign_id) > 0),
    root_branch_id TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE branches (
    branch_id        TEXT PRIMARY KEY,
    campaign_id      TEXT NOT NULL REFERENCES campaigns(campaign_id),
    parent_branch_id TEXT REFERENCES branches(branch_id),
    fork_seq         INTEGER,           -- last parent event visible to the child
    fork_game_time   INTEGER,           -- restore point (game ticks)
    fork_epoch       INTEGER,
    lineage          TEXT NOT NULL CHECK (lineage IN ('ROOT', 'INFERRED_FROM_ACTIVE')),
    created_at       TEXT NOT NULL,
    CHECK ((lineage = 'ROOT') = (parent_branch_id IS NULL)),
    CHECK (lineage = 'ROOT' OR (fork_seq IS NOT NULL AND fork_game_time IS NOT NULL))
);

CREATE TABLE events (
    seq                   INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id              TEXT NOT NULL UNIQUE,
    idempotency_key       TEXT NOT NULL UNIQUE,
    campaign_id           TEXT NOT NULL REFERENCES campaigns(campaign_id),
    branch_id             TEXT NOT NULL REFERENCES branches(branch_id),
    host_epoch            INTEGER NOT NULL CHECK (host_epoch >= 0),
    event_type            TEXT NOT NULL CHECK (length(event_type) > 0),
    category              TEXT NOT NULL
                          CHECK (category IN ('CAMPAIGN_OBSERVATION', 'CAMPAIGN_FACT', 'RECONCILIATION')),
    game_time             INTEGER CHECK (game_time IS NULL OR game_time >= 0),
    payload_json          TEXT NOT NULL,
    evidence              TEXT NOT NULL CHECK (evidence IN ('SYNTHETIC', 'LAB_OBSERVED', 'POC_VERIFIED')),
    source_observation_id TEXT,
    recorded_at           TEXT NOT NULL
);
CREATE INDEX events_by_branch ON events (campaign_id, branch_id, seq);

-- NPC memory (ADR-0059): immutable acquisition episodes. SECRET is not persisted in this stage.
CREATE TABLE npc_experiences (
    experience_id    TEXT PRIMARY KEY,
    idempotency_key  TEXT NOT NULL UNIQUE,
    campaign_id      TEXT NOT NULL REFERENCES campaigns(campaign_id),
    branch_id        TEXT NOT NULL REFERENCES branches(branch_id),
    npc_id           TEXT NOT NULL CHECK (length(npc_id) > 0),
    game_time        INTEGER NOT NULL CHECK (game_time >= 0),
    acquisition_mode TEXT NOT NULL CHECK (acquisition_mode IN ('OBSERVED', 'TOLD', 'READ', 'INVESTIGATED')),
    claim_event_id   TEXT NOT NULL REFERENCES events(event_id),
    channel_ref      TEXT NOT NULL CHECK (length(channel_ref) > 0),
    visibility       TEXT NOT NULL CHECK (visibility IN ('PARTY', 'HOST_ONLY')),
    recorded_at      TEXT NOT NULL
);
CREATE INDEX npc_experiences_by_npc ON npc_experiences (campaign_id, npc_id, game_time);

-- Belief state is versioned separately from the episodes that justify it (REQ-MEM-002).
CREATE TABLE belief_revisions (
    revision_id          TEXT PRIMARY KEY,
    belief_id            TEXT NOT NULL,
    previous_revision_id TEXT REFERENCES belief_revisions(revision_id),
    campaign_id          TEXT NOT NULL REFERENCES campaigns(campaign_id),
    branch_id            TEXT NOT NULL REFERENCES branches(branch_id),
    npc_id               TEXT NOT NULL,
    game_time            INTEGER NOT NULL CHECK (game_time >= 0),
    claim_event_id       TEXT NOT NULL REFERENCES events(event_id),
    stance               TEXT NOT NULL
                         CHECK (stance IN ('ACCEPTED', 'DOUBTFUL', 'REJECTED', 'SUSPENDED', 'INVESTIGATING')),
    reason_codes_json    TEXT NOT NULL,
    authored_by          TEXT NOT NULL CHECK (authored_by = 'RULES'),
    recorded_at          TEXT NOT NULL,
    UNIQUE (belief_id, previous_revision_id)
);

CREATE TABLE belief_revision_sources (
    revision_id   TEXT NOT NULL REFERENCES belief_revisions(revision_id),
    experience_id TEXT NOT NULL REFERENCES npc_experiences(experience_id),
    PRIMARY KEY (revision_id, experience_id)
);

CREATE TRIGGER campaigns_no_update BEFORE UPDATE ON campaigns BEGIN SELECT RAISE(ABORT, 'append-only: campaigns'); END;
CREATE TRIGGER campaigns_no_delete BEFORE DELETE ON campaigns BEGIN SELECT RAISE(ABORT, 'append-only: campaigns'); END;
CREATE TRIGGER branches_no_update BEFORE UPDATE ON branches BEGIN SELECT RAISE(ABORT, 'append-only: branches'); END;
CREATE TRIGGER branches_no_delete BEFORE DELETE ON branches BEGIN SELECT RAISE(ABORT, 'append-only: branches'); END;
CREATE TRIGGER events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'append-only: events'); END;
CREATE TRIGGER events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'append-only: events'); END;
CREATE TRIGGER npc_experiences_no_update BEFORE UPDATE ON npc_experiences BEGIN SELECT RAISE(ABORT, 'append-only: npc_experiences'); END;
CREATE TRIGGER npc_experiences_no_delete BEFORE DELETE ON npc_experiences BEGIN SELECT RAISE(ABORT, 'append-only: npc_experiences'); END;
CREATE TRIGGER belief_revisions_no_update BEFORE UPDATE ON belief_revisions BEGIN SELECT RAISE(ABORT, 'append-only: belief_revisions'); END;
CREATE TRIGGER belief_revisions_no_delete BEFORE DELETE ON belief_revisions BEGIN SELECT RAISE(ABORT, 'append-only: belief_revisions'); END;
CREATE TRIGGER belief_revision_sources_no_update BEFORE UPDATE ON belief_revision_sources BEGIN SELECT RAISE(ABORT, 'append-only: belief_revision_sources'); END;
CREATE TRIGGER belief_revision_sources_no_delete BEFORE DELETE ON belief_revision_sources BEGIN SELECT RAISE(ABORT, 'append-only: belief_revision_sources'); END;
