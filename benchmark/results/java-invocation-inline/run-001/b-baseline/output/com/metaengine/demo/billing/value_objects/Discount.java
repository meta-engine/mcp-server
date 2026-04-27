package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** Value object representing a discount applied to an invoice. */
public record Discount(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
