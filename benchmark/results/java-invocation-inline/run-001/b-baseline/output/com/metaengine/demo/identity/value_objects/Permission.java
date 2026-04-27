package com.metaengine.demo.identity.value_objects;

import java.time.Instant;

/** Value object representing a granted permission. */
public record Permission(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
