CREATE TABLE IF NOT EXISTS works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT '下書き',
    thumbnail_image_id INTEGER,
    memo TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (thumbnail_image_id) REFERENCES images(id)
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    is_thumbnail INTEGER NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 1,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS work_destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT '未着手',
    posted_at TEXT,
    memo TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    UNIQUE (work_id, destination_id)
);

CREATE TABLE IF NOT EXISTS work_checks (
    work_id INTEGER PRIMARY KEY,
    thumbnail_checked INTEGER NOT NULL DEFAULT 0,
    order_checked INTEGER NOT NULL DEFAULT 0,
    destination_checked INTEGER NOT NULL DEFAULT 0,
    final_checked_at TEXT,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_images_work_id_sort_order
ON images(work_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_works_status
ON works(status);

CREATE INDEX IF NOT EXISTS idx_work_destinations_work_id
ON work_destinations(work_id);

CREATE INDEX IF NOT EXISTS idx_work_destinations_status
ON work_destinations(status);
