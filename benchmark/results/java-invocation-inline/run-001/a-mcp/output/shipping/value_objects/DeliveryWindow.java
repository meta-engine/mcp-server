package com.metaengine.demo.shipping.value_objects;

import java.time.OffsetDateTime;

// DeliveryWindow value object.

public class DeliveryWindow {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public DeliveryWindow(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
