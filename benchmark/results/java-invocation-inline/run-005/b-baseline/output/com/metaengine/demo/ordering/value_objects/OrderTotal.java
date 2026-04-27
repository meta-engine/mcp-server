package com.metaengine.demo.ordering.value_objects;

/** OrderTotal value object representing a monetary amount in a currency. */
public record OrderTotal(
    double amount,
    String currency
) {}
