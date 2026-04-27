package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** EventPayload value object in the analytics domain. */
public record EventPayload(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
