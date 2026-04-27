package com.metaengine.demo.catalog.value_objects;

/** Price value object — monetary amount with currency. */
public record Price(
    double amount,
    String currency
) {}
