package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** Value object carrying the payload of an analytics event. */
public record EventPayload(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
