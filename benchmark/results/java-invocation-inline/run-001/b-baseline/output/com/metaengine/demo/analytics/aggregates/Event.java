package com.metaengine.demo.analytics.aggregates;

import java.time.Instant;

/** Aggregate root for the analytics domain. */
public class Event {
    private final String id;
    private final Instant createdAt;
    private final Instant updatedAt;
    private final String name;
    private final String description;

    public Event(String id, Instant createdAt, Instant updatedAt, String name, String description) {
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
