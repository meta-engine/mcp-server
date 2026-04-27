package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** TaxLine value object. */
public record TaxLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
