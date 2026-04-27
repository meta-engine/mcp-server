package com.metaengine.demo.billing.value_objects;

import java.time.OffsetDateTime;

// InvoiceLine value object.

public class InvoiceLine {
    public String id;
    public OffsetDateTime createdAt;
    public OffsetDateTime updatedAt;
    public String name;
    public String description;

    public InvoiceLine(String id, OffsetDateTime createdAt, OffsetDateTime updatedAt, String name, String description) {
        this.id = id;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.name = name;
        this.description = description;
    }
}
