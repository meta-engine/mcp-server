package com.metaengine.demo.inventory.value_objects;

import java.time.Instant;

/** Value object representing a stock reservation. */
public record Reservation(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
