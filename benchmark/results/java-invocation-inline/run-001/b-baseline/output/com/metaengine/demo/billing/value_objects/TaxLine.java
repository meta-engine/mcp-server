package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** Value object representing a tax line on an invoice. */
public record TaxLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
