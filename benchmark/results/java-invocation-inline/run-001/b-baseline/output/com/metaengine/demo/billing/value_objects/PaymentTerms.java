package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** Value object describing the payment terms for an invoice. */
public record PaymentTerms(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
