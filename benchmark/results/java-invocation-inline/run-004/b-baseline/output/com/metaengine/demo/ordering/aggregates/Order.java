package com.metaengine.demo.ordering.aggregates;

import java.time.Instant;

/** Order aggregate root. */
public class Order {
    private final String id;
    private final Instant createdAt;
    private final Instant updatedAt;
    private final String name;
    private final String description;

    public Order(String id, Instant createdAt, Instant updatedAt, String name, String description) {
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
