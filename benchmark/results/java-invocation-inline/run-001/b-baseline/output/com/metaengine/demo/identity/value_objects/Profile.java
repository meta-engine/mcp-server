package com.metaengine.demo.identity.value_objects;

import java.time.Instant;

/** Value object representing a user profile snapshot. */
public record Profile(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
