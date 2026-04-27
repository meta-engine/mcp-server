package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** Value object representing an analytics metric. */
public record Metric(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
