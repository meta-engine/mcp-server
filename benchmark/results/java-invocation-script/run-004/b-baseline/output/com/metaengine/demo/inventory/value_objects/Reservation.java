package com.metaengine.demo.inventory.value_objects;

import java.time.Instant;

/** Reservation value object in the inventory domain. */
public record Reservation(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
