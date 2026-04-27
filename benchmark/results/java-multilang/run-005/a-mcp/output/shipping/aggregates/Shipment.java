package com.metaengine.demo.shipping.aggregates;

import java.time.OffsetDateTime;

// Shipment aggregate root for the shipping domain.

public class Shipment {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public Shipment(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
