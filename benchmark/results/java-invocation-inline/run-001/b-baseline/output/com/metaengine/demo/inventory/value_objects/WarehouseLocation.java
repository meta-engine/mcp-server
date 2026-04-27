package com.metaengine.demo.inventory.value_objects;

import java.time.Instant;

/** Value object representing a warehouse location. */
public record WarehouseLocation(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
