package com.metaengine.demo.inventory.aggregates;

import java.time.Instant;

/** StockItem aggregate root. */
public class StockItem {
    private final String id;
    private final Instant createdAt;
    private final Instant updatedAt;
    private final String name;
    private final String description;

    public StockItem(String id, Instant createdAt, Instant updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }

    public String getId() { return id; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public String getName() { return name; }
    public String getDescription() { return description; }
}
