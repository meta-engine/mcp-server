package com.metaengine.demo.ordering.aggregates;

import java.time.OffsetDateTime;

// Order aggregate root for the ordering domain.

public class Order {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public Order(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
