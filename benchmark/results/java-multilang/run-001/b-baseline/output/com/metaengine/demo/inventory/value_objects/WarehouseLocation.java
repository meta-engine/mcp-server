package com.metaengine.demo.inventory.value_objects;

import java.time.Instant;

/** WarehouseLocation value object for the inventory domain. */
public record WarehouseLocation(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
