package com.metaengine.demo.ordering.value_objects;

/** Value object representing the billing address for an order. */
public record BillingAddress(String street, String city, String country, String postalCode) {}
