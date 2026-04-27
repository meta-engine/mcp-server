package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** Discount value object in the billing domain. */
public record Discount(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
