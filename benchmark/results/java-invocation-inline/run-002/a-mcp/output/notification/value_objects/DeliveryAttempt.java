package com.metaengine.demo.notification.value_objects;

import java.time.OffsetDateTime;

// DeliveryAttempt value object.

public class DeliveryAttempt {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public DeliveryAttempt(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
