package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Recipient value object in the notification domain. */
public record Recipient(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
