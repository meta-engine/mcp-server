package com.metaengine.demo.ordering.value_objects;

/** ShippingAddress value object. */
public record ShippingAddress(
    String street,
    String city,
    String country,
    String postalCode
) {}
