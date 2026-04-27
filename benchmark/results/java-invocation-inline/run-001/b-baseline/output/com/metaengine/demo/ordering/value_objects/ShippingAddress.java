package com.metaengine.demo.ordering.value_objects;

/** Value object representing the shipping address for an order. */
public record ShippingAddress(String street, String city, String country, String postalCode) {}
