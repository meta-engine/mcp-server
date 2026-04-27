package com.metaengine.demo.shipping.value_objects;

import java.time.Instant;

/** Value object representing a shipment route. */
public record ShipmentRoute(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
