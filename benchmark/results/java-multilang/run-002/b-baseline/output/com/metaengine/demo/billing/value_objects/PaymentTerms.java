package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** PaymentTerms value object in the billing domain. */
public record PaymentTerms(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
