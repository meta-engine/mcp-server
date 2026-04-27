package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Template value object for the notification domain. */
public record Template(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
