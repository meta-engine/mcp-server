package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** Value object representing a metric dimension. */
public record Dimension(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
