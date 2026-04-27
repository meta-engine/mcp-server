package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** Dimension value object in the analytics domain. */
public record Dimension(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
