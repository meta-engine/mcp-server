package com.metaengine.demo.analytics.value_objects;

import java.time.OffsetDateTime;

// Dimension value object.

public class Dimension {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public Dimension(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
