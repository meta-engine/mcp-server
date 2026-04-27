package com.metaengine.demo.ordering.value_objects;

/** BillingAddress value object in the ordering domain. */
public record BillingAddress(String street, String city, String country, String postalCode) {
}
