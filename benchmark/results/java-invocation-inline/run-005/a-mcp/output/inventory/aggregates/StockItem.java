package com.metaengine.demo.inventory.aggregates;

import java.time.OffsetDateTime;

// StockItem aggregate root for the inventory domain.

public class StockItem {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public StockItem(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
