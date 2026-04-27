package com.metaengine.demo.inventory.value_objects;

import java.time.OffsetDateTime;

// WarehouseLocation value object.

public class WarehouseLocation {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public WarehouseLocation(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
