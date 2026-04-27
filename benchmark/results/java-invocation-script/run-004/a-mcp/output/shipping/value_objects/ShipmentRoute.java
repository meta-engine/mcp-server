package com.metaengine.demo.shipping.value_objects;

import java.time.OffsetDateTime;

// ShipmentRoute value object.

public class ShipmentRoute {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public ShipmentRoute(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
