package com.metaengine.demo.inventory.value_objects;

/** Quantity value object — amount with unit of measure. */
public record Quantity(
    double amount,
    String unit
) {}
