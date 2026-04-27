package com.metaengine.demo.ordering.value_objects;

/** ShippingAddress value object for the ordering domain. */
public record ShippingAddress(
        String street,
        String city,
        String country,
        String postalCode) {
}
