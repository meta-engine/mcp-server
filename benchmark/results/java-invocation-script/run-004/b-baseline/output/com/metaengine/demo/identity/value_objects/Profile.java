package com.metaengine.demo.identity.value_objects;

import java.time.Instant;

/** Profile value object in the identity domain. */
public record Profile(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
